from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from .models import Form
from .serializers import FormSerializer, FormCreateSerializer, FormUpdateSerializer
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import connection
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist, FieldError


class GetTablesAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Fetch all tables from the database",
        responses={
            200: openapi.Response(
                description="A list of tables in the database",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "tables": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING),
                        )
                    },
                ),
            )
        },
    )
    def get(self, request, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]

        excluded_prefixes = [
            "django_",
            "auth_",
            "admin_",
            "contenttypes",
            "sessions",
            "jsonformapp_",
        ]

        filtered_tables = [
            table
            for table in tables
            if not any(table.startswith(prefix) for prefix in excluded_prefixes)
        ]

        return Response({"tables": filtered_tables}, status=status.HTTP_200_OK)


class GetFieldsAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Fetch all fields and metadata from a specific table in the database",
        responses={
            200: openapi.Response(
                description="A list of fields and metadata in the specified table",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "fields": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "name": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description="Name of the field",
                                    ),
                                    "type": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description="Data type of the field",
                                    ),
                                    "nullable": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description="Is field nullable ('YES'/'NO')",
                                    ),
                                    "key": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description="Key type ('PRI', 'MUL', '')",
                                    ),
                                    "default": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        nullable=True,
                                        description="Default value",
                                    ),
                                    "extra": openapi.Schema(
                                        type=openapi.TYPE_STRING,
                                        description="Extra information",
                                    ),
                                },
                            ),
                        )
                    },
                ),
            )
        },
    )
    def get(self, request, table_name, *args, **kwargs):
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"DESCRIBE {table_name}")
                fields = [
                    {
                        "name": field[0],
                        "type": field[1],
                        "required": field[2],
                        "key": field[3],
                        "default": field[4],
                    }
                    for field in cursor.fetchall()
                ]

            return Response({"fields": fields}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Error fetching fields for table {table_name}: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class FormListAPIView(ListAPIView):
    queryset = Form.objects.filter(is_deleted=False)
    serializer_class = FormSerializer


class FormListCreateView(APIView):
    @swagger_auto_schema(request_body=FormCreateSerializer)
    def post(self, request):
        serializer = FormCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FormListUpdateView(APIView):
    @swagger_auto_schema(request_body=FormUpdateSerializer)
    def put(self, request, form_id):
        try:
            form_instance = Form.objects.get(pk=form_id)
            print("form instance", form_instance)
        except Form.DoesNotExist:
            return Response(
                {"error": "Form not found"}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = FormUpdateSerializer(form_instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FormSoftDeleteView(APIView):
    @swagger_auto_schema(
        operation_description="Delete Form from db",
        responses={
            200: openapi.Response(
                description="A Form got deleted.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                ),
            )
        },
    )
    def delete(self, request, form_id, *args, **kwargs):
        if not form_id:
            return Response(
                {"error": "Form ID is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            form = Form.objects.get(id=form_id)
            form.is_deleted = True
            form.save()
            return Response(
                {"message": "Form soft-deleted successfully."},
                status=status.HTTP_200_OK,
            )
        except Form.DoesNotExist:
            return Response(
                {"error": "Form not found."}, status=status.HTTP_404_NOT_FOUND
            )


class DynamicTableRecordView(APIView):
    """
    Dynamically creates or updates data in any table by table_name and fields.
    """

    @swagger_auto_schema(
        operation_description="Create or update record in a dynamic table",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "table_name": openapi.Schema(type=openapi.TYPE_STRING),
                "field_values": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    additional_properties=openapi.Schema(type=openapi.TYPE_STRING),
                ),
            },
            required=["table_name", "field_values"],
        ),
        responses={
            201: "Created",
            200: "Updated",
            400: "Bad Request",
            404: "Not Found",
        },
    )
    def post(self, request):
        table_name = request.data.get("table_name")
        field_values = request.data.get("field_values")

        if not table_name or not field_values:
            return Response(
                {"error": "Both 'table_name' and 'field_values' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            app_label, model_name = table_name.split("_")
            model = apps.get_model(app_label, model_name)
        except Exception:
            return Response(
                {"error": "Invalid table name."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            instance = model.objects.create(**field_values)
            return Response(
                {"message": "Record created successfully.", "id": instance.id},
                status=status.HTTP_201_CREATED,
            )
        except FieldError as fe:
            return Response({"error": str(fe)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request):
        table_name = request.data.get("table_name")
        field_values = request.data.get("field_values")

        if not table_name or not field_values or "id" not in field_values:
            return Response(
                {"error": "Missing 'table_name', 'field_values', or 'id'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            app_label, model_name = table_name.split("_")
            model = apps.get_model(app_label, model_name)
        except Exception:
            return Response(
                {"error": "Invalid table name."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            instance = model.objects.get(id=field_values["id"])
            for field, value in field_values.items():
                if field != "id":
                    setattr(instance, field, value)
            instance.save()
            return Response(
                {"message": "Record updated successfully."}, status=status.HTTP_200_OK
            )
        except ObjectDoesNotExist:
            return Response(
                {"error": "Record not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except FieldError as fe:
            return Response({"error": str(fe)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetEmptyTablesAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Fetch all tables in the database that have no records",
        responses={
            200: openapi.Response(
                description="A list of empty tables in the database",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "empty_tables": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING),
                        )
                    },
                ),
            )
        },
    )
    def get(self, request, *args, **kwargs):
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]

        # Exclude system tables
        excluded_prefixes = [
            "django_",
            "auth_",
            "admin_",
            "contenttypes",
            "sessions",
            "jsonformapp_",
        ]

        # Fetch table_names from jsonformapp_form
        excluded_form_tables = []
        with connection.cursor() as cursor:
            try:
                cursor.execute("SELECT table_name FROM jsonformapp_form")
                excluded_form_tables = [row[0] for row in cursor.fetchall()]
            except Exception as e:
                # Table might not exist yet, skip
                pass

        # Filter user-defined tables
        user_tables = [
            table
            for table in tables
            if not any(table.startswith(prefix) for prefix in excluded_prefixes)
            and table not in excluded_form_tables
        ]

        # Find empty tables
        empty_tables = []
        with connection.cursor() as cursor:
            for table in user_tables:
                try:
                    cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
                    count = cursor.fetchone()[0]
                    if count == 0:
                        empty_tables.append(table)
                except Exception as e:
                    continue

        return Response({"tables": empty_tables}, status=status.HTTP_200_OK)


class GetTableDataAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Fetch all data from a specific table",
        manual_parameters=[
            openapi.Parameter(
                "table_name",
                openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                description="Name of the table to fetch data from",
            )
        ],
        responses={
            200: openapi.Response(description="Success"),
            400: openapi.Response(description="Invalid table name or query error"),
        },
    )
    def get(self, request, table_name):
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {table_name}")
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            return Response({"data": data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Error fetching data from {table_name}: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
