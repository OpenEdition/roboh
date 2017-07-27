#!/usr/bin/env python3

__author__ ='morban'
__email__ = 'mathieu.orban@openedition.org'

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

parser = argparse.ArgumentParser(description='Get texts in Open Edition, saved them and tagged them.')

parser.add_argument('-d','--datasource', metavar='DATASOURCE', type=str, help='source required')
parser.add_argument('-c','--corpus', metavar='MODES', type=str, help='corpus file path')
parser.add_argument('-o','--output', metavar='OUTPUT', nargs='?', const='/tmp', type=str, help='output file path', default='/tmp')
parser.add_argument('-s','--site_name', metavar='SITE', type=str, help='site_name of the journal')
parser.add_argument('-p','--platform', metavar='PLATFORM', type=str, help='platform where you can find documents')
args = parser.parse_args()

##@brief Abstract class to represent data source
#@see SolrSource TextSource
class DataSource(object):
    def __init__(self):
        self.source_name = args.datasource
        self.corpus_dir = args.corpus
        self.output_dir = args.output

    def importSource(self, *args):
        raise 'Must be implemented in child class'

    ##@brief Get text (path initialized in__init__) and   
    # write opinion mining (json list of polarity order sentence by sentence) to the out__files
    def echoData(self):
        for name_id, opinion_txt in annotator.annotator(self.files).items():
            path_out = self._setPath(self.output_dir, name_id)
            with open(path_out, 'r+') as f:
                f.seek(0,2)
                f.write('\n{}'.format(json.dumps(opinion_txt)))

    ##@brief Get text (path initialized in__init__) and   
    # write tagged text (with NERD) to the out_files
    def tagData(self):
        n = nerd.NERD('http://cloud.science-miner.com/nerd', 'disambiguate')
        time_out = 30 
        for name_id, text in self.files:
            path_out = self._setPath(self.output_dir, name_id)
            with open(path_out, 'r+') as f:
                #check only one line
                #lines = f.readlines()
                #print(len(lines))
                data = text
                try:
                    response = n.query(text, debug=False)
                    data = n.extract(response, text)
                except nerd.LanguageException as err:
                    print('This file %s is probably not in english, french or german. Error: %s' % (name_id, err))
                except Exception as err:
                    print('This file %s is occured an Exception error %s' % (name_id, err))
                finally:
                    f.seek(0,2)
                    f.write('\n{}'.format(data))
            print('This file {} was saved with entities tagged when it is possible'.format(name_id))
    
    ##@brief Set a full path
    # @param path_dir  st : directory
    # @param file_name st
    # @return st : the full path
    def _setPath(self, path_dir, file_name):
        return  '{}/{}'.format(path_dir, file_name)


class SolrSource(DataSource):
    def __init__(self):
        super(SolrSource, self).__init__()
        self._solr =pysolr.Solr(s.solr_url, timeout=20)

    ##@brief Import documents from solr, add an attribute 'files' 
    # and write document in two directory
    def importSource(self):
        platform = args.platform
        if platform == 'HO':
            request = 'platformID:"HO" AND siteid:"%s" AND autodetect_lang:fr' % (args.site_name)
        else:
            request = 'platformID:%s AND site_name:"%s" AND autodetect_lang:fr' % (args.platform, args.site_name)
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

    ##@brief Get number of documents for a solr request 
    # @param request  st : solr request
    # @param filter_query  dict : solr filter query dictionnary
    # @return int : number of documents
    def _findNumFound(self, request, filter_query={'rows' : '0'}):
        results = self._solr.search(request, **filter_query)
        return results.hits

    ##@brief Get solr result. Write result in two directory
    # file_in.txt and file_out.txt (which usefull later) 
    # @param results  list : list of solr result (each result is a dict)
    # @return list : list of tuple (file name, full naked_texte)
    def _setFiles(self, results):
        list_files = []
        if not os.path.exists(self.corpus_dir):
            os.makedirs(self.corpus_dir)
        for result in results:
            name_id = ''.join((result['id'].replace('http://','').replace('/','_'), '.txt'))
            path_in = self._setPath(self.corpus_dir, name_id)
            path_out = self._setPath(self.output_dir, name_id)
            if not os.path.exists('./{}'.format(path_in)):
                mode = 'a'
            else:
                mode = 'w'
            list_files.append((name_id, result['naked_texte']))
            with open(path_in, mode) as f_witness, open(path_out, 'w') as f_job:
                f_witness.write(result['naked_texte'])
                f_job.write(result['naked_texte'])
        return list_files #, list_files_result


class TextSource(DataSource):
    def __init__(self):
        super(TextSource, self).__init__()

    ##@brief Import documents from input directory, 
    # add attribute 'files' (list of tuple file name, full naked_text) 
    # and set in one line and write in output diretory
    def importSource(self):
        files = list()
        for file_name in os.listdir(self.corpus_dir):
            path_in = self._setPath(self.corpus_dir, file_name)
            path_out = self._setPath(self.output_dir, file_name)
            with open(path_in, 'r') as f_read, open(path_out, 'w') as f_write:
                lines = f_read.readlines() 
                if len(lines) == 1:
                    text = lines[0]
                else:
                    text = '\t'.join([line.strip() for line in lines])
                f_write.write(text)
                files.append((file_name, text))
        self.__setattr__('files', files) 

##@brief factory function to initialize the right object
def factory():
    if args.datasource == 'solr':
        return SolrSource()
    elif args.datasource == 'text':
        return TextSource()


if __name__ == '__main__':
    data_obj = factory() 
    data_obj.importSource()
    data_obj.tagData() # Added Tag
    data_obj.echoData() # Added analysis sentiment

