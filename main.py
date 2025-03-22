import sys
from pathlib import Path

from PyQt6.QtCore import QMutex, pyqtSlot
from PyQt6.QtWidgets import QWidget, QApplication, QPushButton, QLineEdit, QVBoxLayout, QLabel, QFileDialog


from examine_url import dispose_url
from Worker.Worker_exame import worker_exa
from Worker.Worker_title import worker_don
class Example(QWidget):


    def __init__(self):
        super().__init__()
        self.mutex = QMutex()
        # 用于储存处理后没有加页数的链接
        self.api_url :str= ''
        self.initUI()




    def initUI(self):
        # 创建一个垂直布局对象vbox
        self.vbox = QVBoxLayout()

        text01 = QLabel("请输入创作者主页链接",self)

        # 接收输入的链接
        self.art_url = QLineEdit()
        # 创建检查按钮
        self.exa_url = QPushButton('检查', self)
        # 连接检查方法
        self.exa_url.clicked.connect(lambda :dispose_url(self.art_url.text(),self))
        # 提示链接问题的文本块
        self.text02 = QLabel(f'\n',self)
        # 创建检查链接网络链接按钮
        self.exa_web_url = QPushButton('检查网络',self)
        self.exa_web_url.clicked.connect(self.exa_threads)
        # 检查链接的提示语
        self.exa_web_rs = QLabel('\n',self)
        # 显示链接指向的创作者信息
        self.text_art = QLabel(f"创作者名字：\n所在平台:\n最新帖子时间:\n最旧帖子时间:\n", self)
        # 选择文件夹按钮
        self.sel_file_a = QPushButton('选择下载位置', self)
        self.sel_file_a.clicked.connect(self.showDialog)
        # 显示所选文件夹的链接
        self.look_fil_a = QLabel(f'\n')
        # 下载按钮
        self.down_file = QPushButton('下载',self)
        self.down_file.clicked.connect(self.down_file_worker)
        #线程下载情况
        self.state_down = QLabel('',self)

        # 将部件添加到布局中
        self.vbox.addWidget(text01)
        self.vbox.addWidget(self.art_url)
        self.vbox.addWidget(self.exa_url)
        self.vbox.addWidget(self.text02)
        self.vbox.addWidget(self.exa_web_url)
        self.vbox.addWidget(self.exa_web_rs)
        self.vbox.addWidget(self.text_art)
        self.vbox.addWidget(self.sel_file_a)
        self.vbox.addWidget(self.look_fil_a)
        self.vbox.addWidget(self.down_file)
        self.vbox.addWidget(self.state_down)
        # 在每个控件前后添加拉伸因子，使控件在垂直方向上均匀分布
        self.vbox.addStretch(1)

        # 将垂直布局vbox设置为当前窗口的布局，这样窗口中的控件会按照该布局进行排列
        self.setLayout(self.vbox)
        self.resize(500, 500) # 调整窗口的大小
        self.center()  # 调用自定义的 center 方法，将窗口移动到屏幕中央
        self.setWindowTitle('down_su') # 设置窗口的标题
        self.show()


    # 初始化以及启动查询线程对象线程方法
    def exa_threads(self):

        self.worker1 = worker_exa(self.api_url, self)
        # 将第一个工作线程的 valueChanged 信号连接到 thread_finished 槽函数，当线程发射该信号时会调用此函数
        self.worker1.data_fetched.connect(self.thread_finished)
        self.worker1.start()


    # 初始化下载线程以及启动线程
    def down_file_worker(self):
        # 通过标题创建文件夹
        self.worker2 = worker_don(self.api_url)
        self.worker2.win_path = self.look_fil_a.text()
        self.worker2.start()
        pass


    # 自定义方法，用于将窗口移动到屏幕中央
    def center(self):
        # 获取窗口的框架几何信息，包含窗口的位置和大小
        qr = self.frameGeometry()
        # 获取当前屏幕的可用几何信息（即不包含任务栏等区域），并找到其中心点
        cp = self.screen().availableGeometry().center()
        # 将窗口框架的中心点移动到屏幕的中心点
        qr.moveCenter(cp)
        # 将窗口移动到调整后框架的左上角位置，从而实现窗口在屏幕中央显示
        self.move(qr.topLeft())

    # 选择下载文件的位置
    def showDialog(self):
        # 获取用户的主目录路径，并将其转换为字符串类型
        home_dir = str(Path.home())
        # 调用 QFileDialog.getExistingDirectory 方法显示文件夹选择对话框
        # 第一个参数 self 表示对话框的父窗口
        # 第二个参数 'Select Directory' 是对话框的标题
        # 第三个参数 home_dir 是对话框打开时默认显示的目录
        directory = QFileDialog.getExistingDirectory(self, 'Select Directory', home_dir)

        if directory:
            self.look_fil_a.setText(directory)


    # 该方法用于在获取用户数据后更新数据
    @pyqtSlot(dict)
    def thread_finished(self, value):

        if not value:
            self.exa_web_rs.setText('你的网络有问题\n')
        else:
            self.exa_web_rs.setText('连接成功')
            self.text_art.setText(f"创作者名字：{value['props']['artist']['name']}\n"
                                                f"所在平台：{value['props']['artist']['service']}\n"
                                                f"最新帖子时间：{value['props']['artist']['updated']}\n"
                                                f"最旧帖子时间：{value['props']['artist']['indexed']}")


        pass

    @pyqtSlot(str)
    def thread_fn(self,vale):
        self.state_down.setText(vale)
def main():
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

