#!/usr/bin/env python

__author__ ='morban'

import pysolr
import subprocess
import os
import pycurl
from io import BytesIO
import json




def findNumFound(solr, request):
    results = solr.search(request, **{'rows' : '0'})
    return results.hits


def getHttpResponse(url, method="GET", list_files=None, content = 'JSON'):
    buffer = BytesIO()
    c = pycurl.Curl()
    #Send file to process
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.VERBOSE, 0)
    c.setopt(c.HTTPHEADER, ['Authorization: Token token=2d1edf7391684877a5b011fe0278806a'])
    if method == "POST":
        l = [('job[webapp_id]', '2'), ('job[param]', '')]
        l1 = [('files[{}]'.format(i), (c.FORM_FILE, f)) for i, f in enumerate(list_files)]
        l.extend(l1)
        c.setopt(c.HTTPPOST, l)
    elif method == "GET":
        pass
    c.perform()
    print('status: {} '.format(c.getinfo(c.RESPONSE_CODE)))
    response = buffer.getvalue().decode('iso-8859-1')
    print(type(response))
    c.close()
    buffer.close()
    if content == 'JSON':
        return json.loads(response)
    elif content == 'NOT JSON':
        return response
    else:
        raise NameError('Give type of answer')

def tagCr():
    url_solr = url_solr = 'http://147.94.102.100:8983/solr/documents'
    solr = pysolr.Solr(url_solr, timeout=20)
    request = 'platformID:HO AND naked_texte:["" TO *] AND site_name:"http://devhist.hypotheses.org"'
    numFound = findNumFound(solr, request)
    print(numFound)
    stop = numFound
    step = 5
    # Get results by data bundle
    for i in range(0, stop, step):
        print(i)
        results = solr.search(request, **{'rows':step, 'start':i, 'sort':'id DESC'})
        print(len(results))
        (list_files, list_files_result) = saveInputFiles(results)
        links = getLinkResult(list_files, list_files_result)
        saveOutputFiles(links)

def saveInputFiles(results):
    list_files = []
    list_files_result = []
    directory = './corpustest/no_tag/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    for result in results:
        name_id = ''.join((result['id'].replace('http://','').replace('/','_'), '.txt'))
        nero_name_id = name_id.replace('.txt', '_nero.txt')
        list_files_result.append(nero_name_id)
        write_path='{}/{}'.format(directory, name_id)
        if not os.path.exists('./{}'.format(write_path)):
            mode = 'a'
        else:
            mode = 'w'
        with open('{}'.format(write_path), mode) as f:
            f.write(result['naked_texte'])
        list_files.append(write_path)
    print(list_files, list_files_result)
    return list_files, list_files_result


def getLinkResult(list_files, list_files_result):
    resp = getHttpResponse('https://allgo.inria.fr/api/v1/jobs', 'POST', list_files)
    url_id = resp['url']
    job_id = resp['id']
    resp ={}
    resp_status = "in progress"
    while resp_status == 'in progress':
        resp = getHttpResponse(url_id)
        if resp.get('status') == 'in progress':
            continue
        else:
            break
    links = [(f, resp[str(job_id)]['{}'.format(f)]) for f in list_files_result]
    print(links)
    return links

def saveOutputFiles(links):
    directory = './corpustest/tag/'
    if not os.path.exists(directory):
        os.makedirs(directory)
    for file_tag in links:
        write_path='{}/{}'.format(directory, file_tag[0])
        if not os.path.exists('./{}'.format(write_path)):
            mode = 'a'
        else:
            mode = 'w'
        with open('{}'.format(write_path), mode, encoding='iso-8859-1') as f:
            f.write(getHttpResponse((file_tag[1]), content = 'NOT JSON'))
        #latinToUnicode(write_path)

def latinToUnicode(tmpfile):
    BLOCKSIZE = 1024*1024
    with open(tmpfile, 'r') as inf:
        with open(tmpfile, 'w') as ouf:
            while True:
                data = inf.read(BLOCKSIZE)
                if not data: break
                converted = data.decode('latin1').encode('utf-8')
                ouf.write(converted)

if __name__ == '__main__':
    tagCr()

