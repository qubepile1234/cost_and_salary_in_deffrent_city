# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import re
import xlwt
import xlrd
import requests
import os
import time
from xlutils.copy import copy as xl_copy


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
        location_items = item.find_all('li', class_="c-icon c-icon-result p-result_icon p-result_area")
        location = "未指定地点"
        if location_items:
            location = location_items[0].get_text(strip=True)
            location = location.replace('&nbsp;', ' ')      # 1. 替换HTML实体&nbsp;为普通空格
            location = location.strip()                     # 2. 去除首尾空格
            location = re.sub(r'\s+', ' ', location)        # 3. 合并多个连续空格
        data.append(location)
        
        # 4. 薪资信息
        salary_items = item.find_all('li', class_="c-icon c-icon-result p-result_icon p-result_pay")
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
        employ_type_items = item.find_all('li', class_="c-icon c-icon-result p-result_icon p-result_employType")
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

def crawl_job_data(start_page, page_count, save_path, append_mode=False):
    """
    爬取求人ボックス网站的工作信息
    
    参数:
    start_page (int): 爬取的起始页数
    page_count (int): 要爬取的页数（大于0的整数）
    save_path (str): Excel文件存储路径
    append_mode (bool): 是否在已有文件基础上追加数据（True=追加，False=覆盖）
    调用函数：read_existing_excel，saveData
    待改进：目前需要删除爬取到的第一组元素，因为是无效信息
    """
    
    # 参数验证
    if page_count <= 0:
        print("错误：page_count必须大于0")
        return False
    
    if start_page <= 0:
        print("错误：start_page必须大于0")
        return False
    
    all_data = []  # 存储所有爬取的数据
    
    # 如果选择追加模式且文件已存在，读取现有数据
    existing_data = []
    if append_mode and os.path.exists(save_path):
        try:
            print(f"检测到已有文件 {save_path}，正在读取现有数据...")
            existing_data = read_existing_excel(save_path)
            print(f"已读取 {len(existing_data)} 条现有数据")
        except Exception as e:
            print(f"读取现有文件失败: {e}，将创建新文件")
            append_mode = False
    
    # 爬取指定页数的数据ok
    for i in range(page_count):
        current_page = start_page + i
        print(f"正在爬取第 {current_page} 页...")
        
        try:
            baseurl = f"https://xn--pckua2a7gp15o89zb.com/it%E3%81%AE%E4%BB%95%E4%BA%8B?pg={current_page}"
            page_data = getData(baseurl)
            
            if page_data:
                all_data.extend(page_data)
                print(f"第 {current_page} 页爬取完成，获得 {len(page_data)} 条数据")
            else:
                print(f"第 {current_page} 页爬取失败或没有数据")
                
        except Exception as e:
            print(f"爬取第 {current_page} 页时出错: {e}")
        
        # 添加延迟，避免请求过快
        time.sleep(1)
    
    # 合并数据（如果是追加模式）
    if append_mode and existing_data:
        final_data = existing_data + all_data
        print(f"数据合并完成：现有{len(existing_data)}条 + 新增{len(all_data)}条 = 总计{len(final_data)}条")
    else:
        final_data = all_data
    
    # 保存数据
    if final_data:
        try:
            saveData(final_data, save_path, append_mode and os.path.exists(save_path))
            print(f"数据保存成功！总计 {len(final_data)} 条数据已保存到 {save_path}")
            return True
        except Exception as e:
            print(f"数据保存失败: {e}")
            return False
    else:
        print("没有数据需要保存")
        return False

def read_existing_excel(file_path):
    """读取现有的Excel文件数据"""
    try:
        # 使用xlrd读取现有文件
        workbook = xlrd.open_workbook(file_path)
        sheet = workbook.sheet_by_index(0)
        
        data = []
        # 从第二行开始读取（跳过表头）
        for row_idx in range(1, sheet.nrows):
            row_data = []
            for col_idx in range(sheet.ncols):
                cell_value = sheet.cell_value(row_idx, col_idx)
                row_data.append(str(cell_value))
            data.append(row_data)
        
        return data
    except Exception as e:
        print(f"读取Excel文件失败: {e}")
        return []

def saveData(datalist, savepath, append_mode=False):
    """保存数据到Excel，支持追加模式"""
    print("正在保存数据...")
    try:
        if append_mode and os.path.exists(savepath):
            # 追加模式：打开现有文件并添加新数据
            workbook_r = xlrd.open_workbook(savepath)
            workbook_w = xl_copy(workbook_r)
            sheet = workbook_w.get_sheet(0)
            
            # 获取现有数据的行数
            existing_rows = workbook_r.sheet_by_index(0).nrows
            
            # 从现有数据的下一行开始写入新数据
            start_row = existing_rows
        else:
            # 覆盖模式：创建新文件
            workbook_w = xlwt.Workbook(encoding="utf-8")
            sheet = workbook_w.add_sheet('求人ボックス工作信息')
            
            # 设置列宽
            widths = [8000, 6000, 5000, 4000, 4000, 10000, 3000, 3000, 5000, 4000, 3000]
            for i, width in enumerate(widths):
                sheet.col(i).width = width
            
            # 写入表头（只在覆盖模式或新文件时写入）
            headers = (
                "职位标题", "职位链接", "公司名称", "工作地点", "薪资待遇", 
                "职位描述", "职位类型", "发布时间", "职位特征", "所需技能", "申请类型"
            )
            
            # 表头样式
            header_style = xlwt.easyxf('font: bold on; alignment: horizontal center, vertical center')
            
            for i, header in enumerate(headers):
                sheet.write(0, i, header, header_style)
            start_row = 1
        
        
        # 数据样式 - 启用自动换行
        data_style = xlwt.easyxf('alignment: wrap on, vertical top')
        
        # 写入数据
        for i, data in enumerate(datalist):
            current_row = start_row + i
            
            for j, value in enumerate(data):
                sheet.write(current_row, j, str(value), data_style)
            
            # 显示进度
            if (i + 1) % 10 == 0:
                print(f'已保存 {i + 1} 条记录')
        
        workbook_w.save(savepath)
        print(f"数据已保存到: {savepath}")
        
    except Exception as e:
        print(f"保存文件时出错: {e}")
        raise


def main():
    while True:
        try:
            print("=== 求人ボックス爬虫程序 ===")
            start_page = int(input("请输入起始页数: "))
            page_count = int(input("请输入要爬取的页数: "))
            save_path = input("请输入保存路径（例如: ./工作信息.xls）: ").strip()
            
            # 检查文件是否已存在，询问是否追加
            append_mode = False
            # append_mode 是 用于文件操作的模式之一，允许将新内容追加到现有文件的末尾，而不会覆盖原有内容。
            if os.path.exists(save_path):
                choice = input(f"文件 {save_path} 已存在，是否追加数据？(y/n): ").lower()
                if choice == 'y' or choice == 'yes':
                    append_mode = True
                    print("将在现有文件基础上追加数据")
                else:
                    print("将覆盖现有文件")
            
            # 调用爬虫函数
            success = crawl_job_data(
                start_page=start_page,
                page_count=page_count,
                save_path=save_path,
                append_mode=append_mode
            )
            
            if success:
                print("爬取任务完成！")
            else:
                print("爬取任务失败！")
            
            # 询问是否继续
            continue_choice = input("是否继续爬取？(y/n): ").lower()
            if continue_choice != 'y' and continue_choice != 'yes':
                print("程序结束")
                break
                
        except ValueError:
            print("错误：请输入有效的数字")
        except Exception as e:
            print(f"程序执行出错: {e}")


if __name__ == "__main__":
    main()
    