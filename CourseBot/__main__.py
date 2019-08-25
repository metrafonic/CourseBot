import argparse
import sys
from Client import DiscordClient
import threading
from Client import models
parser = argparse.ArgumentParser(description='Discord bot to manage and notify about new courses')
parser.add_argument('token', metavar='t', type=str,
                    help='token')

args = parser.parse_args()
client = DiscordClient()
print(args)
if "initdb" in args.token:
    models.init_db()
    sys.exit(0)
t = threading.Thread(target=client.run, args=(args.token,))
t.start()