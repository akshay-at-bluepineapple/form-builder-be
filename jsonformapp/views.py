from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from .models import Form
from .serializers import FormSerializer, FormCreateUpdateSerializer
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import connection


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
        return Response({"tables": tables}, status=status.HTTP_200_OK)


class GetFieldsAPIView(APIView):
    @swagger_auto_schema(
        operation_description="Fetch all fields from a specific table in the database",
        responses={
            200: openapi.Response(
                description="A list of fields in the specified table",
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
                    {"name": field[0], "type": field[1]} for field in cursor.fetchall()
                ]

            return Response({"fields": fields}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Error fetching fields for table {table_name}: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class FormListAPIView(ListAPIView):
    queryset = Form.objects.all()
    serializer_class = FormSerializer


class FormListCreateUpdateView(APIView):
    @swagger_auto_schema(request_body=FormCreateUpdateSerializer)
    def post(self, request):
        serializer = FormCreateUpdateSerializer(data=request.data)
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
    def delete(self,request, form_id, *args, **kwargs):
        if not form_id:
            return Response({"error": "Form ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            form = Form.objects.get(id = form_id)
            form.is_deleted = True
            form.save()
            return Response({"message": "Form soft-deleted successfully."}, status=status.HTTP_200_OK)
        except Form.DoesNotExist:
            return Response({"error": "Form not found."}, status=status.HTTP_404_NOT_FOUND)

