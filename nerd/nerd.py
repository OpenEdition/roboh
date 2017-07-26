"""
    nerd -   A python library which provides an interface to NERD
                    http://nerd.eurecom.fr
"""

__author__ = "morban"
__email__ = "mathieu.orban@openedition.org"



import pycurl
import tempfile
import json
from io import BytesIO
import os

class LanguageException(Exception):
    pass

class NERD(object):
    """Connection to the NERD service.
    """
    def __init__(self, endpoint, action, user_agent=None):
        if user_agent is None:
            user_agent = "NERD python 3 library 0.5"
        self._headers = [
            "content-type: multipart/form-data",
            "accept: application/json",
            "user-agent: {}".format(user_agent)
            ]
        self.url = endpoint + "".join(("/service/", action))

    def query(self, text, debug=True):
        with open('result.json', 'w') as fp:
            json.dump({"text":text, "onlyNER":True}, fp)
        c, buffer = self.init_curl('result.json', debug)
        response = self.getResponse(c, buffer)
        return json.loads(response)

    def init_curl(self, filename, debug=True):
        c = pycurl.Curl()
        buffer = BytesIO()
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.POST, 1)
        c.setopt(c.HTTPHEADER, self._headers)
        c.setopt(c.URL, self.url)
        if debug:
            c.setopt(pycurl.VERBOSE, 1)
            c.setopt(pycurl.DEBUGFUNCTION, test)
        send = [("query", (c.FORM_FILE, str(filename)))]
        c.setopt(c.HTTPPOST, send) 
        return c, buffer

    def getResponse(self, c, buffer):
        """Extract named entities from document with 'service'.        
        'service' can be any of the constants defined in this module.
        """

        """ submit document """
        c.perform()
        status = c.getinfo(c.RESPONSE_CODE)
        if status  == 406: 
            raise LanguageException("%d %s" % (status, "This language is not supported by nerd"))
        if status  != 200: 
            raise Exception("%d %s " % (status, "Try to debug..."))
        response = buffer.getvalue().decode('utf-8')
        c.close()
        return response


    def extract(self, data, text):
        str_gap = 0
        for entity in data["entities"]:
            tag_name = "".join(('<', entity['type'], '>', entity['rawName'], '<\\', entity['type'], '>'))
            start = entity["offsetStart"] + str_gap
            end = entity["offsetEnd"] + str_gap
            text = text[:start] + tag_name + text[end:]
            str_gap = str_gap + 2 * len(entity['type']) + 5
        return text

def test(debug_type, debug_msg):
    print("debug(%d): %s" % (debug_type, debug_msg))

