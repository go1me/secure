#!/usr/bin/env python2

import argparse
import pprint
import sys

# Suppress scapy warning if no default route for IPv6. This needs to be done before the import from scapy.
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)


# Try to import sniff from scapy.all and show error w/ install instructions if it cannot be imported.
try:
    from scapy.all import *#sniff
    import scapy.layers.http as scapy_http
except ImportError:
    sys.stderr.write("ERROR: You must have scapy installed.\n")
    sys.stderr.write("You can install it by running: sudo pip3 install -U 'scapy'")
    exit(1)



def prn_oper(pkt):#HTTPRequest
    #pprint.pprint(pkt.getlayer(scapy_http.HTTPResponse).fields, indent=4)
    flag =False
    ip_layer=pkt.getlayer('IP')
    if not ip_layer:
        pprint.pprint("no ip_layer")
        return
    tcp_layer=pkt.getlayer('TCP')
    data ={}
    if tcp_layer:
        data['time']=ip_layer.time
        data['src']=ip_layer.src
        data['dst']=ip_layer.dst
        data['version']=ip_layer.version

        data['seq']=tcp_layer.seq
        data['ack']=tcp_layer.ack

        data['sport']=tcp_layer.sport
        data['dport']=tcp_layer.dport

    if pkt.haslayer(scapy_http.HTTPRequest):
        data['type'] = "HTTPRequest"
        http_header = pkt[scapy_http.HTTPRequest].fields
        for i in http_header.keys():
            data[i]=http_header[i]
        flag = True

    if pkt.haslayer(scapy_http.HTTPResponse):
        data['type'] = "HTTPResponse"
        http_header = pkt[scapy_http.HTTPResponse].fields
        for i in http_header.keys():
            data[i]=http_header[i]
        flag = True

    if flag ==True:
        if 'Raw' in pkt:
            payload = pkt['Raw'].load
            if payload:
                #if isinstance(payload,str):
                data["payload"]=payload#.decode('utf8')
        pprint.pprint(data)
    


if __name__ == "__main__":
    # Parser command line arguments and make them available.
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Print HTTP Request headers (must be run as root or with capabilities to sniff).",
    )
    parser.add_argument("--interface", "-i", help="Which interface to sniff on.", default="eth0")
    parser.add_argument("--filter", "-f", help='BPF formatted packet filter.', default="tcp and port 80")
    parser.add_argument("--count", "-c", help="Number of packets to capture. 0 is unlimited.", type=int, default=0)

    parser.add_argument("--offline", "-o", help='offline pcap.', default=None)
    args = parser.parse_args()

    # Sniff for the data and print it using lambda instead of writing a function to pretty print.
    # There is no reason not to use a function you write for this but I just wanted to keep the example simply while
    # demoing how to only match HTTP requests and to access the HTTP headers as pre-created dict's instead of
    # parsing the data as a string.

    '''
    def sniff(count=0, store=1, offline=None, prn=None,filter=None, L2socket=None, timeout=None, opened_socket=None, stop_filter=None, iface=None，*args,**kargs)

    count：抓包的数量，0表示无限制；
    store：保存抓取的数据包或者丢弃，1保存，0丢弃
    offline：从 pcap 文件读取数据包，而不进行嗅探，默认为None
    prn：为每一个数据包定义一个函数，如果返回了什么，则显示。例如：prn = lambda x: x.summary()； （  packct.summar()函数返回的是对包的统计性信息 ）
    filter：过滤规则，使用wireshark里面的过滤语法
    L2socket：使用给定的 L2socket
    timeout：在给定的时间后停止嗅探，默认为 None
    opened_socket：对指定的对象使用 .recv() 进行读取；
    stop_filter：定义一个函数，决定在抓到指定数据包后停止抓包，如：stop_filter = lambda x: x.haslayer(TCP)；
    iface：指定抓包的接口

    lfilter=lambda x: x.haslayer(scapy_http.HTTPResponse),

        
    '''
    if args.offline !=None:
        sniff(offline=args.offline,
            filter=args.filter,
            prn=prn_oper,
            count=args.count
        )
    else:
        sniff(iface=args.interface,
            promisc=False,
            filter=args.filter,
            prn=prn_oper,
            count=args.count
        )
