#!/usr/bin/env python
# coding=utf-8
"""
apertium_translate.py - Phenny Translation Module
"""

import re, urllib.request, json
import web
from tools import GrumbleError

headers = [(
    'User-Agent', 'Mozilla/5.0' + 
    '(X11; U; Linux i686)' + 
    'Gecko/20071127 Firefox/2.0.0.11'
)]

APIerrorData = 'Sorry, the apertium API did not return any data ☹'
APIerrorHttp = 'Sorry, the apertium API gave HTTP error %s: %s ☹'

def translate(translate_me, input_lang, output_lang='en'): 
    opener = urllib.request.build_opener()
    opener.addheaders = headers

    input_lang, output_lang = web.quote(input_lang), web.quote(output_lang)
    translate_me = web.quote(translate_me)

    response = opener.open('http://api.apertium.org/json/translate?q='+translate_me+'&langpair='+input_lang+"|"+output_lang).read()

    responseArray = json.loads(response.decode('utf-8'))
    if int(responseArray['responseStatus']) != 200:
        raise GrumbleError(APIerrorHttp % (responseArray['responseStatus'], responseArray['responseDetails']))
    if responseArray['responseData']['translatedText'] == []:
        raise GrumbleError(APIerrorData)

    translated_text = responseArray['responseData']['translatedText']
    return translated_text


def apertium_translate(phenny, input): 
    """Translates a phrase using the apertium API"""
    line = input.group(2)
    if not line:
        raise GrumbleError("Need something to translate!")
    #line = line.encode('utf-8')

    pairs = []
    guidelines = line.split('|')
    if len(guidelines) > 1:
        for guideline in guidelines[1:]:
            #phenny.say(guideline)
            pairs.append(guideline.strip().split('-'))
    guidelines = guidelines[0]
    #phenny.say(str(guidelines))
    stuff = re.search('(.*) ([a-z]+-[a-z]+)', guidelines)
    #phenny.say(str(stuff.groups()))
    pairs.insert(0, stuff.group(2).split('-'))
    translate_me = stuff.group(1)
    #phenny.say(str(pairs))

    #output_lang = line.split(' ')[-1]
    #input_lang = line.split(' ')[-2]
    #translate_me = ' '.join(line.split(' ')[:-2])

    if (len(translate_me) > 350) and (not input.admin): 
        raise GrumbleError('Phrase must be under 350 characters.')

    msg = translate_me
    finalmsg = False
    translated = ""
    for (input_lang, output_lang) in pairs:
        if input_lang == output_lang: 
            raise GrumbleError('Stop trying to confuse me!  Pick different languages ;)')
        msg = translate(msg, input_lang, output_lang)
        if not msg:
            raise GrumbleError('The %s to %s translation failed, sorry!' % (input_lang, output_lang))
        msg = web.decode(msg) # msg.replace('&#39;', "'")
        this_translated = "(%s-%s) %s" % (input_lang, output_lang, msg)
        translated = msg

    #if not finalmsg:
    #    finalmsg = translated
    #phenny.reply(finalmsg)
    phenny.reply(translated)

def apertium_listlangs(phenny, input):
    """Lists languages available for translation from/to"""

    opener = urllib.request.build_opener()
    opener.addheaders = headers

    response = opener.open('http://api.apertium.org/json/listPairs').read()

    langs = json.loads(response.decode('utf-8'))
    if int(langs['responseStatus']) != 200:
        raise GrumbleError(APIerrorHttp % (langs['responseStatus'], langs['responseDetails']))
    if langs['responseData'] == []:
        raise GrumbleError(APIerrorData)

    outlangs = []
    #phenny.say(str(langs))
    for pair in langs['responseData']:
        if pair['sourceLanguage'] not in outlangs:
            outlangs.append(pair['sourceLanguage'])
        if pair['targetLanguage'] not in outlangs:
            outlangs.append(pair['targetLanguage'])
    #phenny.say(str(outlangs))

    extra = "; more info: .listpairs lg"

    first=True
    allLangs = ""
    for lang in outlangs:
        if not first:
            allLangs+=", "
        else:
            first=False
        allLangs += lang
    phenny.say(allLangs + extra)
  

def apertium_listpairs(phenny, input): 
    """Lists translation pairs available to apertium translation"""
    lang = input.group(2)

    opener = urllib.request.build_opener()
    opener.addheaders = headers

    response = opener.open('http://api.apertium.org/json/listPairs').read()

    langs = json.loads(response.decode('utf-8'))

    langs = json.loads(response.decode('utf-8'))
    if langs['responseData'] is []:
        raise GrumbleError(APIerrorData)
    if int(langs['responseStatus']) != 200:
        raise GrumbleError(APIerrorHttp % (langs['responseStatus'], langs['responseDetails']))

    if not lang:
        allpairs=""
        first=True
        for pair in langs['responseData']:
            if not first:
                allpairs+=","
            else:
                first=False
            allpairs+="%s→%s" % (pair['sourceLanguage'], pair['targetLanguage'])
        phenny.say(allpairs)
    else:
        toLang = []
        fromLang = []
        for pair in langs['responseData']:
            if pair['sourceLanguage'] == lang:
                fromLang.append(pair['targetLanguage'])
            if pair['targetLanguage'] == lang:
                toLang.append(pair['sourceLanguage'])
        first=True
        froms = ""
        for lg in fromLang:
            if not first:
                froms += ", "
            else:
                first = False
            froms += lg
        first = True
        tos = ""
        for lg in toLang:
            if not first:
                tos += ", "
            else:
                first = False
            tos += lg
        #finals = froms + (" → %s → " % lang) + tos
        finals = tos + (" → %s → " % lang) + froms

        phenny.say(finals)

apertium_listpairs.name = 'listpairs'
apertium_listpairs.commands = ['listpairs']
apertium_listpairs.example = '.listpairs ca'
apertium_listpairs.priority = 'low'

apertium_listlangs.name = 'listlangs'
apertium_listlangs.commands = ['listlangs']
apertium_listlangs.example = '.listlangs'
apertium_listlangs.priority = 'low'

apertium_translate.name = 't'
apertium_translate.commands = ['t']
apertium_translate.example = '.t I like pie en-es'
apertium_translate.priority = 'high'