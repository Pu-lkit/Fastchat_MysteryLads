from matplotlib import pyplot as plt

if __name__ == "__main__":
    alldata = []
    with open("data.txt", 'r') as f:
        for line in f:
            k = line.split(',')
            #print(k)
            
            dc = {
                "Load_balance" : k[0],
                "No_of_servers" : k[1],
                "No_of_clients" : float(k[2]),
                "No_of_messages" : float(k[3]),
                "msg_pattern" : k[4],
                'latency' : float(k[5]),
                "throughput" : float(k[6]),
                "bandwidth" : 0,
            }
            
            if '0.0' in dc['msg_pattern']:
                dc['bandwidth'] = dc['throughput']
                dc['throughput'] = 0
            
            
            alldata.append(dc)
        
    # Plotting graphs:
    #print(alldata)
    
    x = []
    y1 = []
    y2 = []
    for dc in alldata:
        if '0.0' in dc['msg_pattern']:
            break
        
        x.append(dc['No_of_messages'])
        y1.append(dc['latency'])
        y2.append(dc['throughput'])
        
    plt.plot(x,y1)
    plt.show()
    #plt.plot(x,y2)
    
    
    
    
            
            
