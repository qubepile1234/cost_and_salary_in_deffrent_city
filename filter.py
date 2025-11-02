import re
def filter_salary_data(datalist):
    """
    筛选薪资数据，过滤掉薪资面议的工作信息
    
    参数:
        datalist: 原始数据列表，每个元素是一个包含工作信息的列表
        
    返回:
        filtered_list: 筛选后的数据列表，不包含薪资面议的工作
    """
    
    if not datalist:
        print("警告: 输入的数据列表为空")
        return []
    
    print("正在筛选薪资数据...")
    
    # 薪资面议的关键词列表（可根据需要扩展）
    salary_keywords = [
        "薪资面议"
    ]
    
    filtered_list = []
    skipped_count = 0
    
    for i, data in enumerate(datalist):
        # 检查数据格式是否正确
        if len(data) < 5:
            print(f"第{i+1}条数据无效，跳过")
            skipped_count += 1
            continue
            
        # 获取薪资信息（第5个元素，索引为4）
        salary_info = str(data['薪资待遇']).strip()
        
        # 检查是否为薪资面议,False为数据可用
        is_salary_negotiable = False
        for keyword in salary_keywords:
            if keyword in salary_info:
                is_salary_negotiable = True
                break
        
        if is_salary_negotiable:
            # 跳过薪资面议的数据
            skipped_count += 1
            if skipped_count <= 5:  # 只显示前5条跳过的记录，避免输出过多
                print(f"跳过薪资面议: {data['职位标题']} - {salary_info}")
        else:
            # 保留有具体薪资的数据
            filtered_list.append(data)
    
    # 输出筛选结果统计
    print(f"筛选完成: 原始数据 {len(datalist)} 条")
    print(f"         保留数据 {len(filtered_list)} 条")
    print(f"         跳过数据 {skipped_count} 条 (薪资面议)")
    
    return filtered_list


def clean_salary_data(salary_text):
    """
    清理薪资数据，删除非数字部分，保留纯薪资信息
    
    参数:
        salary_text: 原始薪资文本
        
    返回:
        cleaned_salary: 清理后的薪资文本
    """
    if not salary_text:
        return ""
    
    # 定义需要删除的非数字部分模式
    patterns_to_remove = [
        r'\s*\/\s*賞与あり・昇給あり',
        r'\s*\/\s*賞与あり',
        r'\s*\/\s*昇給あり',
        r'\s*\/\s*昇給',
        r'\s*\/\s*賞与',
        r'\s*・昇給あり',
        r'\s*・賞与あり',
        r'\s*賞与あり',
        r'\s*昇給あり',
        r'\s*賞与',
        r'\s*昇給',
    ]
    
    cleaned_salary = str(salary_text).strip()
    
    # 逐步删除各种非数字部分
    for pattern in patterns_to_remove:
        cleaned_salary = re.sub(pattern, '', cleaned_salary)
    
    # 清理多余的空格
    cleaned_salary = re.sub(r'\s+', ' ', cleaned_salary).strip()
    
    return cleaned_salary


def filter_datalist(datalist,no_salary=True,text_remove_salary=True,mon_is_year_no=True):
    """
    处理datalist
    no_salary: 是否过滤掉薪资面议的工作信息
    text_remove_salary: 是否清理薪资数据，删除非数字部分，保留
    mon_is_year_no: 是月薪还是年薪
    """
    if no_salary:
        datalist = filter_salary_data(datalist)
    if text_remove_salary:
        datalist = filter_and_clean_datalist(datalist)
    return datalist


def filter_and_clean_datalist(datalist):
    """
    筛选并清理数据列表中的薪资信息
    
    参数:
        datalist: 原始数据列表，每个元素是一个包含工作信息的列表
        
    返回:
        cleaned_datalist: 清理后的数据列表
    """
    if not datalist:
        return []
    
    cleaned_datalist = []
    
    for data in datalist:
        # 确保数据格式正确（至少有5个元素）
        if len(data) >= 5:
            # 复制原数据
            cleaned_data = data.copy()
            # 清理第5个元素（薪资信息）
            cleaned_data['薪资待遇'] = clean_salary_data(data['薪资待遇'])
            cleaned_datalist.append(cleaned_data)
        else:
            # 如果数据格式不正确，直接添加
            cleaned_datalist.append(data)
    
    return cleaned_datalist
