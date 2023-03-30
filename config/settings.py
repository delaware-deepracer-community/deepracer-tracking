import logging
from deepracer import boto3_enhancer
import os

DURATION_THRESHOLD = 180

GOOGLE_DDNS = os.getenv('GOOGLE_DDNS')
GOOGLE_DDNS_UNAME = os.getenv('GOOGLE_DDNS_UNAME')
GOOGLE_DDNS_PWD = os.getenv('GOOGLE_DDNS_PWD')

print(f"Google DDNS is: {GOOGLE_DDNS}")