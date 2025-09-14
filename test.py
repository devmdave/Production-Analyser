import datetime
import subprocess

# Get current date and time
now = datetime.datetime.now()
# Format it as "14 Sep 2025, 03:45 PM"
formatted_time = now.strftime("%d %b %Y, %I:%M %p")
#setting the backup time in the env
subprocess.run(f'setx LAST_BACKUP_TIME "{formatted_time}"', shell=True)