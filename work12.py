# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re
import xlwt
import requests

def main():
    try:
        # 目标网站URL - 东京都中央区的求人信息
        baseurl = "https://xn--pckua2a7gp15o89zb.com/%E6%9D%B1%E4%BA%AC%E9%83%BD%E4%B8%AD%E5%A4%AE%E5%8C%BA%E3%81%A7%E3%81%AE%E4%BB%95%E4%BA%8B"
        print("开始爬取求人ボックス - 东京都中央区工作信息...")
        baseurl="https://xn--pckua2a7gp15o89zb.com/it%E3%81%AE%E4%BB%95%E4%BA%8B-%E6%9D%B1%E4%BA%AC%E9%83%BD%E4%B8%AD%E5%A4%AE%E5%8C%BA?pg=2"
        baseurl="https://xn--pckua2a7gp15o89zb.com/it%E3%81%AE%E4%BB%95%E4%BA%8B?pg=2"
        datalist = getData(baseurl)
        print(f"成功爬取 {len(datalist)} 条职位数据")
        
        savepath = "求人ボックス_东京都中央区工作信息.xls"
        saveData(datalist, savepath)
        
        print("爬取完毕！")
        
    except Exception as e:
        print(f"程序执行出错: {e}")


def getData(baseurl):
    datalist = []
    
    print("正在爬取工作信息...")
    html = askURL(baseurl)
    if not html:
        return datalist
        
    soup = BeautifulSoup(html, "html.parser")
    
    # 根据实际网页结构，工作信息在section标签中，class为p-result_card
    job_items = soup.find_all('section', class_="p-result_card")
    
    print(f"找到 {len(job_items)} 个工作项目")
    
    for item in job_items:
        data = parse_job_item(item)
        if data:
            datalist.append(data)
            print(f"已解析: {data[0]} - {data[2]}")
    
    return datalist

def parse_job_item(item):
    """解析单个职位信息 - 针对求人ボックス网站结构"""
    try:
        data = []
        
        # 1. 职位标题和链接
        title_link = item.find('a', class_="p-result_title_link")
        if title_link:
            job_title = title_link.get_text(strip=True)
            # 清理标题中的"新着"标记
            job_title = job_title.replace('新着', '').strip()
            job_link = title_link.get('href', '')
            
            # 处理相对链接
            if job_link and job_link.startswith('/'):
                job_link = "https://xn--pckua2a7gp15o89zb.com" + job_link
        else:
            job_title = "未找到职位标题"
            job_link = ""
        
        data.append(job_title)
        data.append(job_link)
        
        # 2. 公司名称
        company = item.find('p', class_="p-result_company")
        company_name = company.get_text(strip=True) if company else "未找到公司名称"
        data.append(company_name)
        
        # 3. 工作地点
        location_items = item.find_all('li', class_="p-result_icon p-result_area")
        location = "未指定地点"
        if location_items:
            location_text = location_items[0].get_text(strip=True)
            # 清理地点文本
            location = re.sub(r'東京都&nbsp;', '', location_text)
        data.append(location)
        
        # 4. 薪资信息
        salary_items = item.find_all('li', class_="p-result_icon p-result_pay")
        salary = "薪资面议"
        if salary_items:
            salary = salary_items[0].get_text(strip=True)
        data.append(salary)
        
        # 5. 职位描述
        description = item.find('p', class_="p-result_lines")
        desc_text = description.get_text(strip=True) if description else "暂无描述"
        # 清理描述文本
        desc_text = re.sub(r'\s+', ' ', desc_text)
        data.append(desc_text)
        
        # 6. 职位类型
        employ_type_items = item.find_all('li', class_="p-result_icon p-result_employType")
        job_type = "未指定"
        if employ_type_items:
            job_type = employ_type_items[0].get_text(strip=True)
        data.append(job_type)
        
        # 7. 发布时间
        date_info = item.find('p', class_="p-result_updatedAt_hyphen")
        post_date = date_info.get_text(strip=True) if date_info else "未知"
        data.append(post_date)
        
        # 8. 职位特征标签
        feature_tags = item.find_all('li', class_="p-result_tag_feature--ver2")
        features = []
        for tag in feature_tags:
            features.append(tag.get_text(strip=True))
        features_text = ', '.join(features) if features else "无特殊标签"
        data.append(features_text)
        
        # 9. 所需技能（从描述和标签中提取）
        all_text = desc_text + " " + features_text + " " + job_title
        technologies = extract_technologies(all_text)
        data.append(technologies)
        
        # 10. 申请类型（かんたん応募等）
        apply_type = "通常申请"
        easy_apply = item.find('span', class_="p-result_easyApp")
        if easy_apply:
            apply_type = "かんたん応募"
        data.append(apply_type)
        
        return data
        
    except Exception as e:
        print(f"解析职位信息时出错: {e}")
        return None

