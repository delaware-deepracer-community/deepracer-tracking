# import logging
# from deepracer import boto3_enhancer
import os
import boto3

DURATION_THRESHOLD = 2

GOOGLE_DDNS = os.getenv('GOOGLE_DDNS')
GOOGLE_DDNS_UNAME = os.getenv('GOOGLE_DDNS_UNAME')
GOOGLE_DDNS_PWD = os.getenv('GOOGLE_DDNS_PWD')
SG_ID = os.getenv("SG_ID")
PL_ID = os.getenv("PL_ID")

LOG_CLIENT = boto3.client('logs', region_name='us-east-1')

# Cloudflare
CF_API_KEY = os.getenv("CF_API_KEY")
CF_EMAIL = os.getenv("CF_EMAIL")
CF_BASE_URL = 'https://api.cloudflare.com/client/v4/zones'
CF_ZONE_ID = os.getenv("CF_ZONE_ID")