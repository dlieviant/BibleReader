import random
import re
import os
import urllib2
import mpd
from mic import Mic

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
    for i in range(1000):
        for j in range(100):
            i+j

    bible = BibleReader("JASPER", mic, lang)
    bible.handleForever()
    
    #audio = urllib2.urlopen("http://cloud.faithcomesbyhearing.com/mp3audiobibles2/ENGESVO2DA/A01___01_Genesis_____ENGESVO2DA.mp3")
    #bible = open("bible.mp3", "wb")
    #bible.write(audio.read())
    #bible.close()

    #os.system("aplay -D hw:1,0 bible.mp3")
    
    #play_audio()   

def isValid(text):
    """
        Returns True if the input is related to new testament

        Arguments:
        text -- user-input, typically transcribed speech
    """
    #return bool(re.search(r'\b(genesis|exodus|leviticus|numbers|deuteronomy|joshua|judges|ruth|samuel|kings|chronicles|ezra|nehemiah|esther|job|psalms|proverbs|ecclesiates|song of solomon|isaiah|jeremiah|lamentations|ezekiel|daniel|hosea|joel|amos|obadiah|jonah|micah|nahum|habakkuk|zephaniah|haggai|zechariah|malachi|matthew|mark|luke|john|acts|romans|corinthians|galatians|ephesians|philippians|colossians|thessalonians|timothy|titus|philemon|hebrews|james|john|jude|revelations)\b', text, re.IGNORECASE))

    return bool(re.search(r'\b(read|bible)\b', text, re.IGNORECASE))

#def play_audio():
#    client = mpd.MPDClient()
#    client.timeout = None
#    client.idletimeout= None
#    client.connect("localhost", 6600)
#    client.clear()
#    #client.add("local: bible.mp3")
#    client.play()
#    client.close()
#    client.disconnect()
  
class BibleReader:
    
    def __init__(self, PERSONA, mic, lang):
        self.persona = PERSONA
        if "INDONESIAN" in lang:
            self.mic = Mic(mic.speaker, "languagemodel_indo.lm", "dictionary_indo.dic", "languagemodel_persona.lm", "dictionary_persona.dic")
        else:
            self.mic = Mic(mic.speaker, "languagemodel_bible.lm", "dictionary_bible.dic", "languagemodel_persona.lm", "dictionary_persona.dic")
 

    def handleForever(self):
        self.mic.say("Please specify the verse to read.")
        '''
	  input = self.mic.activeListen()
	  if "close bible" in input.lower():
		self.mic.say("Closing the Bible")
		return
        ''' 
	
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
        
                input = self.mic.activeListen()
                if "CLOSE BIBLE" in input:
                    self.mic.say("Closing the Bible")
                    return
                elif input:
                    self.mic.say("Opening the Bible. Please wait.")
                else:
                    self.mic.say("Pardon?")
         

