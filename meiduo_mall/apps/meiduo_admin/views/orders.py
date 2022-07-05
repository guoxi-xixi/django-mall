from apps.orders.models import OrderInfo, OrderGoods
from apps.meiduo_admin.serializers.orders import OrderModelSerializer, OrderGoodsModelSerializer
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.viewsets import ModelViewSet
from apps.meiduo_admin.utils import PageNum


class OrderListAPIView(ListAPIView):

    # queryset = OrderInfo.objects.all()
    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')

        if keyword:
            return OrderInfo.objects.filter(order_id__contains=keyword)
        return OrderInfo.objects.all()

    serializer_class = OrderModelSerializer

    pagination_class = PageNum


class OrderModelViewSet(ModelViewSet):

    # queryset = OrderInfo.objects.all()
    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')

        if keyword:
            return OrderInfo.objects.filter(order_id__contains=keyword)
        return OrderInfo.objects.all()

    serializer_class = OrderModelSerializer

    pagination_class = PageNum


# class OrderGoodsRetrieveUpdateAPIView(RetrieveUpdateAPIView):
#
#     # queryset = OrderGoods.objects.get()
#     def get_queryset(self):
#         order_id = self.request.query_params.get('pk')
#         return OrderGoods.objects.filter(order_id=order_id)
#
#     serializer_class = OrderModelSerializer
