import json

import time

import requests
from PyQt6.QtCore import QThread, pyqtSignal


class worker_exa(QThread):

    # 定义信号，用于传递数据给主线程
    data_fetched = pyqtSignal(dict)

    def __init__(self,api_url,main_self):

        super().__init__()
        self.api_url = api_url
        self.main_self = main_self


    def run(self):

        self.main_self.exa_web_rs.setText('尝试连接网络...\n')

        # 页数前缀
        directory = '/posts-legacy?o='


        # 最终要访问的json地址
        all_json_url = self.api_url + directory
        # 防止频繁访问导致封ip
        time.sleep(1)

        # 下载json数据并且进行不保存json文件下载
        try:
            resu = requests.get(all_json_url)
            # 将json数据转换为字典数据
            json_data = json.loads(resu.text)
            if type(json_data) == dict:
                # 将创作者基本信息传递给前台
                self.data_fetched.emit(json_data)
            else:
                self.data_fetched.emit({})

        except Exception:
            self.data_fetched.emit({})





"Mizuki & Suiko (One-Punch Man)- LQ jpg"

"IMG_6464.jpeg"
"/05/61/0561e009abd59ba2b0c300a55a1cc6e875609e2604df5eeb29f51e55d3c7974e.jpg"