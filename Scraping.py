# 导入模块
import requests
from lxml import etree
import csv
"""
三行代码的意思就是：

import requests：相当于给我们的收集员一部电话，让它可以通过网络去“打电话”联系豆瓣网站，获取网页内容。
from lxml import etree：这是给它一个高亮笔和一把尺子。当网站把复杂的网页源代码（像HTML）发回来时，
收集员可以用这个工具快速定位并圈出我们关心的信息，比如电影名字、评分在哪里。
import csv：这是给它一个标准的Excel表格模板。这样收集员整理好的信息可以直接规整地填进表格里，方便我们以后查看。
这就好比派一个员工去图书馆查资料，我们得先告诉他：“带上你的手机（打电话问）、荧光笔（标出重点）和笔记本（记录结果）。
"""
# 请求头信息
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
# 这是一个“请求头”，主要是User-Agent信息

moive_list = []
# 准备一个空袋子，用来装每部电影的信息

"""
首先，我们告诉收集员目标在哪，也就是10个页面的网址（url）。
但网站不喜欢被程序频繁访问，所以我们要让收集员“伪装”成正常的浏览器。
headers里的User-Agent信息，就相当于给他准备了一套浏览器的工作服和工牌，让他能“混”进去
"""
for page in range(1, 11):
    # 目标url
    url = f'https://movie.douban.com/top250?start={(page - 1) * 25}&filter='
    # f‘’-----即格式化字符串变量在其中可以插入变量在{}内---{(page - 1) * 25}
    # 发送请求, 获取响应
    res = requests.get(url, headers=headers)
    # 打印响应信息
    # print(res.text)
    # 网页源码文档格式存为html变量
    html = res.text
    # html实例化为etree对象
    tree = etree.HTML(html)

    divs = tree.xpath('//div[@class="info"]')
    # 根目录的下面遍历检索div且class属性为info的容器
    # print(divs)
    for div in divs:
        dic = {}
        # 创建一个空的字典

        title = div.xpath('./div[@class="hd"]/a/span[@class="title"]/text()')
        title_cn = ''.join(title).split('\xa0/\xa0')[0]
        # 制作dic['电影中文名']的值，join方法拼接,split去除\xao( &nbsp; 对应的Unicode编码的十六进制表示),
        # [0]表示提取第一个符合上面xpath条件的对象
        # print(title_cn)
        dic['电影中文名'] = title_cn
        # 添加电影中各种信息的键值对，eg：dic['电影中文名'] = title_cn


        # 电影英文标题
        title_en = div.xpath('./div[@class="hd"]/a/span[2]/text()')[0].strip('\xa0/\xa0')

        dic['电影英文名'] = title_en
        # 电影详情页链接
        links = div.xpath('./div[@class="hd"]/a/@href')[0]
        dic['电影详情页链接'] = links
        # print(links)
        # 导演
        director = div.xpath('./div[@class="bd"]/p/text()')[0].strip('\xa0/\xa0').split('导演: ')[1].split('主演: ')[0]
        dic['导演'] = director.replace('\xa0', '').strip()
        # print(director)

        try:
            act = div.xpath('./div[@class="bd"]/p/text()')[0].strip().split('导演: ')[1].split('主演: ')[1]
            # .strip()去除文本两端的空白字符;.split('导演: ')[1]以"导演: "为分割切取并拿取第二个元素;后同
            # print(act)
        except IndexError as e:
            print(end='')
        # 报错尝试让我们更精确的知道触发什么错误

        # 主演
        dic['主演'] = act
        # 上映年份
        Release_year = div.xpath('./div[@class="bd"]/p/text()')[1].strip().split('/')[0]
        # print(Release_year)
        dic['上映年份'] = Release_year
        # print(Release_year)
        # 国籍
        nationality = div.xpath('./div[@class="bd"]/p/text()')[1].strip().split('/')[1].strip()
        if len(nationality[0].encode('utf-8')) == 1:
            nationality = div.xpath('./div[@class="bd"]/p/text()')[1].strip().split('/')[2].strip()
        else:
            nationality = div.xpath('./div[@class="bd"]/p/text()')[1].strip().split('/')[1].strip()
        # print(nationality)
        dic['国籍'] = nationality
        # print(title_cn, nationality)
        # 类型
        genre = div.xpath('./div[@class="bd"]/p/text()')[1].strip().split('/')[2].strip()
        # 这里的<br>也会作为节点分割
        if len(div.xpath('./div[@class="bd"]/p/text()')[1].strip().split('/')[1].strip()[0].encode('utf-8')) == 1:
            genre = div.xpath('./div[@class="bd"]/p/text()')[1].strip().split('/')[3].strip()

        # 如果不类似于1987&nbsp;/&nbsp;英国 意大利 中国大陆 法国&nbsp;/&nbsp;剧情 传记 历史，
        # 而是1987&nbsp;/US/&nbsp;英国 意大利 中国大陆 法国&nbsp;/&nbsp;剧情 传记 历史，则需要使用if下面的路线

        else:
            genre = div.xpath('./div[@class="bd"]/p/text()')[1].strip().split('/')[2].strip()
        dic['类型'] = genre
        # print(genre)
        # 评分
        score = div.xpath('./div[@class="bd"]/div/span[2]/text()')[0]
        dic['评分'] = score
        # print(score)
        # 评分人数
        num_score = div.xpath('./div[@class="bd"]/div/span[4]/text()')[0]
        dic['评分人数'] = num_score
        # print(dic)
        moive_list.append(dic)
        # print(len(moive_list))  # 检查数据是否全部爬取成功
    print(f'----------------------第{page}页爬取完成--------------------------------------')
print('-----------------------爬虫结束-------------------------------')
# 数据保存
# with open('豆瓣电影Top250.csv', 'w', encoding='utf-8-sig', newline='') as f:
#     # 1. 创建对象
#     writer = csv.DictWriter(f, fieldnames=('电影中文名', '电影英文名', '电影详情页链接', '导演', '主演', '上映年份', '国籍', '类型', '评分', '评分人数'))
#     # 2. 写入表头
#     writer.writeheader()
#     # 3. 写入数据
#     writer.writerows(moive_list)

# *'w' 模式的特点与风险​
# 'w' 模式的特点是“写入”。如果指定的文件（如豆瓣电影Top250.csv）不存在，Python会创建它；
# 如果该文件已经存在**，Python会清空其所有原有内容，然后写入新数据
# 。这是一个需要特别注意的地方，意味着如果不小心再次运行程序，之前保存的数据可能会被覆盖。
#
# 2.
# ​**encoding='utf-8-sig' 的意义**​
# 这个参数指定了文件的编码格式为UTF-8，并带有BOM签名。这对于包含中文等非ASCII字符的文本非常重要，
# 能确保字符正确显示。特别是，当你在Windows系统上用Excel打开CSV文件时，utf-8-sig编码可以避免中文出现乱码
# 。
#
# 3.
# ​**DictWriter 的优势**​
# 使用csv.DictWriter非常方便，因为它允许你通过字典的键（key）来写入数据，代码可读性更好。
# 你只需要确保moive_list中的每个字典都拥有fieldnames中定义的键（即使某些键对应的值为空），
# 写入器就会自动将值放入正确的列