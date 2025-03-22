import re


# 用于检查输入的链接格式是否有问题，以及输出创作者相关信息

def dispose_url(art_url,self):

    # 存档网站类型
    site_list = ['patreon',
                 'pixiv Fanbox',
                 'discord',
                 'fantia',
                 'afdian',
                 'boosty',
                 'gumroad',
                 'subscribestar',
                 'dlsite']

    front_url = 'https://kemono.su/'

    # josn服务器地址
    server_url = 'https://kemono.su/api/v1/'

    # 标记链接格式是否正确
    ap: bool = False

    if re.match(front_url, art_url):
        # 将存档类型匹配
        for sel in site_list:
            # 判断链接中有无对应的存档类型，有则修改成对应获取json数据的url
            service = re.findall(sel, art_url)

            if len(service) > 0:
                ap = True
                # 将网址切片分离出用户id
                userid = art_url.split(sel)[1]

                # 最后组合url并返回
                json_url = f'{server_url}{sel}{userid}'
                self.text02.setText('格式没问题\n')
                self.api_url = json_url

                break
            else:
                continue

    if ap is False:
        self.text02.setText('你的链接有问题\n')
