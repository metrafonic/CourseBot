import argparse
from Client import DiscordClient
import threading
parser = argparse.ArgumentParser(description='Discord bot to manage and notify about new courses')
parser.add_argument('token', metavar='t', type=str,
                    help='token')
parser.add_argument('--sum', dest='accumulate', action='store_const',
                    const=sum, default=max,
                    help='sum the integers (default: find the max)')

args = parser.parse_args()
client = DiscordClient()
print(args.token)
t = threading.Thread(target=client.run, args=(args.token,))
t.start()