from rest_framework.viewsets import ModelViewSet
from apps.goods.models import SKUImage, SKU
from apps.meiduo_admin.serializers.images import SKUImageModelSerializer, SKUModelSerializer
from apps.meiduo_admin.utils import PageNum

from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status

class ImageModelViewSet(ModelViewSet):

    queryset = SKUImage.objects.all()

    serializer_class = SKUImageModelSerializer

    pagination_class = PageNum

    def create(self, request, *args, **kwargs):
        """
        @param request:
        @param args:
        @param kwargs:
        @return:
        """

        # 0.单独接收二进制图片
        image = request.data.get('image')
        # read() 方法来读取二进制图片流
        image_data = image.read()

        # 1.接收数据
        sku_id = request.data.get('sku')
        # 2.验证数据
        try:
            SKU.objects.get(pk=sku_id)
        except SKU.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 3.保存数据(保存 file_id 和sku_id)
        #  3.1 创建 Fdfs的客户端
        from fdfs_client.client import Fdfs_client
        fdfs_clinet = Fdfs_client('utils/fastdfs/client.conf')
        #  3.2 上传图片
        # 我们上传图片的二进制流 因为客户端提交图片的时候 上传的图片是二进制流
        result = fdfs_clinet.upload_by_buffer(image_data)
        """
        {
            'Remote file_id': 'group1/M00/00/00/wKjlhFsTgJ2AJvG_AAAyZgOTZN0850.jpg', 
            'Uploaded size': '12.00KB',
            'Local file name': '/home/python/Desktop/images/0.jpg',
            'Storage IP': '192.168.229.132',
            'Group name': 'group1', 
            'Status': 'Upload successed.'
        }
        """
        #  3.3 根据上传的结果 获取file_id
        if result['Status'] != 'Upload successed.':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        file_id = result.get('Remote file_id')
        #  3.4 保存SKUImage
        save_image = SKUImage.objects.create(
            sku_id=sku_id,
            image=file_id
        )

        # 4.返回响应
        return Response({
            'id': save_image.id,
            'sku': sku_id,
            'image': save_image.image.url
        }, status=status.HTTP_201_CREATED)




class ImageSKUListAPIView(ListAPIView):

    queryset = SKU.objects.all()

    serializer_class = SKUModelSerializer
