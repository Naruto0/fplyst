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
# TODO: include selenium to support javascript generated <html>

import sys
import json
import getopt
import time as _t
from requests import get
from requests.exceptions import ConnectionError, SSLError

with open("requirements.txt", "r") as _req_file:
    _req = _req_file.readlines()    

try:
    from lxml import html
    from selenium import webdriver
    from pyvirtualdisplay import Display
except ImportError:
    if _req:
        print("You have to install modules: ")
        for module in _req:
            print("\t%s"%module)
    else:
        print("Unexpected error")
    sys.exit(2)

_config = {}
_selenium = False

_station = 'EVROPA2'
_url = 'https://www.evropa2.cz'
_interpret_path = '//h3[@class="author"]/text()'
_song_name_path = '//h4[@class="song"]/text()'

_dictionary = { 'station':_station, 'web_page':_url, \
                'interpret_xpath':_interpret_path,\
                'song_xpath':_song_name_path}

def write_last(song):
    song_info = song[:2]
    station = song[2]
    last_name = ".last_on_%s.json"%(station)
    with open(last_name, 'w') as f:
        json.dump(song, f)

def read_last(station=None):
    try:
        last_name = ".last_on_%s.json"%(station)
        with open(last_name, 'r') as f:
            data = json.load(f)
            return data
    except IOError:
        return []


def make_config(filename=None):
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
    now = _t.localtime()
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
    playing = fetch(*args,**kwargs)
    print(playing)

    current = read_last(playing[2])

    if playing:

        if current != playing:
            save(playing+get_time())
            write_last(playing)
        else:
            # print("[log-%s]not saving %s - %s"%(get_time()[1],current[0],current[1]))
            pass

def fetch(web_page, interpret_xpath, song_xpath, station):
    '''What are they playing?'''
    global _selenium

    if _selenium:
        
        browser = webdriver.Firefox()
        browser.get(web_page)

        interpret = browser.find_element_by_xpath(interpret_xpath).text
        song = browser.find_element_by_xpath(song_xpath).text

        if interpret and song:
            return [interpret, song, station]
        else:
            return []

    else:
        try:
            page = get(web_page)
        except SSLError:
            page = get(web_page, verify=False) 
        except ConnectionError:
            print ("No internet connection aviable")
            sys.exit(2)


        tree = html.fromstring(page.content)

        interpret_list = tree.xpath(interpret_xpath)
        song_list = tree.xpath(song_xpath)

        if interpret_list and song_list
            return [interpret_list[0], song_list[0], station]
        else:
            return []

def job(name):
    print(name)
    record()


def main(argv):
    global _selenium
    help_string = '''__main__.py -c <config_file.json> \t -or we load default config.json
-h \t\t - help
-s \t\t - use selenium instead of requests (for javascript generated html)'''
    if argv:
        try:
            opts, args = getopt.getopt(argv,"hsc:",["conf="])
        except getopt.GetoptError:
            print(help_string)
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print(help_string)
                sys.exit(2)
            if opt == '-s':
                _selenium = True
            elif opt in('-c','--conf'):
                read_config(arg)
            # TODO: unsecure option if https:// connection failing
    else:
        print("Loading default config")
        read_config('config.json')

    record(**_config)

if __name__ == '__main__':
    main(sys.argv[1:])
