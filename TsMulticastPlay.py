# coding:utf-8,
import socket
import time
import os
import datetime
import argparse

PACKAGE_SIZE = 7*188
ANY = '0.0.0.0'
SENDERPORT = 7002

def command_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f",help="play file")
    parser.add_argument("-b",type=int,help="byterate",default=2000)
    parser.add_argument("-m",help="multicast ip",default='224.0.23.14')
    parser.add_argument("-p",type=int,help="multicast port",default=1314)
    parser.add_argument("-l",type=int,help="Loop",default=1)
    args = parser.parse_args()
    return args
    

def network_init():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.bind((ANY, SENDERPORT))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 255)
    return sock
    
def ReadTsPackage(ts,file_len):
    NullPackage=b'\x471FFF10'+b'\xFF'*(188-4)
    cur_offset = ts.tell()
    if cur_offset == file_len:
        return 7*NullPackage
        
    if (cur_offset+7*188) <= file_len:
        return ts.read(7*188)
    else:
        tmppackage_cnt=(file_len - cur_offset)//188
        tmp = ts.read(tmppackage_cnt*188)+(7-tmppackage_cnt)*NullPackage      
        return tmp
        
def main():
    args = command_parser()
    print(args.f)
    print(args.b)
    print(args.m)
    print(args.p)
    print(args.l)
    
    play_file = args.f
    byterate = args.b*1024//8
    mcast_addr = args.m
    mcast_port = args.p
    loop = args.l
    
    sock = network_init()
    time.sleep(1)
    starttv_time=time.time()
    FILE_SIZE = os.path.getsize(os.path.join(os.getcwd(), play_file))
    total_send_bytes = 0
    multiple = 0
    play_cnt = 1
    with open(os.path.join(os.getcwd(), play_file), mode='rb') as ts:  
        while True:
            if total_send_bytes <=FILE_SIZE:
                time.sleep(0.01)
                cur_time = time.time()
                s_data = ((cur_time-starttv_time)*1000)*byterate/1000
                if(s_data >= total_send_bytes):
                    multiple = int((s_data - total_send_bytes + PACKAGE_SIZE - 1) // PACKAGE_SIZE)
                else:
                    continue
                
                for i in range(0,multiple):
                    # read ts package 7*188
                    buf =ReadTsPackage(ts,FILE_SIZE)
                    sock.sendto(buf, (mcast_addr, mcast_port))
                    total_send_bytes += PACKAGE_SIZE
            else:
                if loop == 1:
                    play_cnt +=1
                    print("Play count: ",play_cnt)
                    total_send_bytes = 0
                    starttv_time=time.time()
                    ts.seek(0)
                else:
                    break
                    
    sock.close()

if __name__ == "__main__": 
    main()
