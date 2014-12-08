import re
import yaml
import os
import speaker
import mpd
from mic import Mic
import time
import bible_search
import bible_lists
import sys
import select

WORDS = ["READ", "BIBLE"]

config = open("config.txt")
lang = config.read()
lang = lang.strip()
config.close()

profile = yaml.safe_load(open("profile.yml", "r"))
mic = Mic(speaker.newSpeaker(), "languagemodel_command.lm", "dictionary_command.dic", "languagemodel_persona.lm", "dictionary_persona.dic")
mic.say("Welcome to Fig, the interactive Bible.")
 

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
        self.bookName = ""
        self.chapNum = ""
        self.client = mpd.MPDClient()
        self.client.timeout = None
        self.client.idletimeout= None
        self.client.connect("localhost", 6600)
        #dictionary = bible_lists.dictList[lang]
        #self.mic = Mic(mic.speaker, "languagemodel_bible.lm", dictionary[0], "languagemodel_persona.lm", "dictionary_persona.dic", lmd_music="languagemodel_playback.lm", dictd_music=dictionary[1], lmd_num="languagemodel_num.lm", dictd_num=dictionary[2])
        if "INDONESIAN" in lang:
            self.mic = Mic(mic.speaker, "languagemodel_bible.lm", "dictionary_indo.dic", "languagemodel_persona.lm", "dictionary_persona.dic", lmd_music="languagemodel_playback.lm", dictd_music="dictionary_playindo.dic", lmd_num="languagemodel_num.lm", dictd_num="dictionary_numindo.dic")
            self.say = self.sayInd
        else:
            self.mic = Mic(mic.speaker, "languagemodel_bible.lm", "dictionary_bible.dic", "languagemodel_persona.lm", "dictionary_persona.dic", lmd_music="languagemodel_playback.lm", dictd_music="dictionary_playback.dic", lmd_num="languagemodel_num.lm", dictd_num="dictionary_num.dic")
            self.say = self.sayEng
    
    def sayEng(self, word):
        self.mic.say(bible_lists.utterances[word])
        
    def sayInd(self, word):
        filename = "audio/" + word + "_indo.wav"
        #filename = "hi.wav"
        os.system("aplay -D hw:1,0 " + filename)
        
