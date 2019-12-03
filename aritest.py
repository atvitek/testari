#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from requests import HTTPError
import ari
from pprint import pprint


class Channel:
    def __init__(self):
        self.dtmf = ''
        self.playback = None

    def playback_start(self, playback, event):
        self.playback = playback

    def on_dtmf(self, channel, event):
        digit = event['digit']
        try:
            if digit == '5':
                self.playback.control(operation='pause')
            elif digit == '8':
                self.playback.control(operation='unpause')
            elif digit == '4':
                self.playback.control(operation='reverse')
            elif digit == '6':
                self.playback.control(operation='forward')
            elif digit == '2':
                self.playback.control(operation='restart')
            elif digit == '#':
                self.playback.stop()
                channel.continueInDialplan()
            elif digit == '*':
                self.playback.stop()
                self.playback = channel.play(media='sound:taxi/ivr2')
            elif len(self.dtmf) > 0 and '{0}{1}'.format(self.dtmf, digit)[-2:] == '90':  # обработка двойных нажатий
                print(90)
                self.dtmf = ''
            else:
                self.dtmf = self.dtmf + digit

        except HTTPError as e:
            # Ignore 404's, since channels can go away before we get to them
            if e.response.status_code != requests.codes.not_found:
                raise


# def playback_finish(playback, event):
#     print('Остановлен проигрышь информационного файла', playback, event)


client = ari.connect('http://192.168.0.111:8088/', 'home', '******')


def on_start(channel, event):
    pprint(('event: {0}'.format(event)))

    c = Channel()  # обработка канала

    # dtmf ожидание ответа и проигрыш файлов
    channel['channel'].answer()
    playback = channel['channel'].play(media='sound:demo-congrats')
    channel['channel'].play(media='sound:taxi/ivr2')
    channel['channel'].hold()

    # слушатель нажатий dtmf
    channel['channel'].on_event('ChannelDtmfReceived', c.on_dtmf)
    # слушатель остановки проигрыша файла
    playback.on_event('PlaybackFinished', lambda *args: print('Остановлен проигрышь информационного файла'))
    client.on_playback_event('PlaybackStarted', c.playback_start)


# print(client.get_repo('/playbacks/{playbackId}'))
client.on_channel_event('StasisStart', on_start)
client.run(apps="hello")
