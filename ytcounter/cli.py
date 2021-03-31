from .counter import Counter
import argparse

def main():
  parser = argparse.ArgumentParser(description='YouTube subscription and view counter')
  parser.add_argument('--device', help="Choose device to output on")
  parser.add_argument('--channel', help="YouTube channel id", required=True)
  parser.add_argument('--apikey', help="YouTube Data API key", required=True)
  args = parser.parse_args()

  Counter(device=args.device, channel=args.channel, apikey=args.apikey).start()
