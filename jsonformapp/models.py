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


from django.db import models


class Product(models.Model):
    CURRENCY_CHOICES = [
        ("INR", "Indian Rupee"),
        ("USD", "US Dollar"),
        ("EUR", "Euro"),
    ]

    FAMILY_CHOICES = [
        ("AUTO", "Auto Insurance"),
        ("HEALTH", "Health Insurance"),
        ("TRAVEL", "Travel Insurance"),
    ]

    admin_fee = models.DecimalField(max_digits=16, decimal_places=2)
    agency_commission = models.DecimalField(max_digits=5, decimal_places=2)
    bank_account = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)
    product_name = models.CharField(max_length=80)
    product_code = models.CharField(max_length=5)
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES)
    product_family = models.CharField(max_length=50, choices=FAMILY_CHOICES)

    assurance_charge = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, null=True
    )
    bank_branch = models.CharField(max_length=255, blank=True, null=True)
    bsb = models.CharField(max_length=255, blank=True, null=True)
    cancellation_fee = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True
    )
    is_active = models.BooleanField(default=True)
    is_annual = models.BooleanField(default=False)
    parameters = models.TextField(blank=True, null=True)
    platform_fee = models.DecimalField(
        max_digits=16, decimal_places=2, blank=True, null=True
    )
    section_definition = models.TextField(blank=True, null=True)
    wording_url = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.product_name


from django.db import models


class Wording(models.Model):
    CURRENCY_CHOICES = [
        ("USD", "USD"),
        ("EUR", "EUR"),
        ("INR", "INR"),
        ("GBP", "GBP"),
    ]

    active = models.BooleanField(default=False)
    created_by = models.CharField(max_length=100, blank=True, null=True)
    currency = models.CharField(
        max_length=10, choices=CURRENCY_CHOICES, blank=True, null=True
    )
    default = models.BooleanField(default=False)
    expiry_date = models.DateField(blank=True, null=True)
    external_id = models.CharField(max_length=50, unique=True)
    last_modified_by = models.CharField(max_length=100, blank=True, null=True)
    owner = models.CharField(max_length=100, blank=True, null=True)
    product = models.CharField(max_length=100, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    wording_full_name = models.TextField(max_length=255, blank=True, null=True)
    wording_name = models.CharField(max_length=80)
    wording_url = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.wording_name
