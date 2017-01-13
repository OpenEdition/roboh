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
from nerd import nerd
from echosocket import annotator 


parser = argparse.ArgumentParser(description='set_tag by Mathieu Orban. Get texts in Open Edition, saved them and tagged them.')

parser.add_argument('-d','--datasource', metavar='DATASOURCE', type=str, help='source required')
parser.add_argument('-c','--corpus', metavar='MODES', type=str, help='corpus file path')
parser.add_argument('-s','--site_name', metavar='SITE', type=str, help='site_name of the journal')
parser.add_argument('-p','--platform', metavar='PLATFORM', type=str, help='platform where you can find documents')
args = parser.parse_args()


class DataSource(object):
    def __init__(self):
        self.source_name = args.datasource
        self.corpus_dir = args.corpus

    def importSource(self, *args):
        raise 'Must be implemented in child class'

    def echoData(self):
        for name_id, opinion_txt in annotator.annotator(self.files).items():
            path='{}/{}'.format(self.corpus_dir, name_id)
            with open(path, 'r+') as f:
                f.seek(0,2)
                f.write('\n{}'.format(json.dumps(opinion_txt)))

    def tagData(self):
        n = nerd.NERD('nerd.eurecom.fr', s.nerd_api_key)
        time_out = 30 
        for base_name, text in self.files:
            path='{}/{}'.format(self.corpus_dir, base_name)
            with open(path, 'r+') as f:
                lines = f.readlines()
                print(len(lines))
                #In case of multi lines on one file
                '''single_line = '\t'.join([line.strip() for line in lines])
                f.write(single_line)'''
                data = n.extract(text, 'combined', time_out)
                f.seek(0,2)
                f.write('\n{}'.format(data))

    def _setInOneLine(self, lines):
        if len(lines) == 1:
            return None
        elif ((len(lines)) > 1):
            return 
        else:
            raise 'Probably it is not a list'
    

class SolrSource(DataSource):
    def __init__(self):
        super(SolrSource, self).__init__()
        self._solr =pysolr.Solr(s.solr_url, timeout=20)
        

    def importSource(self, writefile= True):
        platform = args.platform
        request = 'platformID:%s AND site_name:"%s"' % (args.platform, args.site_name)
        filter_query = {'fq':'naked_texte:[* TO *]'}
        numFound = self._findNumFound(request, filter_query)
        print(numFound)
        stop = numFound
        #stop = 1 # for testing
        step = 50
        files = list()
        # Get results by data bundle
        for i in range(0, stop, step):
            results = self._solr.search(request, **{'rows':step, 'start':i, 'sort':'id DESC'})
            files.extend(self._setFiles(results))
        self.__setattr__('files', files) 

    def _findNumFound(self, request, filter_query={'rows' : '0'}):
        results = self._solr.search(request, **filter_query)
        return results.hits

    def _setFiles(self, results):
        list_files = []
        if not os.path.exists(self.corpus_dir):
            os.makedirs(self.corpus_dir)
        for result in results:
            name_id = ''.join((result['id'].replace('http://','').replace('/','_'), '.txt'))
            path='{}/{}'.format(self.corpus_dir, name_id)
            if not os.path.exists('./{}'.format(path)):
                mode = 'a'
            else:
                mode = 'w'
            list_files.append((name_id, result['naked_texte']))
            with open(path, mode) as f:
                print(type(result['naked_text']))
                f.write(result['naked_texte'])
                #f.write(self._getInOneLine(result['naked_texte']))
        return list_files #, list_files_result


class TextSource(DataSource):
    def __init__(self):
        super(TextSource, self).__init__()

    def importSource(self):
        files = list()
        for file_name in os.listdir(self.corpus_dir):
            path='{}/{}'.format(self.corpus_dir, file_name)
            with open(path, 'r+') as f:
                lines = f.readlines() 
                if len(lines) == 1:
                    text = lines[0]
                else:
                    text = '\t'.join([line.strip() for line in lines])
                    f.write(text)
                files.append((file_name, text))
        self.__setattr__('files', files) 


def factory():
    if args.datasource == 'solr':
        return SolrSource()
    elif args.datasource == 'text':
        return TextSource()


if __name__ == '__main__':
    data_obj = factory() 
    data_obj.importSource()
    #data_obj.tagData() # Added Tag
   # data.echoData() # Added analysis sentiment
    data_obj.echoData()

