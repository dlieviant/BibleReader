import re
import yaml
import os
import "../speaker"
import urllib2
import mpd
from "../mic" import Mic
import time
import bible_search
import getch
import sys
import select

#WORDS = ["READ","FIRST", "SECOND", "THIRD", "BIBLE"
#	 "GENESIS", "EXODUS", "LEVITICUS", "NUMBERS", "DEUTERONOMY", "JOSHUA",
#	 "JUDGES", "RUTH", "SAMUEL", "KINGS", "CHRONICLES", "EZRA", "NEHEMIAH",
#	 "ESTHER", "JOB", "PSALMS", "PROVERBS", "ECCLESIASTES", "SONG",
#	 "SOLOMON", "ISAIAH", "JEREMIAH", "LAMENTATIONS", "EZEKIEL", "DANIEL",
#	 "HOSEA", "JOEL", "AMOS", "OBADIAH", "JONAH", "MICAH", "NAHUM",
#	 "HABAKKUK", "ZEPHANIAH", "HAGGAI", "ZECHARIAH", "MALACHI",
#	 "MATTHEW", "MARK", "LUKE", "JOHN", "ACTS", "ROMANS", "CORINTHIANS", 
#	 "GALATIANS", "EPHESIANS", "PHILIPPIANS", "COLOSSIANS", "THESSALONIANS",
#	 "TIMOTHY", "TITUS", "PHILEMON", "HEBREWS", "JAMES", "PETER", "JOHN",
#	 "JUDE", "REVELATIONS"]

WORDS = ["READ", "BIBLE"]

test_uri = "http://cloud.faithcomesbyhearing.com/mp3audiobibles2/ENGESVO2DA/A01___01_Genesis_____ENGESVO2DA.mp3"

profile = yaml.safe_load(open("profile.yml", "r"))
mic = Mic(speaker.newSpeaker(), "languagemodel_bible.lm", "dictionary_bible.dic", "languagemodel_persona.lm", "dictionary_persona.dic", lmd_music="languagemodel_playback.lm", dictd_music="dictionary_playback.dic", lmd_num="languagemodel_num.lm", dictd_num="dictionary_num.dic")
    
 

def isValid(text):
    """
        Returns True if the input is related to new testament

        Arguments:
        text -- user-input, typically transcribed speech
    """
    #return bool(re.search(r'\b(genesis|exodus|leviticus|numbers|deuteronomy|joshua|judges|ruth|samuel|kings|chronicles|ezra|nehemiah|esther|job|psalms|proverbs|ecclesiates|song of solomon|isaiah|jeremiah|lamentations|ezekiel|daniel|hosea|joel|amos|obadiah|jonah|micah|nahum|habakkuk|zephaniah|haggai|zechariah|malachi|matthew|mark|luke|john|acts|romans|corinthians|galatians|ephesians|philippians|colossians|thessalonians|timothy|titus|philemon|hebrews|james|john|jude|revelations)\b', text, re.IGNORECASE))

    return bool(re.search(r'\b(read|bible)\b', text, re.IGNORECASE))

  
class BibleReader:
    
    def __init__(self, PERSONA, mic, lang):
        self.persona = PERSONA
        self.client = mpd.MPDClient()
        self.client.timeout = None
        self.client.idletimeout= None
        self.client.connect("localhost", 6600)
        self.mic = mic
        #if "INDONESIAN" in lang:
        #    self.mic = Mic(mic.speaker, "languagemodel_indo.lm", "dictionary_indo.dic", "languagemodel_persona.lm", "dictionary_persona.dic")
        #else:
        #    self.mic = Mic(mic.speaker, "languagemodel_bible.lm", "dictionary_bible.dic", "languagemodel_persona.lm", "dictionary_persona.dic")
    

    def handleForever(self):
        badInput = True
        while badInput:
            badInput = False
            self.mic.say("Please specify the book to read.")
            book = self.mic.activeListen()
            self.mic.say("Please choose the chapter.")
            chap = self.mic.activeListen(NUMBER=True)
            audio = bible_search.bible_query(book, chap)
            if book == "" or chap == "":
                badInput = True
                self.mic.say("I am sorry, I did not catch that. Please repeat.")
            else:
                audio = bible_search.bible_query(book, chap)
                if audio == "":
                    badInput = True
                    self.mic.say("Cannot find chapter. Please repeat.")

        self.mic.say("Opening the Bible. Please wait.")

        self.client.clear()
        #self.client.add(audio)
        self.client.add("file:///home/pi/jasper/client/audio/bible.mp3")
        self.client.play()
	
        while True:
            '''
            input = self.mic.activeListen()
            if input:
                self.mic.say("Input detected.")
            '''
            inputFlag = False
            try:
		#char = getch.getch()
                print "key input"
                i, o, e = select.select([sys.stdin], [], [], 0)
                for s in i:
                    if s == sys.stdin:
                        input = sys.stdin.read(1)
                        inputFlag = True
                print "voice input"
                threshold, transcribed = self.mic.passiveListen(self.persona)
            except:
                continue

            #if threshold or char == 'j':
            if threshold or inputFlag:
                inputFlag = False
		#if char == 'j':
                #    print "manual persona activation"
                try:
                    self.client.pause(1)
                except mpd.ConnectionError:
                    self.client.disconnect()
                    self.client.connect("localhost", 6600)
                    self.client.pause(1)
        
                input = self.mic.activeListen(MUSIC=True)
                if "CLOSE BIBLE" in input:
                    self.mic.say("Closing the Bible")
                    self.client.stop()
                    self.client.close()
                    self.client.disconnect()
                    return
                elif "STOP" in input:
                    self.mic.say("Stopping reading.")
                    self.client.stop()
                elif "PAUSE" in input:
                    self.mic.say("Pausing reading.")
                elif "CONTINUE" in input:
                    self.mic.say("Continue reading.")
                    self.client.pause(0)
                elif "OPEN" in input:
                    self.mic.say("Please specify the book to read.")
                    book = self.mic.activeListen()
                    self.mic.say("Please choose the chapter.")
                    chap = self.mic.activeListen(NUMBER=True)
                    audio = bible_search.bible_query(book, chap)
                    self.mic.say("Opening the Bible. Please wait.") #choose another book
                    self.client.clear()
                    self.client.add("file:///home/pi/jasper/client/audio/bible.mp3")
                    self.client.play()
                else:
                    self.mic.say("Pardon?")
                    self.client.play()
         

mic.say("Please choose a language.")
mic.say("Available languages are: English ... Indonesian")
lang = mic.activeListen()

bible = BibleReader("JASPER", mic, "ENGLISH") #lang instead of "ENGLISH"
bible.handleForever()
