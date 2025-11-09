import requests
import pandas as pd
from datetime import datetime


def fetch_fund_data(fund_code="009505"):
    """
    东方财富网基金净值接口
    参数说明：
    fund_code: 基金代码（默认富国上海金ETF联接C）
    """
    url = "https://api.fund.eastmoney.com/f10/lsjz"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Referer": f"http://fund.eastmoney.com/{fund_code}.html"
    }

    params = {
        "fundCode": fund_code,
        "pageIndex": 1,
        "pageSize": 100,  # 单页数据量
        "startDate": "",
        "endDate": "",
        "rt": "0.123456"  # 随机数防缓存
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data["Data"]["LSJZList"]:
            return data["Data"]["LSJZList"]
        else:
            print("未获取到有效数据，请检查基金代码或网络连接")
            return None
    except Exception as e:
        print(f"请求异常: {str(e)}")
        return None


def data_to_dataframe(raw_data):
    """数据清洗与格式化"""
    if not raw_data:
        return pd.DataFrame()

    df = pd.DataFrame(raw_data)
    # 关键修改：日期格式改为 "%Y-%m-%d"，匹配数据中的 "年-月-日" 格式
    df["FSRQ"] = pd.to_datetime(df["FSRQ"], format="%Y-%m-%d")
    df[["DWJZ", "JZHZ", "LJJZ"]] = df[["DWJZ", "JZHZ", "LJJZ"]].apply(pd.to_numeric)
    df["GRL"] = (df["LJJZ"] - df["DWJZ"]) / df["DWJZ"] * 100  # 计算日增长率

    return df[["FSRQ", "DWJZ", "JZHZ", "LJJZ", "GRL"]]


if __name__ == "__main__":
    # 获取最新数据
    raw_data = fetch_fund_data()

    if raw_data:
        # 数据处理
        clean_data = data_to_dataframe(raw_data)

        # 生成表格
        print("富国上海金ETF联接C实时净值数据：")
        print(clean_data.to_markdown(index=False))

        # 保存到CSV
        filename = f"fund_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        clean_data.to_csv(filename, index=False, encoding="utf_8_sig")
        print(f"\n数据已保存至：{filename}")