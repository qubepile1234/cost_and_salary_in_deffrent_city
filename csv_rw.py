import csv
def read_existing_csv(file_path):
    """读取现有的CSV文件数据"""
    try:
        data = []
        with open(file_path, 'r', encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            ## 跳过表头
            # next(reader, None)
            # 读取所有数据行
            for row in reader:
                data.append(row)
        return data
    except Exception as e:
        print(f"读取CSV文件失败: {e}")
        return []

def saveData(datalist, savepath, append_mode=False):
    """保存数据到CSV，支持追加模式"""
    print("正在保存数据...")
    try:
        headers = (
                "职位标题","职位链接",
                "公司名称", "工作地点",
                "薪资待遇", "职位描述",
                "职位类型", "发布时间",
                "职位特征", "所需技能",
                "申请类型",'勤務時間・休日',
                '仕事内容','給与・報酬',
                '雇用形態','勤務地・交通'
                )
        # CSV写入模式：追加模式用 'a'，覆盖模式用 'w'
        mode = 'a' if append_mode else 'w'
        
        with open(savepath, mode, encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            
            # 如果是覆盖模式，写入表头
            if not append_mode:
                writer.writeheader()
            
            # 写入数据
            for i, data in enumerate(datalist):
                writer.writerow(data)
                
                # 显示进度
                if (i + 1) % 10 == 0:
                    print(f'已保存 {i + 1} 条记录')
        
        print(f"数据已保存到: {savepath}")
        
    except Exception as e:
        print(f"保存文件时出错: {e}")
        raise
