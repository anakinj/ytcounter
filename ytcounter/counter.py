from requests import get
from time import sleep
from os import getenv

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, LCD_FONT, TINY_FONT

# from assets import YOUTUBE_LOGO

YOUTUBE_LOGO = [[0,0,0,0,0,0,0,0,0,0],
                [0,0,1,1,1,1,1,1,1,0],
                [0,1,1,1,0,1,1,1,1,1],
                [0,1,1,1,0,0,1,1,1,1],
                [0,1,1,1,0,0,0,1,1,1],
                [0,1,1,1,0,0,1,1,1,1],
                [0,1,1,1,0,1,1,1,1,1],
                [0,0,1,1,1,1,1,1,1,0]]

class YouTubeClient(object):
  def __init__(self, apikey = getenv('YOUTUBE_KEY'), channel = getenv('YOUTUBE_CHANNEL_ID')):
    super(YouTubeClient, self).__init__()
    self.apikey = apikey
    self.channel = channel

  def get_data(self):
    print(f'Fetching data for channel {self.channel} ...')
    url = 'https://content-youtube.googleapis.com/youtube/v3/channels'
    response = get(url, params = { 'part': 'statistics', 'id': self.channel, 'key': self.apikey})
    if response.status_code != 200:
      raise ValueError(f'YouTube returned {response.status_code}')

    return response.json()

  def get_subs(self):
    return self.get_data()['items'][0]['statistics']['subscriberCount']

  def get_views(self):
    return self.get_data()['items'][0]['statistics']['viewCount']

class Controller(object):
  def __init__(self, device, apikey, channel):
    super(Controller, self).__init__()
    self.device = device
    self.channel = channel
    self.apikey = apikey

  def start(self):
    iteration = 0
    client = YouTubeClient(channel = self.channel, apikey = self.apikey)

    try:
      self.device.contrast = 1
      while True:
        count = client.get_subs() if iteration % 2 == 0 else client.get_views();
        with canvas(self.device) as draw:
          self.draw_pic(draw, YOUTUBE_LOGO, 0)
          self.draw_text(draw, str(count))

        iteration +=1
        sleep(10)
    except Exception as e:
      print(f'An error occurred: {e}')

  def draw_text(self, draw, content):
    content_len = len(content)
    text(draw, (66-(content_len*6), 1), content, fill="white", font=proportional(LCD_FONT))

  def draw_pic(self, draw, pattern, offset):
    for x, row in enumerate(pattern):
      for y, val in enumerate(row):
        if val == 1:
          draw.point((y+offset, x), fill="white")

class Counter(object):
  def __init__(self, channel, apikey, device = 'max7219'):
    self.channel = channel
    self.apikey = apikey
    self.device = device
    super(Counter, self).__init__()

  def start(self):
    Controller(device = self.resolve_device(), channel = self.channel, apikey = self.apikey).start()

  def resolve_device(self):
    if self.device == 'max7219':
      return self.device_max7219()
    else:
      return self.device_pygame()

  def device_max7219(self):
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, width=64, height=8, rotate=0, block_orientation=-90)
    return device

  def device_pygame(self):
    from luma.emulator.device import pygame
    return pygame(width=64, height=8)
