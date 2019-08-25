import argparse
import sys
import os
from Client import DiscordClient
import threading
from Client import models
parser = argparse.ArgumentParser(description='Discord bot to manage and notify about new courses')
parser.add_argument('--token', metavar='t', type=str,
                    help='token')

args = parser.parse_args()
client = DiscordClient()
models.init_db()
token = str(os.getenv('TOKEN', str(args.token)))
t = threading.Thread(target=client.run, args=(token,))
t.start()