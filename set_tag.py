#!/usr/bin/env python

__author__ ='morban'

import pysolr
import subprocess
import os
import pycurl
from io import BytesIO
import json
import argparse
import settings as s


parser = argparse.ArgumentParser(description='set_tag by Mathieu Orban. Get texts in Open Edition, saved them and tagged them.')

parser.add_argument('-c','--corpus', metavar='MODES', type=str, help='corpus file path')
parser.add_argument('-s','--site_name', metavar='SITE', type=str, help='site_name of the journal')
parser.add_argument('-p','--platform', metavar='PLATFORM', type=str, help='platform where you can find documents')
args = parser.parse_args()


def findNumFound(solr, request, filter_query={'rows' : '0'}):
    results = solr.search(request, **filter_query)
    return results.hits


def getHttpResponse(url, method="GET", list_files=None, content = 'JSON'):
    buffer = BytesIO()
    c = pycurl.Curl()
    #Send file to process
    c.setopt(c.URL, url)
    c.setopt(c.WRITEDATA, buffer)
    c.setopt(c.VERBOSE, 0)
    token = s.allgo_key
    c.setopt(c.HTTPHEADER, ['Authorization: Token token=%s' % token])
    if method == "POST":
        l = [('job[webapp_id]', '2'), ('job[param]', '')]
        l1 = [('files[{}]'.format(i), (c.FORM_FILE, f)) for i, f in enumerate(list_files)]
        l.extend(l1)
        c.setopt(c.HTTPPOST, l)
    elif method == "GET":
        pass
    c.perform()
    #print('status: {} '.format(c.getinfo(c.RESPONSE_CODE)))
    response = buffer.getvalue().decode('iso-8859-1')
    c.close()
    buffer.close()
    if content == 'JSON':
        return json.loads(response)
    elif content == 'NOT JSON':
        return response
    else:
        raise NameError('Give type of answer')

def importAndTag():
    solr = pysolr.Solr(s.solr_url, timeout=20)
    platform = args.platform
    request = 'platformID:%s AND site_name:"%s"' % (args.platform, args.site_name)
    filter_query = {'fq':'naked_texte:[* TO *]'}
    numFound = findNumFound(solr, request, filter_query)
    print(numFound)
    stop = numFound
    step = 5
    # Get results by data bundle
    for i in range(0, stop, step):
        print(i)
        results = solr.search(request, **{'rows':step, 'start':i, 'sort':'id DESC'})
        (list_files, list_files_result) = saveInputFiles(results)
        links = getLinkResult(list_files, list_files_result)
        saveOutputFiles(links)

def saveInputFiles(results):
    list_files = []
    list_files_result = []
    directory = ''.join((args.corpus, 'no_tag/'))
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
    return list_files, list_files_result


def getLinkResult(list_files, list_files_result):
    resp = getHttpResponse(s.allgo_url, 'POST', list_files)
    url_id = resp['url']
    job_id = resp['id']
    resp ={}
    resp_status = "in progress"
    print("Inria Allgo processing your job : %s" % job_id)
    while resp_status == 'in progress':
        resp = getHttpResponse(url_id)
        if resp.get('status') == 'in progress':
            continue
        else:
            break
    links = [(f, resp[str(job_id)]['{}'.format(f)]) for f in list_files_result]
    return links

def saveOutputFiles(links):
    directory = ''.join((args.corpus, 'tag/'))
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
    importAndTag()

