import re
import yaml
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
if "INDONESIAN" in lang:
    mic = Mic(speaker.newSpeaker(), "languagemodel_command.lm", "dictionary_commandindo.dic", "languagemodel_persona.lm", "dictionary_persona.dic")
else:
    mic = Mic(speaker.newSpeaker(), "languagemodel_command.lm", "dictionary_command.dic", "languagemodel_persona.lm", "dictionary_persona.dic")
 

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
        
        dictionary = bible_lists.dictList[lang]
        self.mic = Mic(mic.speaker, "languagemodel_bible.lm", dictionary[0], "languagemodel_persona.lm", "dictionary_persona.dic", lmd_music="languagemodel_playback.lm", dictd_music=dictionary[1], lmd_num="languagemodel_num.lm", dictd_num=dictionary[2])
                
#    def say(self, word, lang):
#        filename = "audio/" + lang + "/" + word + ".wav"
#        os.system("aplay -D hw:1,0 " + filename)
    
    def lookupBible(self, lang):
        badInput = True
        while badInput:
            badInput = False
            self.mic.speak("book", self.lang)
            book = self.mic.activeListen()
            self.mic.speak("chapter", self.lang)
            chap = self.mic.activeListen(NUMBER=True)

            if book == "" or chap == "":
                badInput = True
                self.mic.speak("pardon", self.lang)
            else:
                book, chap, audio = bible_search.bible_query(book, chap, lang)
                if audio == "":
                    badInput = True
                    self.mic.speak("repeat", self.lang)
                else:
                    self.mic.say("Opening " + book + " " + chap)
                    self.mic.speak("confirm", self.lang)
                    input = self.mic.activeListen(MUSIC=True)
                    if "CANCEL" in input:
                        badInput = True
                        self.mic.speak("cancel", self.lang)
                    else:
                        return book, chap, audio

    def nextBook(self, book):
        return bible_lists.nextList[book]   
    
    def handleForever(self):
        
        self.mic.speak("opening", self.lang)

        try:
            self.client.clear()
        except mpd.ConnectionError:
            self.client.disconnect()
            self.client.connect("localhost", 6600)
            self.client.clear()
 
        self.client.add("file:///home/pi/jasper/client/BibleReader/bible.mp3")
        self.client.play()
        isPlaying = True
	
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
                    self.mic.speak("closing", self.lang)
                    self.client.stop()
                    self.client.close()
                    self.client.disconnect()
                    return
                elif "STOP" in input:
                    self.mic.speak("stop", self.lang)
                    self.client.stop()
                    isPlaying = False
                elif "PAUSE" in input:
                    self.mic.speak("pause", self.lang)
                    isPlaying = False
                elif "CONTINUE" in input:
                    self.mic.speak("continuing", self.lang)
                    self.client.pause(0)
                    isPlaying = True
                elif "OPEN" in input:
                    self.bookName, self.chapNum, audio = self.lookupBible(self.lang)
                    self.mic.speak("opening", self.lang) #choose another book
                    
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
                    self.mic.speak("pardon", self.lang)
                    if isPlaying:
                        self.client.play()

            if finishedFlag:
                finishedFlag = False
                self.mic.speak("nextchap", self.lang)
                input = self.mic.activeListen(MUSIC=True)
                
                if "CONTINUE" in input:
                    nextChap = str(int(self.chapNum) + 1)
                    self.bookName, self.chapNum, audio = bible_search.bible_query(self.bookName, nextChap, self.lang)
                    if audio == "":
                        #go to next book
                        self.bookName = self.nextBook(self.bookName)
                        nextChap = "1"
                        self.bookName, self.chapNum, audio = bible_search.bible_query(self.bookName, nextChap, self.lang)
                    self.mic.speak("opening", self.lang) #choose another book
                    
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
                    self.mic.speak("closing", self.lang)
                    try:
                        self.client.close()
                        self.client.disconnect()
                    except mpd.connectionError:
                        self.client.disconnect()
                    
                    return



bible = BibleReader("JASPER", mic, lang) 
mic.speak("welcome", lang)

while True:
    mic.speak("prompt", lang)
    time.sleep(0.1)
    command = mic.activeListen()
    if "COMMAND" in command:
        mic.speak("command", lang)
    elif "CHANGE LANGUAGE" in command:
        mic.speak("changelang", lang)
        lang = mic.activeListen()
        if "INDONESIAN" in lang:
            mic = Mic(mic.speaker, "languagemodel_command.lm", "dictionary_commandindo.dic", "languagemodel_persona.lm", "dictionary_persona.dic")
        else:
            mic = Mic(mic.speaker, "languagemodel_command.lm", "dictionary_command.dic", "languagemodel_persona.lm", "dictionary_persona.dic")
        bible = BibleReader("JASPER", mic, lang)
        mic.speak("langchange", lang)
    elif "LIST BOOK" in command:
        mic.speak("listbook", lang) #example, needs revision
    elif "RECOMMEND BOOK" in command:
        mic.speak("recommend", lang)
        ans = mic.activeListen()
        if "YES" in ans:
            book, chap, audio = bible_search.bible_query("JOHN", "3", lang)
            mic.say("Opening John 3")
            bible_search.audio_download(audio)
            bible.handleForever()
    elif "READ BIBLE" in command:
        bible.bookName, bible.chapNum, audio = bible.lookupBible(lang)
        bible_search.audio_download(audio)
        bible.handleForever()
    elif "CLOSE" in command:
        mic.speak("end", lang)
        break
    else:
        mic.speak("pardon", lang)

config = open("config.txt", "w")
config.write(lang)
config.close()
