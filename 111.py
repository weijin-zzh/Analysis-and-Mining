import time
import requests
from bs4 import BeautifulSoup
import csv


def get_movie_data(url):
    """获取单页电影数据"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        return response.text
    except Exception as e:
        print(f"请求失败: {str(e)}")
        return None


def parse_movies(html):
    """解析HTML获取电影信息"""
    soup = BeautifulSoup(html, 'html.parser')
    movies = []

    # 定位所有电影条目
    for item in soup.select('.item'):
        title = item.select_one('.title').text.strip()  # 电影名称
        rating = item.select_one('.rating_num').text.strip()  # 评分
        quote = item.select_one('.inq').text.strip() if item.select_one('.inq') else '暂无简介'  # 简介

        movies.append({
            '电影名称': title,
            '评分': rating,
            '简介': quote
        })

    return movies


def save_to_csv(data, filename='douban_movies.csv'):
    """保存数据到CSV文件"""
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"数据已保存至 {filename}")


if __name__ == '__main__':
    base_url = 'https://movie.douban.com/top250'
    all_movies = []

    # 遍历10个分页
    for page in range(0, 250, 25):
        print(f"正在爬取第 {page // 25 + 1} 页...")
        url = f"{base_url}?start={page}"
        html = get_movie_data(url)

        if html:
            movies = parse_movies(html)
            all_movies.extend(movies)
            time.sleep(1)


    if all_movies:
        save_to_csv(all_movies)
        print(f"共爬取 {len(all_movies)} 条数据")
    else:
        print("未获取到有效数据")