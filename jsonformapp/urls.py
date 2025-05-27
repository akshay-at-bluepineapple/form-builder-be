from django.urls import path
from .views import (
    FormListAPIView,
    FormListCreateUpdateView,
    GetTablesAPIView,
    GetFieldsAPIView,
    FormSoftDeleteView,
)

urlpatterns = [
    path("tables/", GetTablesAPIView.as_view(), name="get-tables"),
    path(
        "tables/<str:table_name>/fields/", GetFieldsAPIView.as_view(), name="get-fields"
    ),
    path("form/", FormListAPIView.as_view(), name="form-list"),
    path("form/create/", FormListCreateUpdateView.as_view(), name="form-create"),
    path("form/soft-delete/<int:form_id>/",FormSoftDeleteView.as_view(), name="form-soft-delete"),
]
