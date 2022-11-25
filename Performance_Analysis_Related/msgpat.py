# INPUT : 
# >> no of clients, N
# >> no of messages, M

import numpy
import random
import sys
from scipy.stats import expon

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

def exp(N, M, b):
    # b is the parameter of exponential distribution, which is 1 / lambda
    # pdf = 1/b * exp(-x/b)
    
    time_list = expon.rvs(scale=b, size=M-1)
    time_list = numpy.append(time_list, 0)
    li = []
    for i in range(M):
        dc = {
            'first' : 0,
            'second' : 0,
            'sleep_time' : 0.1
        }
        
        dc['second'] = random.randint(1,N-1)
        dc['sleep_time'] = time_list[i]
        li.append(dc)
        
        
    return li
    
    

def uniform(N, M, gap):
    li = []
    for i in range(M):
        dc = {
            'first' : 0,
            'second' : 0,
            'sleep_time' : 0.6
        }
        
        dc['second'] = random.randint(1,N-1)
        dc['sleep_time'] = gap
        li.append(dc)
    return li
        
        
#def multi_exp(N, M, b):
    

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

def create_file_single_source(li, file_name):
    with open(file_name, 'w') as f:
        # SIGNING UP ALL THE USERS
        
        
        # SENDING MESSAGES
        f.write("login\n")
        f.write(f"u{li[0]['first']}\n")
        f.write("0\n")
        f.write("0.5\n")
        for dc in li:
            f.write(f"send u{dc['second']} hi\n")
            f.write(f"{dc['sleep_time']}\n")
            
        # EXITING
        f.write("logout\n")
        f.write("0.5\n")
        f.write("exit\n")
        
# def create_file_multi_source(li, N, file_name):
    
        

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    
if __name__ == '__main__':
    N = int(sys.argv[1])
    M = int(sys.argv[2])
    b = float(sys.argv[3])
    msg_pattern = sys.argv[4]
    li = []
    if msg_pattern == "exp":
        li = exp(N, M, b)
        
    elif msg_pattern == "uniform":
        li = uniform(N, M, b)
    print(li)
    #with open("tsr.txt", 'w'):
    #    f.write("")
    open('tsr.txt', 'w').close()
    create_file_single_source(li, 'zz.txt')
        
        
    

