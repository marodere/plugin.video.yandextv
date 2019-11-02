# -*- coding: utf-8 -*-

import os
import sys
import xbmcgui
import xbmcplugin
import xbmcaddon
from urlparse import parse_qsl
from urllib import urlencode
import json
import time
import datetime
from urllib2 import urlopen
from urlparse import urlparse

YANDEX_TV_URL_PREFIX = 'https://strm.yandex.ru'
RESOLUTION = '720p'
#
# Notes
#
# For plugin rules are the following:
# - If a ListItem opens a lower lever list, it must have isFolder=True.
# - If a ListItem calls a playback function that ends with setResolvedUrl, it must have setProperty('isPlayable', 'true') and IsFolder=False.
# - If a ListItem does any other task except for mentioned above, is must have isFolder=False (and only this).

# setup plugin base stuff
try:
    KODI_BASE_URL = sys.argv[0]
    PLUGIN_HANDLE = int(sys.argv[1])
except ValueError:
    PLUGIN_HANDLE = 1
    KODI_BASE_URL = ''

def main(paramstring):
    print(paramstring)
    params = dict(parse_qsl(paramstring))
    if params:
        if params['action'] == 'play':
            play_video(params['video'])
        elif params['action'] == 'episodes':
            list_today_episodes(params['content_id'])
        else:
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        #
        # This action caused one time after Kodi boot
        # Other openings the addon just show result of previous call
        list_channels(get_channels())


def play_video(path):
    play_item = xbmcgui.ListItem(path=get_content_url(path, RESOLUTION).strip())
    xbmcplugin.setResolvedUrl(PLUGIN_HANDLE, True, listitem=play_item)

def get_channels():
    with open(os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'tv.json'), 'r') as jsonfo:
        return json.load(jsonfo)


def list_channels(channels):
    xbmcplugin.setPluginCategory(PLUGIN_HANDLE, 'Yandex TV')
    xbmcplugin.setContent(PLUGIN_HANDLE, 'videos')

    list_items = []
    its_folder = True
    for channel in channels:
        it = xbmcgui.ListItem(label=channel['title'])

        thumb = channel['thumbnail']
        it.setArt({'thumb': thumb, 'icon': thumb, 'fanart': thumb})

        it.setProperty('content_id', channel['content_id'])

        url = get_url(action='episodes', content_id=channel['content_id'])

        list_items.append((url, it, its_folder))

    xbmcplugin.addDirectoryItems(PLUGIN_HANDLE, list_items)
    xbmcplugin.addSortMethod(PLUGIN_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(PLUGIN_HANDLE)


def get_url(**kwargs):
    return '{0}?{1}'.format(KODI_BASE_URL, urlencode(kwargs))


def list_today_episodes(content_id):
    # url = 'https://frontend.vh.yandex.ru/v23/episodes.json?parent_id={parent_id}&start_date__to={now}&end_date__from={now}&locale=ru&from=videohub&service=ya-main&disable_trackings=1'
    #
    # Receive all available episodes, because i did not understand how receive for concrete day
    #
    url = 'https://frontend.vh.yandex.ru/v23/episodes.json?parent_id={parent_id}&locale=ru'
    url = url.format(parent_id=content_id, now=int(time.time()))

    # print(url)
    try:
        r = urlopen(url)
        # print(r)

        body = r.read()
        # print(body)

        episodes = json.loads(body)
        # print(episodes)

        list_items = []
        for episode in episodes['set']:
            title = u'{} {}'.format(datetime.datetime.fromtimestamp(episode['start_time']), episode['title'])

            it = xbmcgui.ListItem(label=title)

            it.setInfo('video', {
                'title': title,
                'duration': int(episode['end_time'] - episode['start_time']),
                'plotoutline': episode.get('description', ''),
                'mediatype': 'video'
                })

            thumb = 'https:{0}'.format(episode['thumbnail'])
            it.setArt({'thumb': thumb, 'icon': thumb, 'fanart': thumb})

            it.setProperty('IsPlayable', 'true')
            it.setIsFolder(False)
            #
            # Does not detect working URL here to suficiently keep time
            # url = get_url(action='play', video=get_content_url(episode['content_url'], RESOLUTION).strip())
            url = get_url(action='play', video=episode['content_url'])

            list_items.append((url, it))

        print('Loaded {} episodes'.format(len(list_items)))

        xbmcplugin.addDirectoryItems(PLUGIN_HANDLE, list_items)
        xbmcplugin.endOfDirectory(PLUGIN_HANDLE)

    except Exception as e:
        print('Could not receive episodes')
        print(e)


def get_content_url(m3u8_url, resolution):
    parser = urlparse(m3u8_url)
    path = parser.path
    if os.path.isabs(path):
        path = YANDEX_TV_URL_PREFIX + path

    try:
        response = urlopen(m3u8_url)
        for l in response:
            if l[0] == '#':
                continue

            if l.find(resolution) > -1:
                if l[0] != '/':
                    content_url = l
                else:
                    content_url = YANDEX_TV_URL_PREFIX + l

                try:
                    recv_anything = urlopen(content_url).read(512)
                    if recv_anything:
                        #
                        # We need only one working video stream, so
                        return content_url
                except Exception as e:
                    print(e)

    except Exception as e:
        print(e)

    return m3u8_url


if __name__ == '__main__':
    print(sys.argv)
    main(sys.argv[2][1:])
