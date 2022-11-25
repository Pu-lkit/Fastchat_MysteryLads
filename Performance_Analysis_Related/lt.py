# PROCESSING THE LOGS

# Logs will be in the format
# <sender> <receiver> <send_time> <receive_time>

import sys

def process_log(logfile):
    li = []
    
    with open(logfile, 'r') as f:
        for line in f:
            k = line.split()
            if len(k) == 0:
                break
            
            dc = {
                'sender' : '',
                'receiver' : '',
                'send_time' : -1,
                'receive_time' : -1
            }
            #print(k)
            dc['sender'] = k[0]
            dc['receiver'] = k[1]
            dc['send_time'] = int(k[2])
            dc['receive_time'] = int(k[3])
            li.append(dc)
            
    return li

# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

def find_latency(plog):
    N = len(plog)
    sum = 0
    
    for dc in plog:
        #print(abs(dc['send_time'] - dc['receive_time']))
        sum = sum + abs(dc['send_time'] - dc['receive_time'])
    
    #print(sum)
    lt = sum / N
    return lt

# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

def find_throughput(plog):
    # Assuming zero sleep time between messages
    N = len(plog)
    minT = plog[0]['send_time']
    maxT = plog[0]['receive_time']
    
    for dc in plog:
        minT = min(minT, dc['send_time'])
        maxT = max(maxT, dc['receive_time'])
    #print(maxT)
    #print(minT)
    #print((maxT - minT) / 1000)
    #print(N)
    #print(N / (maxT - minT))
    thp = (1e3)*N / (maxT - minT)
    return thp
    
# '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

if __name__ == "__main__":
    li = process_log(sys.argv[1])
    N = int(sys.argv[2])
    M = int(sys.argv[3])
    b = float(sys.argv[4])
    msg_pattern = sys.argv[5]
    #for a in li:
        #print(a)
    lt = find_latency(li)
    print(lt)
    thp = find_throughput(li)
    print(thp)
    #M = len(li)
    with open("data.txt", 'a') as f:
        f.write(f"""SINGLE SERVER,   2+1,   {N},   {M},  {msg_pattern}(mean={b}),    {lt},    {thp}\n""")
