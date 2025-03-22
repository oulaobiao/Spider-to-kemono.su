import concurrent
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor
# 从 pathlib 模块导入 Path 类，用于以面向对象的方式处理文件路径
from pathlib import Path

import psutil
import requests
from PyQt6.QtCore import QThread, pyqtSignal

# 下载的根地址，初始化线程的时候传递
win_path = ''
class worker_don(QThread):
    # 定义信号，用于传递数据给主线程
    data_fetched = pyqtSignal(str)

    def __init__(self,api_url):

        super().__init__()
        self.api_url = api_url      # 访问json数据的地址

    def run(self):
        # 计数器
        dn_num = 1

        # 页数前缀
        directory = '/posts-legacy?o='
        # 页数 以50为单位
        di_num = 0

        # 创建文件夹并将下载任务提交给线程池
        # 以每个文件夹为单位，下载完一个文件夹的内容才会进行下一个循环
        # while循环用于每页的json数据下载
        while True:
            # 每页最终json地址
            all_url = f'{self.api_url}{directory}{di_num}'

            # 创建线程池，用于下载数据，每个ip有时间段限流，
            # 文件下载的时候伴随创建文件夹，多线程可能出现同时占用文件导致线程死锁以及运行报错
            # 所以使用单线程下载
            executor = ThreadPoolExecutor(max_workers=1)

            try:
                time.sleep(2)
                # 访问每页json数据，下载完一页再访问下一页
                resu = requests.get(all_url)
                # 将json数据转换为字典数据
                json_data = json.loads(resu.text)

                # 如果没有数据则退出下载
                if len(json_data) == 1:
                    self.data_fetched().emit('已经获取全部数据')
                    break

                self.data_fetched().emit(f'下载数据中,当前是第{dn_num}页的数据')


                # 该页的标题量
                print(len(json_data['results']))



                # 获取预览和附件的链接并清理，没有预览和附件的帖子文件清除不下载

                # 用于存储每页清理后的数据
                # 获取标题名并清理违规部分
                fil_name_li = [] # 帖子文件夹名
                name_li = []  # 文件名
                server_li = []  # 服务器地址
                don_path_li = []  # 文件的下载地址


                # 打开每个帖子
                for i in range(0, len(json_data['results'])):

                    # 先判断帖子内是否有图片
                    if len(json_data['result_previews'][i]) !=0:

                        # 获取每个帖子内的全部图片
                        # 并将图片分开处理
                        for ul in range(0, len(json_data['result_previews'][i])):

                            # 初次存入数据，防止后面判断地址功能失效
                            if len(don_path_li) == 0:
                                name_li.append(json_data['result_previews'][i][ul]['name'])
                                server_li.append(json_data['result_previews'][i][ul]['server'])
                                don_path_li.append(json_data['result_previews'][i][ul]['path'])
                                fil_name_li.append(json_data['results'][i]['title'])
                                continue

                            # 需要判断的地址
                            path = json_data['result_previews'][i][ul]['path']

                            # 将存储的数据一一取出对比
                            for pa in don_path_li:
                                # 如果有重复的地址则不存入
                                if path == pa:
                                    break
                                # 如果没有重复则存入数据
                                else:
                                    name_li.append(json_data['result_previews'][i][ul]['name'])
                                    server_li.append(json_data['result_previews'][i][ul]['server'])
                                    don_path_li.append(json_data['result_previews'][i][ul]['path'])
                                    fil_name_li.append(json_data['results'][i]['title'])
                                    break



                    # 判断有没有附件
                    if len(json_data['result_attachments'][i]) != 0:

                        # 将每个附件分开处理
                        for ul in range(0, len(json_data['result_attachments'][i])):
                            # 初次存入数据，防止后面判断地址功能失效
                            if len(don_path_li) == 0:
                                name_li.append(json_data['result_attachments'][i][ul]['name'])
                                server_li.append(json_data['result_attachments'][i][ul]['server'])
                                don_path_li.append(json_data['result_attachments'][i][ul]['path'])
                                fil_name_li.append(json_data['results'][i]['title'])
                                continue

                            # 需要判断的地址
                            path = json_data['result_attachments'][i][ul]['path']

                            # 将存储的数据一一取出对比
                            for pa in don_path_li:
                                # 如果有重复的地址则不存入
                                if path == pa:
                                    break
                                # 如果没有重复则存入数据
                                else:
                                    name_li.append(json_data['result_attachments'][i][ul]['name'])
                                    server_li.append(json_data['result_attachments'][i][ul]['server'])
                                    don_path_li.append(json_data['result_attachments'][i][ul]['path'])
                                    fil_name_li.append(json_data['results'][i]['title'])
                                    break

                # 打包数据
                all_don = zip(name_li, server_li, fil_name_li, don_path_li)
                # 将数据与任务对象封装
                all_task = [executor.submit(down_file.get_down,(name),(server),(path),(filname)) for name,server,path,filname in all_don]
                # 将任务对象加载进线程池
                # 直到所有文件下载完毕后再爬取下页数据进行下载
                for future in concurrent.futures.as_completed(all_task):
                    future.result()


            except Exception:
                self.data_fetched().emit('已经获取全部数据，请检查文件')

            # 释放线程池
            executor.shutdown(wait=True)

            # 计数器，下一页
            di_num += 50





