"""
https://docs.djangoproject.com/zh-hans/3.2/howto/custom-file-storage/#django.core.files.storage._open

1. 你自定义的存储系统必须为 Django.core.files.storage.Storage 的一个子类:
2. Django 必须能以无参数实例化你的存储系统。意味着所有配置都应从 django.conf.settings 配置中获取:
        我们在创建存储类的时候，不传递任何参数
3. 在你的存储类中，除了其他自定义的方法外，还必须实现 _open() 以及 _save() 等其他适合你的存储类的方法。
    url
"""

from django.core.files.storage import Storage
from meiduo_mall import settings

class MyStorage(Storage):
    """自定义文件存储系统，修改存储的方案"""
    def __init__(self, fdfs_base_url=None):
        """
        构造方法，可以不带参数，也可以携带参数
        :param base_url: Storage的IP
        """
        self.fdfs_base_url = fdfs_base_url or settings.FDFS_BASE_URL

    def _open(self, name, mode='rb'):
        """Retrieve the specified file from storage."""
        pass

    def _save(self, name, content, max_length=None):
        """
        Save new content to the file specified by name. The content should be
        a proper File object or any Python file-like object, ready to be read
        from the beginning.
        """
        pass

    def url(self, name):
        """
        返回name所指文件的绝对URL
        :param name: 要读取文件的引用:group1/M00/00/00/wKhnnlxw_gmAcoWmAAEXU5wmjPs35.jpeg
        :return: http://192.168.103.158:8888/group1/M00/00/00/wKhnnlxw_gmAcoWmAAEXU5wmjPs35.jpeg
        """
        # return 'http://127.0.0.1:8888/' + name
        # return 'http://image.meiduo.site:8888/' + name
        return self.fdfs_base_url + name