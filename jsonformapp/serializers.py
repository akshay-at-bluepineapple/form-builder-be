from rest_framework import serializers
from .models import Form, Section, Row, Column, Field


class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = "__all__"


class ColumnSerializer(serializers.ModelSerializer):
    fields = FieldSerializer(many=True, read_only=True)

    class Meta:
        model = Column
        fields = "__all__"


class RowSerializer(serializers.ModelSerializer):
    columns = ColumnSerializer(many=True, read_only=True)

    class Meta:
        model = Row
        fields = "__all__"


class SectionSerializer(serializers.ModelSerializer):
    rows = RowSerializer(many=True, read_only=True)

    class Meta:
        model = Section
        fields = "__all__"


class FormSerializer(serializers.ModelSerializer):
    sections = SectionSerializer(many=True, read_only=True)

    class Meta:
        model = Form
        fields = "__all__"


class FieldCreateUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    column = serializers.PrimaryKeyRelatedField(
        queryset=Column.objects.all(), required=False
    )

    class Meta:
        model = Field
        fields = "__all__"

    def create(self, validated_data):
        column = self.context.get("column")
        if not column:
            raise serializers.ValidationError(
                "Column context is required to create Field."
            )
        return Field.objects.create(column=column, **validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ColumnsCreateUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    row = serializers.PrimaryKeyRelatedField(queryset=Row.objects.all(), required=False)
    fields = FieldCreateUpdateSerializer(many=True)

    class Meta:
        model = Column
        fields = "__all__"

    def create(self, validated_data):
        fields_data = validated_data.pop("fields", [])
        row = self.context.get("row")
        column = Column.objects.create(row=row, **validated_data)
        for field_data in fields_data:
            serializer = FieldCreateUpdateSerializer(
                data=field_data, context={"column": column}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return column

    def update(self, instance, validated_data):
        fields_data = validated_data.pop("fields", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update fields
        existing_ids = {f.id for f in instance.fields.all()}
        payload_ids = {f.get("id") for f in fields_data if f.get("id")}
        Field.objects.filter(id__in=(existing_ids - payload_ids)).delete()

        for field_data in fields_data:
            field_id = field_data.get("id")
            if field_id:
                field_instance = Field.objects.filter(
                    id=field_id, column=instance
                ).first()
                if field_instance:
                    serializer = FieldCreateUpdateSerializer(
                        field_instance, data=field_data, context={"column": instance}
                    )
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                else:
                    raise serializers.ValidationError(f"Field ID {field_id} not found.")
            else:
                serializer = FieldCreateUpdateSerializer(
                    data=field_data, context={"column": instance}
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()

        return instance


class RowCreateUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    section = serializers.PrimaryKeyRelatedField(
        queryset=Section.objects.all(), required=False
    )
    columns = ColumnsCreateUpdateSerializer(many=True)

    class Meta:
        model = Row
        fields = "__all__"

    def create(self, validated_data):
        columns_data = validated_data.pop("columns", [])
        section = self.context.get("section")
        row = Row.objects.create(section=section, **validated_data)
        for column_data in columns_data:
            serializer = ColumnsCreateUpdateSerializer(
                data=column_data, context={"row": row}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return row

    def update(self, instance, validated_data):
        columns_data = validated_data.pop("columns", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update columns
        existing_ids = {c.id for c in instance.columns.all()}
        payload_ids = {c.get("id") for c in columns_data if c.get("id")}
        Column.objects.filter(id__in=(existing_ids - payload_ids)).delete()

        for column_data in columns_data:
            column_id = column_data.get("id")
            if column_id:
                column_instance = Column.objects.filter(
                    id=column_id, row=instance
                ).first()
                if column_instance:
                    serializer = ColumnsCreateUpdateSerializer(
                        column_instance, data=column_data, context={"row": instance}
                    )
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                else:
                    raise serializers.ValidationError(
                        f"Column ID {column_id} not found."
                    )
            else:
                serializer = ColumnsCreateUpdateSerializer(
                    data=column_data, context={"row": instance}
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()

        return instance


class SectionCreateUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    form = serializers.PrimaryKeyRelatedField(
        queryset=Form.objects.all(), required=False
    )
    rows = RowCreateUpdateSerializer(many=True)

    class Meta:
        model = Section
        fields = "__all__"

    def create(self, validated_data):
        rows_data = validated_data.pop("rows", [])
        form = self.context.get("form")
        section = Section.objects.create(form=form, **validated_data)
        for row_data in rows_data:
            serializer = RowCreateUpdateSerializer(
                data=row_data, context={"section": section}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return section

    def update(self, instance, validated_data):
        rows_data = validated_data.pop("rows", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update rows
        existing_ids = {r.id for r in instance.rows.all()}
        payload_ids = {r.get("id") for r in rows_data if r.get("id")}
        Row.objects.filter(id__in=(existing_ids - payload_ids)).delete()

        for row_data in rows_data:
            row_id = row_data.get("id")
            if row_id:
                row_instance = Row.objects.filter(id=row_id, section=instance).first()
                if row_instance:
                    serializer = RowCreateUpdateSerializer(
                        row_instance, data=row_data, context={"section": instance}
                    )
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                else:
                    raise serializers.ValidationError(f"Row ID {row_id} not found.")
            else:
                serializer = RowCreateUpdateSerializer(
                    data=row_data, context={"section": instance}
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()

        return instance


class FormCreateSerializer(serializers.ModelSerializer):
    sections = SectionCreateUpdateSerializer(many=True)

    class Meta:
        model = Form
        fields = "__all__"

    def create(self, validated_data):
        section_data = validated_data.pop("sections", [])
        form = Form.objects.create(**validated_data)
        for section in section_data:
            serializer = SectionCreateUpdateSerializer(
                data=section, context={"form": form}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return form


class FormUpdateSerializer(serializers.ModelSerializer):
    sections = SectionCreateUpdateSerializer(many=True)

    class Meta:
        model = Form
        fields = "__all__"

    def update(self, instance, validated_data):
        sections_data = validated_data.pop("sections", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update sections
        existing_ids = {s.id for s in instance.sections.all()}
        payload_ids = {s.get("id") for s in sections_data if s.get("id")}
        Section.objects.filter(id__in=(existing_ids - payload_ids)).delete()

        for section_data in sections_data:
            section_id = section_data.get("id")
            if section_id:
                section_instance = Section.objects.filter(
                    id=section_id, form=instance
                ).first()
                if section_instance:
                    serializer = SectionCreateUpdateSerializer(
                        section_instance, data=section_data, context={"form": instance}
                    )
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                else:
                    raise serializers.ValidationError(
                        f"Section ID {section_id} not found."
                    )
            else:
                serializer = SectionCreateUpdateSerializer(
                    data=section_data, context={"form": instance}
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()

        return instance
