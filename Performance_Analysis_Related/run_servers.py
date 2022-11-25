import sys
import subprocess
LBS = sys.argv[1]   # Load Balancing Strategy

def run_servers1():
    #global choice
    ms = f"python3 main_server.py 5050 2 {LBS}"
    s1 = f"python3 server.py 5060"
    s2 = f"python3 server.py 5070"
    p0 = subprocess.run(f'./parallel_commands.sh "{ms} " "{s1} " "{s2}" ', shell=True, capture_output=True, text=True)
    
def run_servers2():
    #global choice
    ms = f"python3 main_server.py 5000 2 {LBS}"
    s1 = f"python3 server.py 5001"
    s2 = f"python3 server.py 5002"
    p0 = subprocess.run(f'./parallel_commands.sh "{ms} " "{s1} " "{s2}" ', shell=True, capture_output=True, text=True)
 

if __name__ == '__main__':
    run_servers1()