#    def say(self, word, lang):
#        filename = "audio/" + lang + "/" + word + ".wav"
#        os.system("aplay -D hw:1,0 " + filename)
    
    def lookupBible(self, lang):
        badInput = True
        while badInput:
            badInput = False
            self.say("book")
            book = self.mic.activeListen()
            self.say("chapter")
            chap = self.mic.activeListen(NUMBER=True)

            if book == "" or chap == "":
                badInput = True
                self.say("pardon")
            else:
                book, chap, audio = bible_search.bible_query(book, chap, lang)
                if audio == "":
                    badInput = True
                    self.say("repeat")
                else:
                    self.mic.say("Opening " + book + " " + chap)
                    self.say("prompt")
                    input = self.mic.activeListen(MUSIC=True)
                    if "CANCEL" in input:
                        badInput = True
                        self.say("cancel")
                    else:
                        return book, chap, audio

    def nextBook(self, book):
        return bible_lists.nextList[book]   
    
    def handleForever(self):
        
        self.say("opening")

        try:
            self.client.clear()
        except mpd.ConnectionError:
            self.client.disconnect()
            self.client.connect("localhost", 6600)
            self.client.clear()
 
        self.client.add("file:///home/pi/jasper/client/BibleReader/bible.mp3")
        self.client.play()
	
        while True:
            inputFlag = False
            finishedFlag = False
            
            try:
                i, o, e = select.select([sys.stdin], [], [], 0)
                for s in i:
                    if s == sys.stdin:
                        input = sys.stdin.read(1)
                        inputFlag = True
                #if not inputFlag:
                #    threshold, transcribed = self.mic.passiveListen(self.persona)
		threshold = False
                stat = self.client.status()
                if 'songid' not in stat:
                    finishedFlag = True 
            except:
                continue

            if inputFlag or threshold:
                inputFlag = False
                try:
                    self.client.pause(1)
                except mpd.ConnectionError:
                    self.client.disconnect()
                    self.client.connect("localhost", 6600)
                    self.client.pause(1)
        
                input = self.mic.activeListen(MUSIC=True)
                if "CLOSE BIBLE" in input:
                    self.say("closing")
                    self.client.stop()
                    self.client.close()
                    self.client.disconnect()
                    return
                elif "STOP" in input:
                    self.say("stop")
                    self.client.stop()
                elif "PAUSE" in input:
                    self.say("pause")
                elif "CONTINUE" in input:
                    self.say("continuing")
                    self.client.pause(0)
                elif "OPEN" in input:
                    self.bookName, self.chapNum, audio = self.lookupBible(self.lang)
                    self.say("opening") #choose another book
                    
                    try:
                        self.client.clear()
                    except mpd.ConnectionError:
                        self.client.disconnect()
                        self.client.connect("localhost", 6600)
                        self.client.clear()

                    bible_search.audio_download(audio)
                    self.client.add("file:///home/pi/jasper/client/BibleReader/bible.mp3")
                    self.client.play()
                else:
                    self.say("pardon")
                    self.client.play()

            if finishedFlag:
                finishedFlag = False
                self.mic.say("To continue to next chapter, say continue")
                self.mic.say("Otherwise, say close")
                input = self.mic.activeListen(MUSIC=True)
                
                if "CONTINUE" in input:
                    nextChap = str(int(self.chapNum) + 1)
                    self.bookName, self.chapNum, audio = bible_search.bible_query(self.bookName, nextChap, self.lang)
                    if audio == "":
                        #go to next book
                        self.bookName = self.nextBook(self.bookName)
                        nextChap = "1"
                        self.bookName, self.chapNum, audio = bible_search.bible_query(self.bookName, nextChap, self.lang)
                    self.say("opening") #choose another book
                    
                    try:
                        self.client.clear()
                    except mpd.ConnectionError:
                        self.client.disconnect()
                        self.client.connect("localhost", 6600)
                        self.client.clear()

                    bible_search.audio_download(audio)
                    self.client.add("file:///home/pi/jasper/client/BibleReader/bible.mp3")
                    self.client.play()
                else:
                    self.say("closing")
                    try:
                        self.client.close()
                        self.client.disconnect()
                    except mpd.connectionError:
                        self.client.disconnect()
                    
                    return


commandList = ["Read bible", "List books", "Recommend book", "Change language", "Close"]

while True:
    mic.say("How can I be of service?")
    time.sleep(0.1)
    command = mic.activeListen()
    if "COMMAND" in command:
        mic.say("Available commands are")
        for c in commandList:
            mic.say(c)
    elif "CHANGE LANGUAGE" in command:
        mic.say("Please choose a language")
        lang = mic.activeListen()
        mic.say("Language changed to " + lang)
    elif "LIST BOOK" in command:
        mic.say("Available books are Genesis ... Exodus ... Leviticus") #example, needs revision
    elif "RECOMMEND BOOK" in command:
        mic.say("I recommend reading John 3")
        mic.say("Is that okay?")
        ans = mic.activeListen()
        if "YES" in ans:
            book, chap, audio = bible_search.bible_query("JOHN", "3", lang)
            mic.say("Opening John 3")
            bible_search.audio_download(audio)
            bible = BibleReader("JASPER", mic, lang) 
            bible.handleForever()
    elif "READ BIBLE" in command:
        bible = BibleReader("JASPER", mic, lang)
        bible.bookName, bible.chapNum, audio = bible.lookupBible(lang)
        bible_search.audio_download(audio)
        bible.handleForever()
    elif "CLOSE" in command:
        mic.say("Thank you for using Fig")
        break
    else:
        mic.say("Pardon?")

config = open("config.txt", "w")
config.write(lang)
config.close()
