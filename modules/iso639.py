#!/usr/bin/python3
"""
iso639.py - ISO codes module
author: mutantmonkey <mutantmonkey@mutantmonkey.in>
"""

import random
from modules import ethnologue
from lxml import html, etree
import web
import os
import threading
import re
import logging

logger = logging.getLogger('phenny')

template = "{} = {}"

def flatten(s):
    #match against accented characters
    my_copy = str(s)
    flatten_mapping = {
        'a': 'áäâ',
        'e': 'éè',
        'i': 'íî',
        'o': 'óö',
        'u': 'ùüú',
        'n': 'ñ',
        "'": '’'
    }
    for i in my_copy:
        for k, v in flatten_mapping.items():
            if i in v:
                my_copy = my_copy.replace(i, k)

    return my_copy


def iso639(phenny, input):
    """.iso639 <lg> | .iso639 <Language> - Search ISO 639-1, -2 and -3 for a language code."""
    response = ""
    thisCode = str(input.group(1)).lower()
    if thisCode == "None":
        thisCode = random.choice(list(phenny.iso_data.keys()))
        #ISOcodes[random.randint(0,len(ISOcodes)-1)]
        #random.choice(ISOcodes)
    else:
        if len(thisCode) > 3:      # so that we don't get e.g. 'a'
            for oneCode, oneLang in phenny.iso_data.items():
                if thisCode in flatten(oneLang.lower()):
                    if response != "":
                        response += ", " + template.format(oneCode, oneLang)
                    else:
                        response = template.format(oneCode, oneLang)
                    #phenny.say("%s %s %s" % (oneCode, oneLang.lower(), thisCode.lower()))
        elif thisCode in phenny.iso_data:
            altCode = None
            if len(thisCode) == 2 and thisCode in phenny.iso_conversion_data:
                altCode = phenny.iso_conversion_data[thisCode]
            elif len(thisCode) == 3:
                for iso1, iso3 in phenny.iso_conversion_data.items():
                    if thisCode == iso3:
                        altCode = iso1
                        break
            response = template.format(thisCode + (", " + altCode if altCode else ""), phenny.iso_data[thisCode])

    if response == "":
        response = "Sorry, %s not found" % thisCode

    phenny.say(response)

def refresh_database(phenny, raw=None):
    if raw.admin or raw is None:
        ethnologue.write_ethnologue_codes(phenny)
        phenny.say('ISO code database successfully written')
    else:
        phenny.say('Only admins can execute that command!')

def thread_check(phenny, raw):
    for t in threading.enumerate():
        if t.name == refresh_database.name:
            phenny.say('An ISO code updating thread is currently running')
            break
    else:
        phenny.say('No ISO code updating thread running')

def setup(phenny):
    # populate ethnologue codes
    ethnologue.setup(phenny)

iso639.name = 'iso639'
#iso639.rule = (['iso639'], r'(.*)')
iso639.commands = ['iso639']
iso639.example = '.iso639 khk'
iso639.priority = 'low'

refresh_database.name = 'refresh_iso_database'
refresh_database.commands = ['isodb update']
refresh_database.thread = True

thread_check.name = 'iso_thread_check'
thread_check.commands = ['isodb status']

if __name__ == '__main__':
    print(__doc__.strip())
