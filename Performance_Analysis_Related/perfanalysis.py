# It should be used as:
#       $ python3 perfanalysis.py <load_balancing_strategy> <N> <M> <msg_pattern> <parameter>

import lt
from msgpat import *
import sys
import random
import subprocess

LBS = sys.argv[1] # Load Balancing Strategy
#S = int(sys.argv[2]) # Number of servers other than master_server
N = int(sys.argv[2])
M = int(sys.argv[3])
msg_pattern = sys.argv[4]
b = float(sys.argv[5])

def run():
    global LBS
    global N
    global M
    global msg_pattern
    global parameter
    
    li = []
    if msg_pattern == "exp":
        li = exp(N, M, b)
    elif msg_pattern == "uniform":
        li = uniform(N, M, b)
        
    dfile = "dd.txt"
    create_file_single_source(li, N, dfile)
    
    # TODO
    # Run main_server.py, server.py, clients.py according to the parameters
    t = random.randint(0,1)
    
    print(t)
    ms = f"python3 main_server.py {5000+t} 2"
    s1 = f"python3 server.py {5001 + 50*t}"
    s2 = f"python3 server.py {5002 + 50*t}"
    
    '''
    c = f"python3 client.py 3 {5000+t} {5001 + 50*t} {5002 + 50*t}"
    s = ''
    for i in range(1,N):
        with open(f"d{i}.txt" , 'w') as f:
            f.write(f"signup\nu{i}\n0\n")
            s = s + f' "{c} -fl d{i}.txt" '
        
        
    
    with open("a.txt", 'w') as f:
        f.write(s)
    
    
    print(s)
    '''
    
    p0 = subprocess.run(f'./parallel_commands.sh "{ms} " "{s1} " "{s2}"', shell=True, capture_output=True, text=True)
 
    
    #p2 = subprocess.run(f'./parallel_commands.sh {s}', shell=True, capture_output=True, text=True)
    #print(p2)
    #p3 = subprocess.run(f'', shell=True, capture_output=True, text=True)
    #print(p3)

    #print(p1.stdout)
    
    
    
    
run()
