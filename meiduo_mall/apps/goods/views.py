"""
关于模型的分析
1. 根据页面效果 尽量多的分析字段
2. 去分析是保存在一个表中 还是多个表中 （多举例说明）

分析表的关系的时候 最多不要超过3个表

多对多（一般是 3个表）

学生 和 老师

学生表
stu_id      stu_name

100             张三
200             李四

老师表
teacher_id  teacher_name
666             牛老师
999             齐老师


第三张表

stu_id      teacher_id
100             666
100             999
200             666
200             999

商品day01    模型的分析 --》  Fdfs(用于保存图片，视频等文件) --》 为了部署Fdfs学习Docker
"""

######################### 上传图片的代码 ################################
# from fdfs_client.client import Fdfs_client

# 1.创建客户端
# 修改加载配置文件的路径
# client = Fdfs_client(conf_path='utils/fastdfs/client.conf')

# 2.上传图片
# 图片的绝对路径
# client.upload_by_filename('/Users/guoxi/Desktop/tracker和storage容器运行的说明.png')

# {'Group name': 'group1', 'Remote file_id': 'group1/M00/00/00/wKgAb2KDuwmAWlW_AAJPDqdyBHU830.png', 'Status': 'Upload successed.', 'Local file name': 'Desktop/tracker和storage容器运行的说明.png', 'Uploaded size': '147.00KB', 'Storage IP': 'host'}

# 3.获取file_id .upload_by_filename 上传成功会返回字典数据
# 字典数据中 有file_id

############################################
import logging

from django.shortcuts import render
from django.views import View
from utils.goods import get_categories
from apps.contents.models import ContentCategory

logger = logging.getLogger('django')

class IndexView(View):
    """首页广告"""
    def get(self, request):
        """
        首页的数据分为2部分
        1部分是 商品分类数据
        2部分是 广告数据
        """
        # 1.商品分类数据
        categories = get_categories()
        # 2.广告数据
        contents = {}
        content_categories = ContentCategory.objects.all()
        for cat in content_categories:
            contents[cat.key] = cat.content_set.filter(status=True).order_by('sequence')

        # 后续讲解页面静态化
        # 数据传递给模版
        context = {
            'categories': categories,
            'contents': contents
        }

        # 模版使用较少，暂时学习过渡使用
        return render(request, 'index.html', context)


"""
需求：
        根据点击的分类，来获取分类数据（有排序，有分页）
前端：
        前端会发送一个axios请求， 分类id 在路由中， 
        分页的页码（第几页数据），每页多少条数据，排序也会传递过来
后端：
    请求          接收参数
    业务逻辑       根据需求查询数据，将对象数据转换为字典数据
    响应          JSON

    路由      GET     /list/category_id/skus/
    步骤
        1.接收参数
        2.获取分类id
        3.根据分类id进行分类数据的查询验证
        4.获取面包屑数据
        5.查询分类对应的sku数据，然后排序，然后分页
        6.返回响应
"""
from apps.goods.models import GoodsCategory,SKU
from django.http import JsonResponse
from utils.goods import get_breadcrumb

class ListView(View):

    def get(self, request, category_id):
        # 1.接收参数
        # 排序字段
        ordering = request.GET.get('ordering')
        # 页码
        page = request.GET.get('page')
        # 每页返回的数据
        page_size = request.GET.get('page_size')

        # 2.获取分类id  - category_id，已传

        # 3.根据分类id进行分类数据的查询验证
        try:
            # 获取三级菜单分类信息
            category = GoodsCategory.objects.get(id=category_id)
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': 400, 'errmsg': '获取分类数据失败'})

        # 4.获取面包屑数据
        breadcrumb = get_breadcrumb(category)

        # 5.查询分类对应的sku数据，然后排序，然后分页, 根据 分类信息和是否上架查询sku信息
        skus = SKU.objects.filter(category=category,is_launched=True).order_by(ordering)
        # 分页
        from django.core.paginator import Paginator
        """
        Paginator必传参数 object_list, per_page
        object_list: 列表数据
        per_page:    每页数据大小
        """
        paginator = Paginator(object_list=skus, per_page=page_size)
        # 获取指定页码数据
        page_skus = paginator.page(page)

        # 定义列表:
        sku_list = []
        # 将对象转换为字典数据
        for sku in page_skus.object_list:
            sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url
            })

        # 获取总页码
        total_num = paginator.num_pages

        # 6.返回响应
        return JsonResponse({
            'code': 0,
            'msg': 'ok',
            'breadcrumb': breadcrumb,
            'list': sku_list,
            'count': total_num
        })


class HotGoodsView(View):
    """商品热销排行"""
    def get(self, request, category_id):
        # 1.接收数据
        # 2.获取分类id category_id
        # 3.根据分类id进行SKU数据的查询验证
        try:
            skus = SKU.objects.filter(category_id=category_id, is_launched=True).order_by('sales')[:2]
        except Exception as e:
            logger.error(e)
            return JsonResponse({'code': 400, 'errmsg': '获取热销商品失败'})
        # 4.组装数据
        sku_list = []
        for sku in skus:
            sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url
            })
        # 5.返回响应
        return JsonResponse({
            'code': 0,
            'msg': 'ok',
            'hot_skus': sku_list
        })


########################################################################
"""
搜索 

1. 我们不使用like

2. 我们使用 全文检索
    全文检索即在指定的任意字段中进行检索查询

3. 全文检索方案需要配合搜索引擎来实现

4. 搜索引擎

    原理：  关键词与词条的对应关系，并记录词条的位置


        1  --- 我爱北京天安门                      我爱， 北京，天安门

        2 --- 王红，我爱你，我想你想的睡不着觉        王红，我爱，我爱你，睡不着觉，想你，

        3 ---  我睡不着觉                          我，睡不着觉 


        我爱


5. Elasticsearch
    进行分词操作 
    分词是指将一句话拆解成多个单字或词，这些字或词便是这句话的关键词

    下雨天 留客天 天留我不 留


6. 
    数据         <----------Haystack--------->             elasticsearch 

                        ORM(面向对象操作模型)                 mysql,oracle,sqlite,sql server
"""

"""
 我们/数据         <----------Haystack--------->             elasticsearch 

 我们是借助于 haystack 来对接 elasticsearch
 所以 haystack 可以帮助我们 查询数据
"""
from haystack.views import SearchView

class SKUSearchView(SearchView):

    def create_response(self):
        # 默认返回 HttpResponse，需要继承重写

        # 获取搜索结果
        context = self.get_context()

        # 添加断点来分析 context 里边有什么数据   -- 对象.列表
        sku_list = []
        for sku in context['page'].object_list:
            sku_list.append({
                'id': sku.object.id,
                'name': sku.object.name,
                'price': sku.object.price,
                'default_image_url': sku.object.default_image.url,
                'searchkey': context.get('query'),
                'page_size': context['page'].paginator.num_pages,
                'count': context['page'].paginator.count
            })

        # 返回响应数据
        return JsonResponse(sku_list, safe=False)