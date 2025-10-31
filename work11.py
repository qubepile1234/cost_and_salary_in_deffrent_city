# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re
import urllib.request, urllib.error
import xlwt
import time
import random

def main():
    try:
        baseurl = "https://movie.douban.com/top250?start="
        print("开始爬取豆瓣电影Top250...")
        
        datalist = getData(baseurl)
        print(f"成功爬取 {len(datalist)} 条电影数据")
        
        savepath = "豆瓣电影Top250.xls"
        saveData(datalist, savepath)
        
        print("爬取完毕！")
        
    except Exception as e:
        print(f"程序执行出错: {e}")

def getData(baseurl):
    datalist = []
    for i in range(0, 10):
        print(f"正在爬取第 {i+1} 页...")
        url = baseurl + str(i * 25)
        html = askURL(url)
        if not html:
            continue
            
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.find_all('div', class_="item"):
            data = parse_movie_item(item)
            if data:
                datalist.append(data)
        
        # 随机延迟，避免请求过快
        time.sleep(random.uniform(1, 3))
    
    return datalist

def parse_movie_item(item):
    """解析单个电影项目"""
    try:
        data = []
        
        # 电影链接
        link_tag = item.find('a')
        link = link_tag['href'] if link_tag else ''
        data.append(link)
        
        # 图片链接
        img_tag = item.find('img')
        imgSrc = img_tag['src'] if img_tag else ''
        data.append(imgSrc)
        
        # 标题
        title_span = item.find('span', class_='title')
        ctitle = title_span.get_text() if title_span else ''
        data.append(ctitle)
        
        # 外文标题
        other_title = item.find('span', class_='other')
        otitle = other_title.get_text().replace('/', '').strip() if other_title else ''
        data.append(otitle)
        
        # 评分
        rating = item.find('span', class_='rating_num')
        rating = rating.get_text() if rating else '0'
        data.append(rating)
        
        # 评价人数
        judge = item.find_all('span')[-1]
        judgeNum = re.findall(r'\d+', judge.get_text())
        judgeNum = judgeNum[0] if judgeNum else '0'
        data.append(judgeNum)
        
        # 简介
        inq = item.find('span', class_='inq')
        inq_text = inq.get_text().replace('。', '') if inq else ''
        data.append(inq_text)
        
        # 相关信息
        bd = item.find('p', class_='')
        bd_text = bd.get_text().strip() if bd else ''
        bd_text = re.sub(r'\s+', ' ', bd_text)
        data.append(bd_text)
        
        return data
        
    except Exception as e:
        print(f"解析电影信息时出错: {e}")
        return None

def askURL(url):
    """请求URL内容"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    request = urllib.request.Request(url, headers=headers)
    try:
        response = urllib.request.urlopen(request, timeout=10)
        html = response.read().decode("utf-8")
        return html
    except Exception as e:
        print(f"请求URL失败: {url}, 错误: {e}")
        return ""

def saveData(datalist, savepath):
    """保存数据到Excel"""
    print("正在保存数据...")
    try:
        book = xlwt.Workbook(encoding="utf-8")
        sheet = book.add_sheet('豆瓣电影Top250')
        
        # 设置列宽
        widths = [6000, 4000, 4000, 4000, 2000, 3000, 6000, 8000]
        for i, width in enumerate(widths):
            sheet.col(i).width = width
        
        # 表头
        headers = ("电影详情链接", "图片链接", "影片中文名", "影片外国名", 
                  "评分", "评价数", "概况", "相关信息")
        for i, header in enumerate(headers):
            sheet.write(0, i, header)
        
        # 数据
        for i, data in enumerate(datalist):
            for j, value in enumerate(data):
                sheet.write(i+1, j, value)
        
        book.save(savepath)
        print(f"数据已保存到: {savepath}")
        
    except Exception as e:
        print(f"保存文件时出错: {e}")

if __name__ == "__main__":
    main()