#-*- coding: utf-8 -*-

__author__ = 'morban'
__email__ = 'mathieu.orban@openedition.org'


import socket
from multiprocessing import Pool, cpu_count
import sys
sys.path.append('../')
import settings

sys.path.append(settings.analysis_path)
data_path = settings.analysis_path + "data/"
from sent_analysis import Echo
import time
import json
import traceback


#Socket initilisation
sock_conf = settings.sock_config_analysis['net']
sock = socket.socket(sock_conf['fam'], sock_conf['type'])
sock.bind((sock_conf['addr'], sock_conf['port']))
sock.listen(1)


def runAnalysis(args):
    try:
        print("START sentiment analysis on '{}'".format(args['id']))
        id_request = args['id']
        txt = args['txt_lst']
        old_stdout = sys.stdout
        with open('/dev/null', 'w') as sys.stdout: #deactivating sent-analysis output
            result = Echo(False, './model/reviewvocab.txt', './model/review.pkl').getResult(txt, data_path)
            sys.stdout = old_stdout
            print("END simpleLabeling on '{}'".format(args['id']))
    except Exception as e:
        traceback.print_exc()
        raise e
    return { 'id':id_request, 'txt_annoted':result }

#Pool initialisation
analysis_pool = Pool(int(cpu_count()*2))#To test concurrent access to ressources (specially files)

while True:
    print("Waiting connection")
    connection, client_addr = sock.accept()
    try:
        #Getting data in small chunck from annotator
        data = ''
        again = True
        while again:
            rd = connection.recv(1024)
            if rd:
                if settings.sock_config_analysis['END_CHR'] in rd:
                    again = False
                    rd = rd.replace(settings.sock_config_analysis['END_CHR'], '')
                data += rd
            else:
                raise RuntimeError()
        #Converting data from json
        analysis_requests = json.loads(data.decode(encoding='utf8'))

        try:
            #Now in analysis_requests we have an array of dict with keys : id, txt_lst
            print("Data received, sending them to the pool")
            nrequests = len(analysis_requests)
            start_t = time.time()
            analysis_results = analysis_pool.map(runAnalysis, analysis_requests)
            stop_t = time.time()
            if nrequests !=0:
                print("Processing of {} requests done in {}s ( {}s per requests)".format(nrequests, stop_t - start_t, float(stop_t - start_t)/nrequests))
            else:
                print("Processing of 0 requests done in {}s".format(stop_t - start_t))
            #Now in analysis results we have an array of dict with keys : id, result
            #Where result is an array of tuple (polarity and sentence)
            connection.sendall(json.dumps(analysis_results))
            connection.close()

        except Exception as e:
            traceback.print_exc()
            #Cleaning
            analysis_pool.terminate()
            connection.close()
            sock.close()
            raise e
    except RuntimeError:
        print("Connection with sentimen-anlysis lost")
sock.close()





