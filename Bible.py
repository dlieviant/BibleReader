import re
import yaml
import os
import speaker
import urllib2
import mpd
from mic import Mic
import time
import bible_search
import bible_lists
import sys
import select

WORDS = ["READ", "BIBLE"]

profile = yaml.safe_load(open("profile.yml", "r"))
mic = Mic(speaker.newSpeaker(), "languagemodel_bible.lm", "dictionary_bible.dic", "languagemodel_persona.lm", "dictionary_persona.dic", lmd_music="languagemodel_playback.lm", dictd_music="dictionary_playback.dic", lmd_num="languagemodel_num.lm", dictd_num="dictionary_num.dic")
    
 

def isValid(text):
    """
        Returns True if the input is related to new testament

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return bool(re.search(r'\b(read|bible)\b', text, re.IGNORECASE))

  
class BibleReader:
    
    def __init__(self, PERSONA, mic, lang):
        self.persona = PERSONA
        self.lang = lang
        self.client = mpd.MPDClient()
        self.client.timeout = None
        self.client.idletimeout= None
        self.client.connect("localhost", 6600)
        if "INDONESIAN" in lang:
            self.mic = Mic(mic.speaker, "languagemodel_indo.lm", "dictionary_indo.dic", "languagemodel_persona.lm", "dictionary_persona.dic", lmd_music="languagemodel_playindo.lm", dictd_music="dictionary_playindo.dic", lmd_num="languagemodel_num.lm", dictd_num="dictionary_numindo.dic")
            self.say = self.sayInd
        else:
            self.mic = mic
            self.say = self.sayEng
    
    def sayEng(self, word):
        self.mic.say(bible_lists.utterances[word])
        
    def sayInd(self, word):
        filename = word + "_indo.wav"
        os.system("aplay -D hw:1,0 " + filename)
    
    def lookupBible(self, lang):
        badInput = True
        while badInput:
            badInput = False
            self.say(self, "book")
            book = self.mic.activeListen()
            self.say(self, "chapter")
            chap = self.mic.activeListen(NUMBER=True)

            if book == "" or chap == "":
                badInput = True
                self.say(self, "pardon")
            else:
                audio = bible_search.bible_query(book, chap, lang)
                if audio == "":
                    badInput = True
                    self.mic.say(self, "repeat")
                else:
                    self.mic.say("Opening" + book + " " + chap)
                    self.say(self, "prompt")
                    input = self.mic.activeListen(MUSIC=True)
                    if "CANCEL" in input:
                        badInput = True
                        self.say(self, "cancel")
                    else:
                        return audio

    def handleForever(self):
        audio = self.lookupBible(self, self.lang)
        
        self.say(self, "opening")
        bible_search.audio_download(audio)

        self.client.clear()
        self.client.add("file:///home/pi/jasper/client/BibleReader/bible.mp3")
        self.client.play()
	
        while True:
            inputFlag = False
            
            try:
                i, o, e = select.select([sys.stdin], [], [], 0)
                for s in i:
                    if s == sys.stdin:
                        input = sys.stdin.read(1)
                        inputFlag = True
                if not inputFlag:
                    threshold, transcribed = self.mic.passiveListen(self.persona)
            except:
                continue

            if threshold or inputFlag:
                inputFlag = False
                try:
                    self.client.pause(1)
                except mpd.ConnectionError:
                    self.client.disconnect()
                    self.client.connect("localhost", 6600)
                    self.client.pause(1)
        
                input = self.mic.activeListen(MUSIC=True)
                if "CLOSE BIBLE" in input:
                    self.say(self, "closing")
                    self.client.stop()
                    self.client.close()
                    self.client.disconnect()
                    return
                elif "STOP" in input:
                    self.say(self, "stop")
                    self.client.stop()
                elif "PAUSE" in input:
                    self.say(self, "pause")
                elif "CONTINUE" in input:
                    self.say(self, "continue")
                    self.client.pause(0)
                elif "OPEN" in input:
                    audio = self.lookupBible(self, self.lang)
                    self.say(self, "opening") #choose another book
                    
                    self.client.clear()
                    bible_search.audio_download(audio)
                    self.client.add("file:///home/pi/jasper/client/BibleReader/bible.mp3")
                    self.client.play()
                else:
                    self.say(self, "pardon")
                    self.client.play()
         

mic.say("Please choose a language.")
mic.say("Available languages are: English ... Indonesian")
lang = mic.activeListen(MUSIC=True)
time.sleep(2)
bible = BibleReader("JASPER", mic, lang) #lang instead of "ENGLISH"
bible.handleForever()
