from django.db import models


class Wording(models.Model):
    CURRENCY_CHOICES = [
        ("USD", "USD"),
        ("EUR", "EUR"),
        ("INR", "INR"),
        ("GBP", "GBP"),
    ]

    PRODUCT_CHOICES = [
        ("ProductA", "Product A"),
        ("ProductB", "Product B"),
        ("ProductC", "Product C"),
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
    product = models.CharField(max_length=100, choices=PRODUCT_CHOICES)
    start_date = models.DateField()
    wording_full_name = models.TextField(max_length=255, blank=True, null=True)
    wording_name = models.CharField(max_length=80)
    wording_url = models.URLField(max_length=255, blank=True)

    def __str__(self):
        return self.wording_name
