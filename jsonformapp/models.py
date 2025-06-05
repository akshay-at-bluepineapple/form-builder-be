from django.db import models
from django.db.models import JSONField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class Form(models.Model):
    submit_api_route = models.URLField()
    form_name = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)
    table_name = models.CharField(max_length=255, default="")

    def __str__(self):
        return f"Form to {self.submit_api_route}"


class Section(models.Model):
    form = models.ForeignKey(Form, related_name="sections", on_delete=models.CASCADE)
    section_name = models.CharField(max_length=255)
    is_collapsable = models.BooleanField(default=False)
    section_order = models.IntegerField(default=None)

    def __str__(self):
        return f"Section: {self.section_name}"


class Row(models.Model):
    section = models.ForeignKey(Section, related_name="rows", on_delete=models.CASCADE)
    row_name = models.CharField(max_length=255, blank=True)
    row_order = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(3)],
        default=1,
        help_text="Column order in the row (1 to 3)",
    )

    def __str__(self):
        return f"Row: {self.row_name}"


class Column(models.Model):
    row = models.ForeignKey(Row, related_name="columns", on_delete=models.CASCADE)
    column_name = models.CharField(max_length=255, blank=True)
    column_order = models.IntegerField(
        default=None, help_text="Column order in the row (1-2)"
    )

    def __str__(self):
        return f"Column: {self.row_name}"

    def clean(self):
        if self.column_order < 1 or self.column_order > 3:
            raise ValidationError("column_order must be between 1 and 3.")


class Field(models.Model):
    column = models.ForeignKey(Column, related_name="fields", on_delete=models.CASCADE)
    db_column_name = models.CharField(max_length=255, default="")
    data_type = models.CharField(max_length=255, null=True)
    is_Required = models.BooleanField(default=False)
    max_length = models.IntegerField(null=True, blank=True)
    config = JSONField()

    def __str__(self):
        return f"Field in column {self.column.column_order} of Row {self.column.row.row_name}"
