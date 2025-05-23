from django.urls import path
from .views import FormListAPIView, FormListCreateUpdateView

urlpatterns = [
    path("forms/", FormListAPIView.as_view(), name="form-list"),
    path("form/create/", FormListCreateUpdateView.as_view(), name="form-create"),
]
