## -*- coding: utf-8 -*-

import sys
import logging
import os
import urllib2
import xmlparse
import re
import codecs
import ScribdDocument

from string import printable

def find(query, start, advanced):
    url = "http://api.scribd.com/api?method=docs.search&api_key=<api_key>&simple=%s&query=%s&num_results=10&num_start=%s" % (str(advanced).lower(), query, start)
    print url + '\n'
    
    proxyHandler = urllib2.ProxyHandler({'http': '208.87.233.150:8081', 'https': '208.87.233.150:8081'})
    opener = urllib2.build_opener(proxyHandler)
    file = opener.open(url)
    #file = urllib2.urlopen(url)
    
    resp = file.read()
    resp = re.sub(r'(\r\n)|[\x0C]', ' ', resp, flags=re.MULTILINE)
    #resp.replace(r'\xFF', ' ')
    #resp = re.sub(r'[\xFF]+', ' ', resp)
    #resp = re.sub('[^{}]+'.format(printable), ' ', resp)

    xmlOutput = open('output.xml', 'w')
    xmlOutput.write(resp)
    xmlOutput.close()

    m = re.search(r'totalResultsAvailable=\"(\d+)\"', resp) 
    result = {}
    result["TotalResultsAvailable"] = int(m.group(1))
    
    m = re.search(r'totalResultsReturned=\"(\d+)\"', resp) 
    result["TotalResultsRetured"] = int(m.group(1))

    xml = xmlparse.parse(resp)

    result["Documents"] = [ScribdDocument.Document(item) for item in xml.get('result_set')]
    
    print result
    return result



def PerformQuery(query, advanced):    
    filename = re.sub(r'[^a-zA-Z0-9_]+', '_', query).strip('_')
    
    docsFile = codecs.open(filename + '.csv', 'w', 'utf-8')
    
    docsFile.write('Title,Document ID,Page Count,Uploader,URL,download_formats,reads,available_on_api\n')
    
    start = 0
    result = find(query, start, advanced)
        
    while start < result["TotalResultsAvailable"]:
        for doc in result["Documents"]:
            docsFile.write(doc.title + ',' + 
                           doc.doc_id + ',' + 
                           doc.page_count + ',' + 
                           doc.uploaded_by + ',' + 
                           'http://www.scribd.com/doc/' + doc.doc_id + ',' +
                           doc.download_formats + ',' +
                           doc.reads + '\n')
        start += result["TotalResultsRetured"]
        result = find(query, start, advanced)
    
    docsFile.close()

PerformQuery('Scissors', False)
