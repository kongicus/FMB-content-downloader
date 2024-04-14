import argparse
from get_fmb_text import save_text
import os
from datetime import datetime


parser = argparse.ArgumentParser()
parser.add_argument("--path", type=str, default="fmb_txt_download")
parser.add_argument("--date", type=str, default='')
args = parser.parse_args()

if args.date == '':

    # 将空字符串表示为最小的日期
    most_recent_date = datetime.min
    
    for file_name in os.listdir(args.path):
        
        # 提取文件名中的日期部分
        file_name_date_str = file_name.split('_')[0]

        # 将日期部分转换为 datetime 对象
        file_date = datetime.strptime(file_name_date_str, '%Y%m%d')  
        
        if file_date > most_recent_date:
            most_recent_date = file_date
            
    save_text(most_recent_date.strftime("%Y%m%d"), args.path)
else:
    save_text(args.date, args.path)