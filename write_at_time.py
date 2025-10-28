import time
import os
import datetime
import sys
import subprocess
from my_plc import Plc 
import pandas as pd

#setting production backup service pid in the env
subprocess.run(f'setx PRODUCTION_BACKUP_PID "{os.getpid()}"', shell=True)

parsed_time = None
saved_time = None
try:
    time_input = sys.argv[1]
    parsed_time = datetime.datetime.strptime(time_input, "%H:%M")
    parsed_time = parsed_time.strftime("%H:%M")
    subprocess.run(f'setx PRODUCTION_BACKUP_TIME "{parsed_time}"', shell=True)
except IndexError:
    saved_time = os.getenv("PRODUCTION_BACKUP_TIME")

def update_last_backtime():
    # Get current date and time
    now = datetime.datetime.now()
    # Format it as "14 Sep 2025, 03:45 PM"
    formatted_time = now.strftime("%d %b %Y, %I:%M %p")
    #setting the backup time in the env
    subprocess.run(f'setx LAST_BACKUP_TIME "{formatted_time}"', shell=True)
# Function to save PLC data to an Excel file
# This function takes a dictionary of PLC data, converts it to a pandas DataFrame, and saves it to an Excel file named 'data.xlsx'.
def save_to_excel(tags_data):
    os.makedirs("CycleTimeBackup", exist_ok=True)
    # Convert dictionary to DataFrame
    df = pd.DataFrame(tags_data)
    df.index = range(1, len(df) + 1)
    # Transpose the DataFrame to have tags as rows and their values as columns
    df = df.transpose()
    #get todays date in the format 'dd-mm-yyyy'
    today_str = datetime.datetime.now().strftime('%d-%m-%Y')
    with pd.ExcelWriter(f'./CycleTimeBackup/{today_str}.xlsx') as writer:
        df.to_excel(writer, sheet_name=today_str, index=True)
    
    update_last_backtime()
# Function to wait until the target time
# This function continuously checks the current time and returns when it matches the target time.
def wait_until_target_time():
    if saved_time:
        TARGET_HOUR = saved_time.split(':')[0]    
        TARGET_MINUTE = saved_time.split(':')[1]

    elif parsed_time:
        TARGET_HOUR = parsed_time.split(":")[0]
        TARGET_MINUTE = parsed_time.split(":")[1]
    else:
        TARGET_HOUR = 00
        TARGET_MINUTE = 00

    while True:
        now = datetime.datetime.now()
        if int(now.hour) == int(TARGET_HOUR) and int(now.minute) == int(TARGET_MINUTE):
            return
        # Sleep for 20 seconds to avoid busy waiting
        time.sleep(20)
def main():
    plc = Plc('192.168.0.10')
    while True:
        wait_until_target_time()
        try:
            plc_data = plc.read_cycletime_tags()
            save_to_excel(plc_data)
        except Exception as e:
            pass
        # Wait a minute to avoid multiple writes within the same minute
        time.sleep(60)


main()