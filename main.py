# -*- coding: utf-8 -*-
# Module: default
# Author: marodere
# Created on: 16.09.2018
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html

import sys
import requests
from urllib import urlencode
from urlparse import parse_qsl
import xbmcgui
import xbmcplugin

_session = requests.Session()

_url = sys.argv[0]
_handle = int(sys.argv[1])

def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urlencode(kwargs))

def get_channels():
    return _session.get("https://frontend.vh.yandex.ru/channels.json").json()["set"]

def list_channels():
    xbmcplugin.setPluginCategory(_handle, 'Yandex TV')
    xbmcplugin.setContent(_handle, 'videos')

    for channel in get_channels():
        list_item = xbmcgui.ListItem(label=channel['title'])

        list_item.setInfo('video', {'title': channel['title'],
                                    'mediatype': 'video'})

        thumb = 'https:{0}'.format(channel['thumbnail'])
        list_item.setArt({'thumb': thumb, 'icon': thumb, 'fanart': thumb})
        list_item.setProperty('IsPlayable', 'true')

        url = get_url(action='play', video=channel['streams'][0]['content_url'])
        is_folder = False
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(_handle)


def play_video(path):
    play_item = xbmcgui.ListItem(path=path)
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    params = dict(parse_qsl(paramstring))
    if params:
        if params['action'] == 'play':
            play_video(params['video'])
        else:
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        list_channels()


if __name__ == '__main__':
    router(sys.argv[2][1:])