# 该类用于线程池，下载数据在指定位置
class down_file:

    def get_down(self,name,path,server,filname):

        # 计数 初始化已下载的文件大小为 0 字节
        downloaded_size = 0

        # 处理下载的地址
        se_url = f'{server}/data/{path}?f={name}'

        # 处理文件名字保证可以合规创建
        safe_name = FileUtils.clean_filename(name)

        # 处理文件夹名合规化
        safe_filname = FileUtils.clean_filename(filname)

        # 最终的文件夹地址
        fn_path = Path(win_path) / safe_filname
        # 判断文件要下载的位置文件夹是否存在，如果不存在则创建文件夹
        if not fn_path.exists():
            FileUtils.create_folder_with_numbering_pathlib(safe_filname, win_path)


        # 处理最终的文件地址
        file_path = fn_path / safe_name

        # 如果有重名的文件创建一个带序号的同名文件，因为前面代码判断过文件的下载地址，
        # 一般不用判断文件是否相同，如果你重新启动程序当我没说，因为这个程序只用于一次性下载，
        # 如果是多次使用下载同一个用户，绝对会有重复文件

        num_fi = 1 # 计数，用于重名文件加序号
        while file_path.exists():

            str_num = f'({num_fi})'  # 用于添加序号
            # 生成带有序号的文件地址
            file_path= file_path / str_num
            num_fi += 1


        # 使用 requests.get 方法发送 HTTP 请求，设置 stream=True 以流式方式下载文件
        response = requests.get(se_url, stream=True)
        # 从响应头中获取文件的总大小，以字节为单位
        # 尝试从响应头中获取 'content-length' 字段的值，如果不存在则返回 0
        total_size = int(response.headers.get('content-length', 0))

        # 使用 with 语句打开本地文件，以二进制写入模式（'wb'）打开
        with open(str(file_path), 'wb') as file:
            # 使用 response.iter_content 方法迭代响应内容，每次迭代返回一个大小为 block_size 的数据块
            for data in response.iter_content():

                file.write(data) # 将当前下载的数据块写入本地文件

                downloaded_size += len(data) # 计数，累加每次下载的数据块大小到已下载的文件大小中

                # 打印当前的下载进度信息
                # 显示已下载的字节数和文件的总字节数
                print(f"已下载: {downloaded_size} / {total_size} 字节")

                # 定义一个函数用于获取文件的存储信息
                def get_file_storage_info(file_path):
                    try:
                        # 获取文件所在磁盘的使用情况
                        # os.path.dirname(file_path) 返回文件所在的目录路径
                        # psutil.disk_usage 方法返回该目录所在磁盘的使用信息
                        disk_usage = psutil.disk_usage(os.path.dirname(file_path))
                        # 获取文件的大小（字节）
                        # os.path.getsize 方法返回指定文件的大小
                        file_size = os.path.getsize(file_path)

                        print(f"文件路径: {file_path}")
                        print(f"文件大小: {file_size} 字节")
                        print(f"磁盘总容量: {disk_usage.total} 字节")
                        print(f"磁盘已使用容量: {disk_usage.used} 字节")
                        print(f"磁盘剩余容量: {disk_usage.free} 字节")
                        print(f"磁盘使用率: {disk_usage.percent}%")
                    except FileNotFoundError:
                        # 若文件未找到，捕获该异常并打印错误信息
                        print(f"文件 {file_path} 未找到。")
                    except Exception as e:
                        # 捕获其他未知异常并打印错误信息
                        print(f"发生错误: {e}")

                # 调用 get_file_storage_info 函数，查询当前下载文件的存储信息
                get_file_storage_info(file_path)


# 该类用于文件夹创建与名称违规
class FileUtils:
    @staticmethod
    # 该方法用于创建文件夹
    def create_folder_with_numbering_pathlib(folder_name, path):
        """
        该函数用于在指定目录下创建一个文件夹。
        如果指定名称的文件夹已存在，会在名称后面添加序号，直到找到可用的名称。
        参数:
        folder_name (str): 要创建的文件夹的名称
        path (str): 要创建文件夹的指定路径
        """
        base_path = Path(path)  # 用户所指定的下载位置
        folder = base_path / folder_name  # 将要创建的文件夹地址

        # 获取文件夹名称的主体部分
        # stem 属性返回路径中最后一个部分（即文件夹名）去掉扩展名后的名称
        # 例如对于路径 "D:/all/test_folder"，folder.stem 会返回 "test_folder"
        base_folder_name = folder.stem

        counter = 1  # 初始化一个计数器，用于在文件夹重名时生成序号

        while folder.exists():
            folder = base_path / f"{base_folder_name} ({counter})"
            counter += 1

        try:
            folder.mkdir()
            print(f"文件夹 {folder} 创建成功。")
            return True
        except Exception as e:
            print(f"创建文件夹时出现错误: {e}")
            return False


    @staticmethod
    # 该方法用于文件名违规修改
    def clean_filename(filename):
        """
        清理文件名，替换违规字符、保留名，处理超长文件名
        :param filename: 原始文件名
        :return: 清理后的有效文件名
        """
        import re

        # 定义 Windows 不允许的特殊字符正则表达式
        windows_invalid_chars = r'[\\/*?:"<>|]'

        # 定义 Windows 保留名称列表
        windows_reserved_names = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7',
                                  'COM8',
                                  'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']

        # 定义 Unix/Linux/macOS 不允许的特殊字符正则表达式
        unix_invalid_chars = r'/'

        # 处理特殊字符
        filename = re.sub(windows_invalid_chars, ' ', filename)

        # 将违规特殊字符替换为空格
        base_name = filename.split('.')[0].upper()

        # 处理保留名称
        if base_name in windows_reserved_names:
            # 提取扩展名
            ext = filename[len(base_name):]
            # 将保留名替换为空格开头
            filename = ' ' + ext.lstrip('.') if ext else ' '

        # 处理超长文件名
        while len(filename) > 255:
            filename = filename[:len(filename) // 2]

        return filename