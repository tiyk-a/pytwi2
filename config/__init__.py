import sys
import argparse

# if 'unittest' in sys.argv[0]:
#     from config.test import *
# else:
parser = argparse.ArgumentParser()
parser.add_argument(
    "-p",
    "--production",
    action="store_true",
    help="use production config")
parser.add_argument(
    "-d",
    "--development",
    action="store_true",
    help="use development config")
# parser.add_argument(
#     "-t", "--test", action="store_true", help="use test config")
args = parser.parse_args()
if args.production:
    from config.config import *
elif args.development:
    from config.dev import *
# elif args.test:
#     from config.test import *
else:
    from config.dev import *