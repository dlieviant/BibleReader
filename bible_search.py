# -*- coding: utf-8 -*-
"""
Created on Fri Oct 03 14:10:58 2014

@author: dlieviant
"""

import urllib2
import bible_lists

def get_collection(book_id, lang):
    if book_id in bible_lists.ntList:
        id_list = bible_lists.idListNT;
    else:
        id_list = bible_lists.idListOT;    
    return id_list[lang]

def get_book_id(book):
    bookname = book.split()
    book_id_key = ""
    if "FIRST" in bookname[0] or "SECOND" in bookname[0] or "THIRD" in bookname[0]:
        book_id_key = book.replace(" ", "")
    else:
        book_id_key = bookname[0]    
    return book_id_key, bible_lists.bookList[book_id_key]

def get_chap_id(chap):
    chapNums = chap.split()
    chap_id = 0
    for nums in chapNums:
        chap_id = chap_id + int(nums)
    return str(chap_id)

def bible_query(book, chapter, lang):
    API_KEY = "fd82d19821647fa4829c7ca160b82e6f"
    book_name, book_id = get_book_id(book)
    chap_id = get_chap_id(chapter)
    dam_id = get_collection(book_id, lang)
    request = "http://dbt.io/audio/path?key="+API_KEY+"&dam_id="+dam_id+"&book_id="+book_id+"&chapter_id="+chap_id+"&v=2"
    response = urllib2.urlopen(request)
    html = response.read().split('","')
    if len(html) == 1:
        return book_name, chap_id, ""
    audiopath = "http://cloud.faithcomesbyhearing.com/mp3audiobibles2/"
    for fields in html:    
    #    print fields
        item = fields.split(":")
        if "path" in item[0]:
            path = item[1].replace("\/", "/")
            path = path.split('"')
            path = path[1]
    #        print path
            audiopath = audiopath+path
    return book_name, chap_id, audiopath
    
def audio_download(path):    
    audio = urllib2.urlopen(path)
    bible = open("bible.mp3", "wb")
    bible.write(audio.read())
    bible.close()