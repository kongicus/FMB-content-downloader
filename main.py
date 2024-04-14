import argparse
from get_fmb_text import save_text
import os
from datetime import datetime


parser = argparse.ArgumentParser()
parser.add_argument("--path", type=str, default="fmb_txt_download")
parser.add_argument("--date", type=str, default='')
args = parser.parse_args()

if args.date == '':

    # Represent an empty string as the minimum date
    most_recent_date = datetime.min
    if os.path.exists(args.path):
        for file_name in os.listdir(args.path):
            # Extract the date part from the file name
            file_name_date_str = file_name.split('_')[0]

            # Convert the date part to a datetime object
            file_date = datetime.strptime(file_name_date_str, '%Y%m%d')  
            
            if file_date > most_recent_date:
                most_recent_date = file_date

    save_text(most_recent_date.strftime("%Y%m%d"), args.path)
else:
    save_text(args.date, args.path)