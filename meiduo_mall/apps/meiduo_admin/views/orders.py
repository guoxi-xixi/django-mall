from rest_framework.response import Response

from apps.orders.models import OrderInfo, OrderGoods
from apps.meiduo_admin.serializers.orders import OrderModelSerializer, OrderGoodsModelSerializer
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from apps.meiduo_admin.utils import PageNum
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser


class OrderModelViewSet(ModelViewSet):

    # queryset = OrderInfo.objects.all()
    def get_queryset(self):
        keyword = self.request.query_params.get('keyword')

        if keyword:
            return OrderInfo.objects.filter(order_id__contains=keyword)
        return OrderInfo.objects.all()

    serializer_class = OrderModelSerializer

    pagination_class = PageNum

    permission_classes = [IsAdminUser]

    # 在视图中定义status方法修改订单状态
    @action(methods=['PUT'], detail=True)   # detail 追加路由
    def status(self, request, pk):
        """
        修改订单状态
        @param request:
        @param pk:
        @return:
        """
        # 查询修改订单
        try:
            order = OrderInfo.objects.get(order_id=pk)
        except Exception as e:
            return Response({'error': '获取订单数据失败'})
        else:
            # 修改订单状态
            status = self.request.data.get('status')

            if not status:
                return Response({'error': '缺失订单状态'})
            order.status = status
            order.save()

        return Response({
            'order_id': pk,
            'status': status
        })



