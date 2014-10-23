import re
import os
import speaker
import urllib2
import mpd
from mic import Mic
import time
import bible_search

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

def handle(text, mic, profile):
    """
        Responds to user-input, typically speech text, by telling a joke.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone number)
    """

    mic.say("Please choose a language.")
    mic.say("Available languages are: English ... Indonesian")
    lang = mic.activeListen()
    print(lang)
    time.sleep(5)

    bible = BibleReader("JASPER", mic, "ENGLISH") #lang instead of "ENGLISH"
    bible.handleForever()

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
        if "INDONESIAN" in lang:
            self.mic = Mic(mic.speaker, "languagemodel_indo.lm", "dictionary_indo.dic", "languagemodel_persona.lm", "dictionary_persona.dic", lmd_music="languagemodel_playback.lm", dictd_music="dictionary_playback.dic", lmd_num="languagemodel_num.lm", dictd_num="dictionary_num.dic") 
        else:
            self.mic = Mic(mic.speaker, "languagemodel_bible.lm", "dictionary_bible.dic", "languagemodel_persona.lm", "dictionary_persona.dic", lmd_music="languagemodel_playback.lm", dictd_music="dictionary_playback.dic", lmd_num="languagemodel_num.lm", dictd_num="dictionary_num.dic")
 

    def handleForever(self):
        self.mic.say("Please specify the book to read.")
        book = self.mic.activeListen()
        self.mic.say("Please choose the chapter.")
        chap = self.mic.activeListen(NUMBER=True)
        bible_search.bible_query(book, chap)
        self.mic.say("Opening the Bible. Please wait.")

        self.client.clear()
        self.client.add("file:///home/pi/jasper/client/audio/bible.mp3")
        self.client.play()
	
        while True:
            '''
            input = self.mic.activeListen()
            if input:
                self.mic.say("Input detected.")
            '''
            try:
                threshold, transcribed = self.mic.passiveListen(self.persona)
            except:
                continue

            if threshold:
                try:
                    self.client.pause(1)
                except:
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
                    bible_search.bible_query(book, chap)
                    self.mic.say("Opening the Bible. Please wait.") #choose another book
                    self.client.clear()
                    self.client.add("file:///home/pi/jasper/client/audio/bible.mp3")
                    self.client.play()
                else:
                    self.mic.say("Pardon?")
                    self.client.play()
         

