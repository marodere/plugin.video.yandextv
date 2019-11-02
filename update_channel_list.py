# -*- coding: utf-8 -*-
#
# Generate JSON with working TV channels

import os
import json
import time
from datetime import timedelta, date
from urllib2 import urlopen
from urlparse import urlparse

CHANNELS_FILE = 'channels.json'
CHANNELS_JSON_URL = 'https://frontend.vh.yandex.ru/channels.json'
TV_FILE = 'tv.json'
YANDEX_TV_URL_PREFIX = 'https://strm.yandex.ru'
RESOLUTION = '720p'


def main():
    with open(CHANNELS_FILE, "w") as fo:
        channels = urlopen(CHANNELS_JSON_URL).read()
        fo.write(channels)

    channels = json.loads(channels)
    tv_channels = []
    for s in channels['set']:
        # content_url = get_channel_content_url(s, RESOLUTION)
        # if content_url:
        tv_channels.append({
                'title': s['title'],
                # Channed icon
                'thumbnail': 'https:{0}'.format(s['thumbnail']),
                'live_broadcast_url': s['streams'][0]['url'],
                # Needed to request episodes
                'content_id': s['content_id'],
                # debug
                # 'episodes': get_today_episodes(s['content_id']),
                })
        # break  # debug
    with open(TV_FILE, 'w') as tvfo:
        json.dump(tv_channels, tvfo)


def get_channel_content_url(s, resolution):
    if 'stream' not in s:
        return None

    url = s['streams'][0]['url']
    parser = urlparse(url)
    path = parser.path
    if os.path.isabs(path):
        path = YANDEX_TV_URL_PREFIX + path

    try:
        response = urlopen(url)
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


def get_today_episodes(content_id):
    # ltime = time.localtime(time.time())
    # today = date(year=ltime.tm_year, month=ltime.tm_mon, day=ltime.tm_mday)

    # today_start = today.timetuple()

    # today_end = today + timedelta(days=1) - timedelta(seconds=1)
    # today_end = today_end.timetuple()

    # url = 'https://frontend.vh.yandex.ru/v23/episodes.json?parent_id={parent_id}&end_date__from={day_end}&start_date__to={day_start}&locale=ru&from=videohub&service=ya-main&disable_trackings=1'
    # url = url.format(parent_id=content_id, 
    #                  day_start=int(time.mktime(today_start)),
    #                  day_end=int(time.mktime(today_end)))

    url = 'https://frontend.vh.yandex.ru/v23/episodes.json?parent_id={parent_id}&end_date__from={now}&start_date__to={now}&locale=ru&from=videohub&service=ya-main&disable_trackings=1'
    url = url.format(parent_id=content_id, 
                     now=int(time.time()))
    # print url
    try:
        r = urlopen(url)
        print r
        print r.read()
        return ''
    except Exception as e:
        print('Could not receive episodes')
        print(e)
        return ''


if __name__ == '__main__':
    main()
