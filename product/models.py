from django.db import models


class Product(models.Model):
    CURRENCY_CHOICES = [
        ("INR", "Indian Rupee"),
        ("USD", "US Dollar"),
    ]

    FAMILY_CHOICES = [
        ("Health", "Health"),
        ("Travel", "Travel"),
        ("Life", "Life"),
        ("Motor", "Motor"),
    ]

    product_name = models.CharField(max_length=80)
    product_code = models.CharField(max_length=5, unique=True)
    currency = models.CharField(max_length=50, choices=CURRENCY_CHOICES)
    is_active = models.BooleanField(default=True)
    is_annual = models.BooleanField(default=False)
    platform_fee = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )
    admin_fee = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )
    agency_commission = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    assurance_charge = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )
    cancellation_fee = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    bank_name = models.CharField(max_length=255, null=True, blank=True)
    bank_branch = models.CharField(max_length=255, null=True, blank=True)
    bank_account = models.CharField(max_length=255, null=True, blank=True)
    bsb = models.CharField(max_length=255, null=True, blank=True)
    parameters = models.TextField(blank=True, null=True)
    product_family = models.CharField(
        max_length=100, choices=FAMILY_CHOICES, null=True, blank=True
    )
    section_definition = models.TextField(blank=True, null=True)
    wording_url = models.URLField(max_length=255, blank=True)

    def __str__(self):
        return self.product_name
