from django.urls import path
from .views import (
    FormListAPIView,
    FormListCreateView,
    FormListUpdateView,
    GetTablesAPIView,
    GetFieldsAPIView,
    FormSoftDeleteView,
    DynamicTableRecordView,
    GetEmptyTablesAPIView,
    GetTableDataAPIView,
)

urlpatterns = [
    path("tables/", GetTablesAPIView.as_view(), name="get-tables"),
    path(
        "tables/<str:table_name>/fields/", GetFieldsAPIView.as_view(), name="get-fields"
    ),
    path("form/", FormListAPIView.as_view(), name="form-list"),
    path("form/create/", FormListCreateView.as_view(), name="form-create"),
    path(
        "form/create-update/<int:form_id>/",
        FormListUpdateView.as_view(),
        name="form-create-update",
    ),
    path(
        "form/soft-delete/<int:form_id>/",
        FormSoftDeleteView.as_view(),
        name="form-soft-delete",
    ),
    path(
        "form/field-values-submission/",
        DynamicTableRecordView.as_view(),
        name="form-field-values-submission",
    ),
    path("tables/empty/", GetEmptyTablesAPIView.as_view(), name="get-empty-tables"),
    path(
        "tables/<str:table_name>/data/",
        GetTableDataAPIView.as_view(),
        name="get-table-data",
    ),
]
