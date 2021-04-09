from requests import get
from time import sleep
from os import getenv

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, LCD_FONT, TINY_FONT

import datetime

from .assets import YOUTUBE_LOGO

class YouTubeApiClient:
    def __init__(self, apikey=getenv('YOUTUBE_KEY'),
                 channel=getenv('YOUTUBE_CHANNEL_ID')):
        self.apikey = apikey
        self.channel = channel

    def get_data(self):
        print(f'Fetching data for channel {self.channel} ...')
        url = 'https://content-youtube.googleapis.com/youtube/v3/channels'
        response = get(
            url,
            params={
                'part': 'statistics',
                'id': self.channel,
                'key': self.apikey})

        if response.status_code != 200:
            raise ValueError(f'YouTube returned {response.status_code}')

        return response.json()


class CachedYouTubeData:
    def __init__(self, client):
        self.client = client
        self.data = None

    def subs(self):
        return self.get_data()['items'][0]['statistics']['subscriberCount']

    def views(self):
        return self.get_data()['items'][0]['statistics']['viewCount']

    def get_data(self):
        if self.data is not None and (
                datetime.datetime.now() -
                self.fetch_timestamp).seconds > 60:
            self.data = None

        if self.data is None:
            self.data = self.client.get_data()
            self.fetch_timestamp = datetime.datetime.now()

        return self.data


class Controller:
    def __init__(self, device, apikey, channel, interval):
        self.device = device
        self.channel = channel
        self.apikey = apikey
        self.interval = interval

    def start(self):
        iteration = 0
        data = CachedYouTubeData(
            YouTubeApiClient(
                channel=self.channel,
                apikey=self.apikey))

        try:
            while True:
                self.set_contrast
                self.draw_count(
                    data.subs() if iteration %
                    2 == 0 else data.views())
                iteration += 1
                sleep(self.interval)
        except Exception as e:
            print(f'An error occurred: {e}')

    def set_contrast(self):
        now = datetime.datetime.now()
        if now.hour > 9 and now.hour < 18:
            self.device.contrast = 1
        else:
            self.device.contrast = 0.1

    def draw_count(self, count):
        with canvas(self.device) as draw:
            self.draw_pic(draw, YOUTUBE_LOGO, 0)
            self.draw_text(draw, str(count))

    def draw_text(self, draw, content):
        content_len = len(content)
        text(draw, (66 - (content_len * 6), 1), content,
             fill="white", font=proportional(LCD_FONT))

    def draw_pic(self, draw, pattern, offset):
        for x, row in enumerate(pattern):
            for y, val in enumerate(row):
                if val == 1:
                    draw.point((y + offset, x), fill="white")


class Counter:
    def __init__(self, channel, apikey, device='max7219', interval=60):
        self.channel = channel
        self.apikey = apikey
        self.device = device
        self.interval = interval

    def start(self):
        Controller(
            device=self.resolve_device(),
            channel=self.channel,
            apikey=self.apikey,
            interval=self.interval).start()

    def resolve_device(self):
        if self.device == 'emulator':
            return self.device_pygame()
        else:
            return self.device_max7219()

    def device_max7219(self):
        serial = spi(port=0, device=0, gpio=noop())
        device = max7219(
            serial,
            width=64,
            height=8,
            rotate=0,
            block_orientation=-90)
        return device

    def device_pygame(self):
        from luma.emulator.device import pygame
        return pygame(width=64, height=8)
