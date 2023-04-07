# import logging
# from deepracer import boto3_enhancer
import os

DURATION_THRESHOLD = 1

GOOGLE_DDNS = os.getenv('GOOGLE_DDNS')
GOOGLE_DDNS_UNAME = os.getenv('GOOGLE_DDNS_UNAME')
GOOGLE_DDNS_PWD = os.getenv('GOOGLE_DDNS_PWD')
SG_ID = os.getenv("SG_ID")
PL_ID = os.getenv("PL_ID")