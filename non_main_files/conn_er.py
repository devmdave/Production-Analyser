import os
import subprocess
# Start the .exe and get the process object
DETACHED_PROCESS = 0x00000008
process = subprocess.Popen(
    ["write_at_time.exe"],
    creationflags=DETACHED_PROCESS
)


# Get the PID
pid = process.pid

print(f"Started process with PID: {pid}")

r = input("enter the char to kill process.")

if r == "q":
    os.system('taskkill /F /PID {}'.format(pid))
    exit(0)


