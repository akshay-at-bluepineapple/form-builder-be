from django.db import models
from django.db.models import JSONField


class Form(models.Model):
    submit_api_route = models.URLField()
    form_name = models.CharField(max_length=255)

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
    row_name = models.CharField(max_length=255)
    row_order = models.IntegerField(default=None)

    def __str__(self):
        return f"Row: {self.row_name}"


class Column(models.Model):
    row = models.ForeignKey(Row, related_name="columns", on_delete=models.CASCADE)
    column_name = models.CharField(max_length=255)
    column_order = models.IntegerField(
        default=None, help_text="Column order in the row (1-2)"
    )

    def __str__(self):
        return f"Column: {self.row_name}"


class Field(models.Model):
    column = models.ForeignKey(Column, related_name="fields", on_delete=models.CASCADE)
    config = JSONField()

    def __str__(self):
        return f"Field in column {self.column.column_order} of Row {self.column.row.row_name}"
