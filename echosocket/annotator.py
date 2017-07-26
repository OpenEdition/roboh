#!/usr/bin/env python

__author__ ='morban'
__email__ = 'mathieu.orban@openedition.org'

import re
import sys
import socket
sys.path.append('../')
import settings
import json
import time


def splitLine(txt, regex=''):
    #pattern = re.compile(r"(?<=[.!?]\s)")
    if txt:
        txt_lst = re.split(r'(?<=[.!?])\s', txt)
    else:
        txt_lst = []
    return txt_lst

def annotator(files):
    #Opening socket to send datas to sent-analysis runner
    sock_conf = settings.sock_config_analysis['net']
    sock = socket.socket(sock_conf['fam'], sock_conf['type'])
    sock.connect((sock_conf['addr'], sock_conf['port']))
    request_buff = []
    for name_id, txt in files:
        txt_lst = splitLine(txt)
        if txt_lst:
            request_buff.append({'id': name_id, 'txt_lst': txt_lst})
        else:
            pass
    #Formating datas in a json array of dict with keys: id and txt_lst
    #Value txt_lst is an array of sentence
    msg = json.dumps(request_buff) + settings.sock_config_analysis['END_CHR']
    print("Sending {} requests to sentiment-analysis runner".format(len(request_buff)))
    sock.sendall(msg.encode())
    print("Waiting for sentiment-analysis  runner to reply")
    #Reading sentiment_analysis results
    req_t = time.time()
    rd_res = ''
    while True:
        rd = sock.recv(1024)
        if rd:
            rd_res += rd.decode()
        else:
            break
    req_t = time.time() - req_t
    results = json.loads(rd_res)
    if len(results)!=0:
        print("Received {} answer from sentiment-analysis runner after {}s ({}s per requests)".format(len(results), req_t, req_t/len(results)))
    else:
        print("Received {} answer from sentiment-analysis runner after {}s".format(0, req_t))
    sock.close()
    j=0
    #Processing analysis results
    #For each row, added result from sentiment-analysis
    files_opinion = dict()
    for result in results:
        files_opinion[result['id']] = [r[0] for r in result['txt_annoted']]
    return files_opinion

