# cost_and_salary_in_deffrent_city
爬虫练习，根据某工作网站编写，目标在于爬取生活成本与薪资，找到适合生活的地方

work11为网络上随便找的爬取豆瓣250的代码，引以为参考

work13相比work12采用了csv写入数据而非xls，可以节省空间，work12暂时废弃
work13与work12相比仅修改了
1   def read_existing_excel(file_path):
2   def saveData(datalist, savepath, append_mode=False):
并在def crawl_job_data(start_page, page_count, save_path, append_mode=False):
调用1，2时的代码做了修改
