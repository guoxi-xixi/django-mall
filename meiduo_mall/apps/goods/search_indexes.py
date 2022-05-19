import datetime
from haystack import indexes
from apps.goods.models import SKU

"""
0. 我们需要在 模型所对应的 子应用中 创建 search_indexes.py 文件。以方便haystack来检索数据
1. 索引类必须继承自  indexes.SearchIndex, indexes.Indexable
2. 必须定义一个字段 document=True
    字段名 起什么都可以。 text只是惯例（大家习惯都这么做） 。
    所有的索引的 这个字段 都一致就行
3. use_template=True
    允许我们来单独设置一个文件，来指定哪些字段进行检索

    这个单独的文件创建在哪里呢？？？
    模板文件夹下/search/indexes/子应用名目录/模型类名小写_text.txt


 数据         <----------Haystack--------->             elasticsearch 

 运作： 我们应该让 haystack 将数据获取到 给es 来生成索引

    在虚拟环境下  python manage.py rebuild_index

"""

class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    """SKU索引数据模型类"""

    # document=True，表名该字段是主要进行关键字查询的字段。
    # text字段的索引值可以由多个数据库模型类字段组成，具体由哪些模型类字段组成，我们用use_template = True表示后续通过模板来指
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        """返回建立索引的模型类"""
        return SKU

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        """返回要建立索引的数据查询集"""
        # return SKU.objects.filter(is_launched=True)
        return self.get_model().objects.filter(is_launched=True)

"""
Indexing 16 商品SKU
GET /haystack/_mapping [status:404 request:0.062s]

404 非失败
"""