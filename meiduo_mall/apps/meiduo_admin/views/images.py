from rest_framework.viewsets import ModelViewSet
from apps.goods.models import SKUImage, SKU
from apps.meiduo_admin.serializers.images import SKUImageModelSerializer, SKUModelSerializer
from apps.meiduo_admin.utils import PageNum

from rest_framework.generics import ListAPIView

class ImageModelViewSet(ModelViewSet):

    queryset = SKUImage.objects.all()

    serializer_class = SKUImageModelSerializer

    pagination_class = PageNum



class ImageSKUListAPIView(ListAPIView):

    queryset = SKU.objects.all()

    serializer_class = SKUModelSerializer
