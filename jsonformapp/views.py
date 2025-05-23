from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from .models import Form
from .serializers import FormSerializer, FormCreateUpdateSerializer
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class FormListAPIView(ListAPIView):
    queryset = Form.objects.all()
    serializer_class = FormSerializer


class FormListCreateUpdateView(APIView):
    @swagger_auto_schema(request_body=FormCreateUpdateSerializer)
    def post(self, request):
        serializer = FormCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
