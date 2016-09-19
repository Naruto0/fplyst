#! /usr/bin/python3
#
# Usage:
#
#   path/to/script$ python3 __main__.py -c <config_file>
#
# Will create 'YYYY_MM_DD_STREAMNAME_PLAYLIST.txt' file
# which will contain currently captured song
#
#   HH:MM    Interpret - Song Name
#
# To capture whole playlist you have to
# make crontab scheldule or widows/mac equivalent.
#
# Crontab job should run every minute
# which is enough to make sure the timing is
# correct.
# You may like to be sure that the files are
# saved at the directory, config file is optional:
#
#   */1 * * * * cd <path to script> && python3 __main__.py [-c myConfig.json]
#
# If you want to make your own config file
# edit the variables which make the _dictionary
# underneath the imports.
# (e.g. _station, _url, _interpret_path,  _song_name_path)
#
# Then run:
#
#   you@host~/.../fplyst$ python3 -i __main__.py
#
# In python prompt you either call method
# without any attributes, which overwrites
# original config file...
# 
#   >>> make_config()
#
# ...or you feed it with a filename,
# which you may than use to import
# config for various stations.
#
#   >>> make_config("myConfig.json")
#
# (json extension is optional)
# 
# If you are familiar enough with xpath syntax,
# it shouldn't be hard for you to easily
# setup html xpaths to interpret and song.
#

import sys
import json
import getopt
import time as _t
from requests import get

with open("requirements.txt", "r") as _req_file:
    _req = _req_file.readlines()    

try:
    from lxml import html
except ImportError:
    if _req:
        print("You have to install modules: ")
        for module in _req:
            print("\t%s"%module)
    else:
        print("Unexpected error")
    sys.exit(2)

_config = {}
_station = 'FAJN_RADIO'
_url = 'http://fajnradio.cz/fajn-radio'
_interpret_path = '//div[@class="playsong"]/a[1]/text()'
_song_name_path = '//div[@class="playsong"]/a[2]/text()'
_current = []

_dictionary = { 'station':_station, 'web_page':_url, \
                'interpret_xpath':_interpret_path,\
                'song_xpath':_song_name_path}

def write_last(song):
    with open('.last.json', 'w') as f:
        json.dump(song, f)

def read_last():
    try:
        with open('.last.json', 'r') as f:
            data = json.load(f)
            return data
    except IOError:
        return []


def write_config(filename=None):
    if filename:
        config_file = filename
    else:
        filename = 'config.json'

    with open(filename, 'w') as f:
        json.dump(_dictionary, f)


def read_config(filename):
    try:
        with open(filename, 'r') as f:
            global _config
            _config = json.load(f)
    except EnvironmentError:
        print('bad config file "%s"'%filename)
        sys.exit(2)

def get_time():
    '''What time it is now?'''
    now = _t.gmtime()
    date = _t.strftime("%Y_%m_%d", now)
    hour_minute = _t.strftime("%H:%M", now)
    return [date, hour_minute]

def save(args):
    '''We are definitely saving this song.'''
    file_name = "%s_%s_PLAYLIST.txt"%(args[3],args[2])
    string = "%s\t%s - %s\n"%(args[4],args[0],args[1])

    with open(file_name, "a") as myfile:
        myfile.write(string)

def record(*args,**kwargs):
    '''Do we really need to save current song?'''
    current = read_last()
    playing = fetch(*args,**kwargs)

    if playing:

        if current != playing[:2]:
            save(playing+get_time())
            write_last(playing[:2])
        else:
            # print("[log-%s]not saving %s - %s"%(get_time()[1],current[0],current[1]))
            pass

def fetch(web_page, interpret_xpath, song_xpath, station):
    '''What are they playing?'''

    try:
        page = get(web_page)
    except ConnectionError:
        print ("No internet connection aviable")
        sys.exit(2)

    tree = html.fromstring(page.content)

    interpret_list = tree.xpath(interpret_xpath)
    song_list = tree.xpath(song_xpath)

    if not interpret_list and not song_list:
        return None
    else:
        return [interpret_list[0], song_list[0], station]

def job(name):
    print(name)
    record()


def main(argv):
    help_string = '''__main__.py -c <config_file.json> \t -or we load default config.json
\t\t\t-h \t\t -help'''
    if argv:
        try:
            opts, args = getopt.getopt(argv,"hc:",["conf="])
        except getopt.GetoptError:
            print(help_string)
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print(help_string)
                sys.exit(2)
            elif opt in('-c','--conf'):
                read_config(arg)
    else:
        print("Loading default config")
        read_config('config.json')

    record(**_config)

if __name__ == '__main__':
    main(sys.argv[1:])