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


# create serializer
class FieldCreateUpdateSerializer(serializers.ModelSerializer):
    column = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Field
        fields = "__all__"


class ColumnsCeateUpdateSerializer(serializers.ModelSerializer):
    row = serializers.PrimaryKeyRelatedField(read_only=True)
    fields = FieldCreateUpdateSerializer(many=True)

    class Meta:
        model = Column
        fields = "__all__"

    def create(self, validated_data):
        fields_data = validated_data.pop("fields")
        column = Column.objects.create(**validated_data)
        for fields_data in fields_data:
            Field.objects.create(column=column, **fields_data)
        return column


class RowCreateUpdateSerializer(serializers.ModelSerializer):
    section = serializers.PrimaryKeyRelatedField(read_only=True)
    columns = ColumnsCeateUpdateSerializer(many=True)

    class Meta:
        model = Row
        fields = "__all__"

    def create(self, validated_data):
        column_date = validated_data.pop("columns")
        row = Row.objects.create(**validated_data)
        for column_date in column_date:
            ColumnsCeateUpdateSerializer().create({**column_date, "row": row})
        return row


class SectionCreateUpdateSerializer(serializers.ModelSerializer):
    form = serializers.PrimaryKeyRelatedField(read_only=True)
    rows = RowCreateUpdateSerializer(many=True)

    class Meta:
        model = Section
        fields = "__all__"

    def create(self, validated_data):
        row_data = validated_data.pop("rows")
        section = Section.objects.create(**validated_data)
        for row_data in row_data:
            RowCreateUpdateSerializer().create({**row_data, "section": section})
        return section


class FormCreateUpdateSerializer(serializers.ModelSerializer):
    sections = SectionCreateUpdateSerializer(many=True)

    class Meta:
        model = Form
        fields = "__all__"

    def create(self, validated_data):
        section_data = validated_data.pop("sections")
        form = Form.objects.create(**validated_data)
        for section_data in section_data:
            SectionCreateUpdateSerializer().create({**section_data, "form": form})
        return form
