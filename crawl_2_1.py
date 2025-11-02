import time
from bs4 import BeautifulSoup
import csv
import work13 as work13
def get_job_details(job_url):
    """
    从工作详情页面提取详细信息，基于dl>dt>dd结构
    """
    details = {
        '勤務時間・休日': '',
        '仕事内容': '',
        '給与・報酬': '',
        '雇用形態': '',
        '勤務地・交通': ''
    }
    if job_url == "":
        for key in details:
            details[key] = '暂无信息'
        return details
    try:
        # 请求详情页面
        detail_html = work13.askURL(job_url)
        if not detail_html:
            return details
            
        detail_soup = BeautifulSoup(detail_html, 'html.parser')
        
        # 查找所有的详情表格dl
        detail_tables = detail_soup.find_all('dl', class_='p-detail_table')
        
        for table in detail_tables:
            # 获取dt中的标题
            dt_title_elem = table.find('dt', class_='p-detail_table_title')
            if not dt_title_elem:
                continue
                
            title_text = dt_title_elem.get_text(strip=True)
            
            # 获取对应的dd内容
            dd_content_elem = table.find('dd', class_='p-detail_table_data')
            if not dd_content_elem:
                continue
            
            # 提取dd中所有的p标签内容
            p_elements = dd_content_elem.find_all('p', class_='p-detail_line')
            content_text = '\n'.join([p.get_text(strip=False) for p in p_elements if p.get_text(strip=True)])
            
            # 根据标题映射到对应的字段
            if '勤務時間・休日' in title_text or '勤務時間' in title_text:
                details['勤務時間・休日'] = content_text
            elif '仕事内容' in title_text:
                details['仕事内容'] = content_text
            elif '給与・報酬' in title_text:
                details['給与・報酬'] = content_text
            elif '雇用形態' in title_text:
                details['雇用形態'] = content_text
            elif '勤務地・交通' in title_text:
                details['勤務地・交通'] = content_text
    ################################################3    
        # 如果通过dl结构没有找到工作内容，使用原来的后备方法
        if not details['勤務時間・休日']:
            detail_lines = detail_soup.find_all('p', class_='p-detail_line')
            for i, line in enumerate(detail_lines):
                text = line.get_text(strip=True)
                if '具体的なお仕事内容' in text or '仕事内容' in text:
                    job_content_parts = []
                    j = i
                    while j < len(detail_lines) and not any(x in detail_lines[j].get_text() for x in ['勤務時間', '【勤務時間】', '給与', '応募資格']):
                        job_content_parts.append(detail_lines[j].get_text())
                        j += 1
                    details['仕事内容'] = '\n'.join(job_content_parts)
                    break
    ################################################3                
    except Exception as e:
        print(f"提取工作详情失败 {job_url}: {e}")
    
    for key in details:
        if not details[key]:
            details[key] = '暂无信息'
    
    return details

# # 更新保存数据的字段
# def saveData(datalist, save_path, append=False):
#     """
#     保存数据到CSV文件，包含所有详情字段
#     """
#     fieldnames = ['职位名', '公司名', '工作地点', '薪资', '仕事内容', '勤務時間・休日', '給与', '応募資格', '勤務地', '详情链接']
    
#     mode = 'a' if append else 'w'
#     with open(save_path, mode, newline='', encoding='utf-8-sig') as f:
#         writer = csv.DictWriter(f, fieldnames=fieldnames)
        
#         if not append or (append and f.tell() == 0):
#             writer.writeheader()
        
#         for data in datalist:
#             writer.writerow(data)

# # 在getData函数中也要更新字段
def getData(baseurl):
    """
    获取第一层页面数据，并跳转到详情页面获取更多信息
    """
    datalist = []
    html = work13.askURL(baseurl)
    if not html:
        return datalist
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # 查找所有工作条目
    job_items = soup.find_all('div', class_="p-result_list_item")
    
    for item in job_items:
        try:
            # 提取基本信息
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
                    '給与': '',
                    '応募資格': '',
                    '勤務地': ''
                }
                detail_url = ""
            
            # 合并所有信息
            job_data = {
                '职位名': job_title,
                '公司名': company,
                '工作地点': location,
                '薪资': salary,
                '仕事内容': job_details['仕事内容'],
                '勤務時間・休日': job_details['勤務時間・休日'],
                '給与': job_details['給与'],
                '応募資格': job_details['応募資格'],
                '勤務地': job_details['勤務地'],
                '详情链接': detail_url
            }
            
            datalist.append(job_data)
            
        except Exception as e:
            print(f"解析工作条目时出错: {e}")
            continue
    
    return datalist