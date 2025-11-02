import time
import requests
from bs4 import BeautifulSoup
import os
import csv
import work13 as work13

def get_job_details(job_url):
    """
    从工作详情页面提取详细信息
    """
    details = {
        '仕事内容': '',
        '勤務時間・休日': '',
        '其他信息': ''
    }
    
    try:
        # 请求详情页面
        detail_html = work13.askURL(job_url)
        if not detail_html:
            return details
            
        detail_soup = BeautifulSoup(detail_html, 'html.parser')
        
        # 查找所有包含详细信息的段落
        detail_lines = detail_soup.find_all('p', class_='p-detail_line')
        
        # 根据内容特征提取信息
        for i, line in enumerate(detail_lines):
            text = line.get_text(strip=True)
            
            # 判断内容类型并分类存储
            if '具体的なお仕事内容' in text or '仕事内容' in text:
                # 获取工作内容部分
                job_content_parts = []
                # 从当前元素开始，获取后续相关内容
                j = i
                while j < len(detail_lines) and not ('勤務時間' in detail_lines[j].get_text() or '【勤務時間】' in detail_lines[j].get_text()):
                    job_content_parts.append(detail_lines[j].get_text())
                    j += 1
                details['仕事内容'] = '\n'.join(job_content_parts)
                
            elif '【勤務時間】' in text or '勤務時間' in text:
                # 获取勤務時間部分
                time_parts = []
                j = i
                while j < len(detail_lines) and j < i + 10:  # 限制获取后续10个段落
                    time_parts.append(detail_lines[j].get_text())
                    j += 1
                details['勤務時間・休日'] = '\n'.join(time_parts)
                
    except Exception as e:
        print(f"提取工作详情失败 {job_url}: {e}")
    
    return details

def getData(baseurl):
    """
    获取第一层页面数据，并跳转到详情页面获取更多信息
    """
    datalist = []
    html = work13.askURL(baseurl)
    soup = BeautifulSoup(html, 'html.parser')
    
    # 查找所有工作条目
    job_items = soup.find_all('div', class_="p-result_list_item")
    
    for item in job_items:
        try:
            # 提取基本信息（你现有的代码）
            job_title_elem = item.find('span', class_='p-result_name')
            job_title = job_title_elem.text.strip() if job_title_elem else ""
            
            company_elem = item.find('span', class_='p-result_company')
            company = company_elem.text.strip() if company_elem else ""
            
            location_elem = item.find('span', class_='p-result_area')
            location = location_elem.text.strip() if location_elem else ""
            
            salary_elem = item.find('span', class_='p-result_salary')
            salary = salary_elem.text.strip() if salary_elem else ""
            
            # 提取详情页链接
            link_elem = item.find('a', class_='p-result_title_link')
            if link_elem and link_elem.has_attr('href'):
                # 构建完整的详情页URL
                detail_url = "https://xn--pckua2a7gp15o89zb.com" + link_elem['href']
                
                # 跳转到详情页面获取更多信息
                print(f"正在获取详情: {job_title}")
                job_details = get_job_details(detail_url)
                
                # 添加延迟，避免请求过快
                time.sleep(1)
                
            else:
                job_details = {
                    '仕事内容': '',
                    '勤務時間・休日': '',
                    '其他信息': ''
                }
            
            # 合并所有信息
            job_data = {
                '职位名': job_title,
                '公司名': company,
                '工作地点': location,
                '薪资': salary,
                '仕事内容': job_details['仕事内容'],
                '勤務時間・休日': job_details['勤務時間・休日'],
                '详情链接': detail_url if link_elem and link_elem.has_attr('href') else ''
            }
            
            datalist.append(job_data)
            
        except Exception as e:
            print(f"解析工作条目时出错: {e}")
            continue
    
    return datalist

def saveData(datalist, save_path, append=False):
    """
    保存数据到CSV文件，包含新的字段
    """
    fieldnames = ['职位名', '公司名', '工作地点', '薪资', '仕事内容', '勤務時間・休日', '详情链接']
    
    mode = 'a' if append else 'w'
    with open(save_path, mode, newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not append or (append and f.tell() == 0):
            writer.writeheader()
        
        for data in datalist:
            writer.writerow(data)

def read_existing_csv(file_path):
    """
    读取现有的CSV文件（如果需要追加模式）
    """
    existing_data = []
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_data.append(row)
    except Exception as e:
        print(f"读取现有文件失败: {e}")
    
    return existing_data