def extract_technologies(text):
    """从文本中提取技术关键词"""
    tech_keywords = [
        # 编程语言
        'Python', 'Java', 'JavaScript', 'TypeScript', 'Ruby', 'PHP', 'Go', 'Rust', 
        'C#', 'C++', 'Swift', 'Kotlin', 'SQL',
        # 前端框架
        'React', 'Vue', 'Angular', 'jQuery', 'Bootstrap',
        # 后端框架
        'Node.js', 'Django', 'Spring', 'Laravel', 'Ruby on Rails', 'Express',
        # 云服务
        'AWS', 'Azure', 'GCP', 'Heroku',
        # 容器化
        'Docker', 'Kubernetes', 'Terraform',
        # 数据库
        'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Oracle',
        # 操作系统
        'Linux', 'Windows', 'MacOS', 'Unix',
        # 办公软件
        'EXCEL', 'Word', 'PowerPoint', 'Office',
        # 其他技术
        '機械学習', 'AI', 'データ分析', 'ビッグデータ', 'データベース',
        'フロントエンド', 'バックエンド', 'フルスタック', 'Web開発',
        'スマホアプリ', 'iOS', 'Android', 'Flutter', 'React Native',
        # 日语技术词
        'プログラミング', 'システム開発', 'Webサイト', 'アプリ開発',
        # 资格证书
        '簿記', '資格', 'TOEIC', '英語'
    ]
    
    found_tech = []
    text_lower = text.lower()
    
    for tech in tech_keywords:
        if tech.lower() in text_lower:
            found_tech.append(tech)
    
    # 去重
    found_tech = list(set(found_tech))
    return ', '.join(found_tech) if found_tech else "未指定"

def askURL(url):
    """请求URL内容"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://xn--pckua2a7gp15o89zb.com/",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        # 使用requests库，它自动处理编码问题
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'  # 强制使用UTF-8编码
        
        if response.status_code == 200:
            return response.text
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return ""
            
    except requests.exceptions.RequestException as e:
        print(f"请求URL失败: {url}, 错误: {e}")
        return ""
    except Exception as e:
        print(f"其他错误: {e}")
        return ""

def saveData(datalist, savepath):
    """保存数据到Excel"""
    print("正在保存数据...")
    try:
        book = xlwt.Workbook(encoding="utf-8")
        sheet = book.add_sheet('求人ボックス工作信息')
        
        # 设置列宽
        widths = [8000, 6000, 5000, 4000, 4000, 10000, 3000, 3000, 5000, 4000, 3000]
        for i, width in enumerate(widths):
            sheet.col(i).width = width
        
        # 表头
        headers = (
            "职位标题", 
            "职位链接", 
            "公司名称", 
            "工作地点", 
            "薪资待遇", 
            "职位描述", 
            "职位类型", 
            "发布时间", 
            "职位特征", 
            "所需技能",
            "申请类型"
        )
        
        # 表头样式
        header_style = xlwt.easyxf(
            'font: bold on; alignment: horizontal center, vertical center'
        )
        
        for i, header in enumerate(headers):
            sheet.write(0, i, header, header_style)
        
        # 数据样式 - 启用自动换行
        data_style = xlwt.easyxf('alignment: wrap on, vertical top')
        
        # 写入数据
        for i, data in enumerate(datalist):
            for j, value in enumerate(data):
                sheet.write(i+1, j, str(value), data_style)
            
            # 显示进度
            if (i + 1) % 10 == 0:
                print(f'已保存 {i + 1} 条记录')
        
        book.save(savepath)
        print(f"数据已保存到: {savepath}")
        print(f"总共保存了 {len(datalist)} 条职位信息")
        
    except Exception as e:
        print(f"保存文件时出错: {e}")

if __name__ == "__main__":
    # 运行主程序
    main()