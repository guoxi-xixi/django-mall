from rest_framework import serializers
from apps.goods.models import SKUImage, SKU

class SKUImageModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKUImage
        fields = '__all__'

    # 重写更新方法保存image_id
    def update(self, instance, validated_data):
        """
        1. 创建Fdfs客户端
        2. 上传图片
        3. 根据上传结果进行判断,获取新图片的file_id
        4. 更新 模型的 image数据
        """
        # 0.单独接收二进制图片
        image_data = validated_data.get('image').read()

        # 1. 创建fdfs客户端
        from fdfs_client.client import Fdfs_client
        fdfs_client = Fdfs_client('utils/fastdfs/client.conf')
        # 2. 上传图片
        result = fdfs_client.upload_by_buffer(image_data)
        # 3. 根据上传结果进行判断，获取新图片的file_id
        if result['Status'] != 'Upload successed.':
            raise serializers.ValidationError('上传失败,请稍后再试')

        file_id = result.get('Remote file_id')
        # 4. 更新 模型的 image数据
        # 更新sku
        instance.sku_id = validated_data.get('sku')
        instance.image = file_id
        instance.save()

        return instance



class SKUModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = '__all__'

