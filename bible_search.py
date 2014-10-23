# -*- coding: utf-8 -*-
"""
Created on Fri Oct 03 14:10:58 2014

@author: dlieviant
"""

import urllib2
import bible_lists

def get_collection(book_id):
    if book_id in bible_lists.ntList:
        dam_id = "ENGESVN2DA"
    else:
        dam_id = "ENGESVO2DA"
    return dam_id

def get_book_id(book):
    book = book.replace(" ", "")
    return bible_lists.bookList[book]

def bible_query(book, chapter):

    API_KEY = "fd82d19821647fa4829c7ca160b82e6f"
    book_id = get_book_id(book)
    dam_id = get_collection(book_id)
    request = "http://dbt.io/audio/path?key="+API_KEY+"&dam_id="+dam_id+"&book_id="+book_id+"&chapter_id="+chapter+"&v=2"
    
    response = urllib2.urlopen(request)
    
    html = response.read().split('","')
    audiopath = "http://cloud.faithcomesbyhearing.com/mp3audiobibles2/"
    print len(html)
    for fields in html:    
    #    print fields
        item = fields.split(":")
        if "path" in item[0]:
            path = item[1].replace("\/", "/")
            path = path.split('"')
            path = path[1]
    #        print path
            audiopath = audiopath+path
            print audiopath
    
    audio = urllib2.urlopen(audiopath)
    bible = open("gen3.mp3", "wb")
    bible.write(audio.read())
    bible.close()
    
bible_query("SECOND CORINTHIANS", "3")