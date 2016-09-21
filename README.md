#Fine Playlist scrapper:

## Story:

Once upon a time (yesterday) someone (me) was riding his car and listening to a radio. It was beautiful rainy day and a beautiful song came to my ears. I said to myself: "Ooh, what a pleasant song." But, (the story always has it's downfalls) either I missed the track info, or the radio didn't show up... so it happened, that it remained just 'a song'. Withou name, without face. And I really wanted to know. Beating around the bushes, going to fight the windmills I came to solution. The funny part is, that when it really started to work, they played my song at the very moment I was debugging it... So i hope it will get use for someone.

## Usage

## To make work headless firefox with selenium, you have to install Xvfb driver:

```
$ sudo apt-get install xvfb xfonts-100dpi xfonts-75dpi xfonts-cyrillic xorg dbus-x11
```

## You have to install requirements.txt

```
$ pip install -r requirements.txt
```


Some pages use generated content model over classic html code, so you can't capture the raw data correctly. In that case, you should use selenium implementation over requests. Options are not mandatory, if -c is ommited default config.json is loaded:

```
python3 __main__.py -s -c expres.conf
```

Will create 'YYYY_MM_DD_STREAMNAME_PLAYLIST.txt' file which will contain currently captured song:

```
HH:MM    Interpret - Song Name
```

#Schedule

To capture whole playlist you have to make crontab schedule or widows/mac equivalent.
Crontab job should run every minute which is enough to make sure the timing is correct. For each radiostation only the new song will be logged.
You may like to be sure that the files are saved at the directory, config file is optional:

Run:
```
crontab -e
```
Fill in following:
```
*/1 * * * * cd <path to script> && python3 __main__.py [-c myConfig.json]
```
Check for sure that it's fine:
```
contrab -l
````

# Man, what station is this?!

If you want to make your own config file, edit the variables which make the _dictionary underneath the imports. in ```main.py``` obviously. (e.g. _station, _url, _interpret_path,  _song_name_path)

For example this bit:
```
_station = 'EVROPA2'
_url = 'https://www.evropa2.cz'
_interpret_path = '//h3[@class="author"]/text()'
_song_name_path = '//h4[@class="song"]/text()'
````

Then run:
```
you@host~/.../fplyst$ python3 -i __main__.py
```
In python prompt you either call method without any attributes, which overwrites original config file...
``` 
>>> make_config()
```
...or you feed it with a filename, which you may than use to import config for various stations.
```
>>> make_config("myConfig.json")
```
(json extension is optional)

# How can i profit?

If you are familiar enough with xpath syntax, it shouldn't be hard for you to easily setup html xpaths to interpret and song.

## notes:
* sorry, it only parses two-element playlist. In my config the info consists of two ```<a href=>``` tags, so edit accordingly or edit whole code
* it should work with UTF-8 since i had hard time to convert iy to python3 (i'm joknig, 'twas only minute)
* does not work on "program" or "shows" when there is no info. If you are willing to help me with anything, pull requests are welcome!
* It does work with javascript generated ```<html>``` code. However, selenium uses another xpath notation than lxml. So when you use one path for lxml, you have to use another when using selenium option.
