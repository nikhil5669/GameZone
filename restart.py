import os
import time

def restart_main_script():
    os.system("python main.py")

if __name__ == "__main__":
    while True:
        print("Restarting main.py...")
        restart_main_script()
        print("Waiting for 1 minute before restarting again...")
        time.sleep(60)  # Wait for 1 minute before restarting
