# libraries we need
import urllib.request
import urllib.parse
import http.client
import base64
import socket
import requests
from config import settings
import pandas as pd

def update_ddns1():
    #------------------------------
    # all the user specific var
    # define google username & password for DDNS service
    myUname = settings.GOOGLE_DDNS_UNAME
    myPasswd = settings.GOOGLE_DDNS_PWD
    

    # define your subdomain to update
    myDomain = settings.GOOGLE_DDNS

    #------------------------------
    # Determine our current external IPs
    # use https://domains.google.com/checkip http server to obtain public IP, Google will return IPv6 so
    # other good server is http://ip.42.pl/raw which returns IPv4
    try:
        url4 = 'http://ip.42.pl/raw'
        req4 = urllib.request.Request(url4)
        resp4 = urllib.request.urlopen(req4)
        respData4 = resp4.read()
        extIP4 = respData4.decode('utf-8')

        url6 = 'https://domains.google.com/checkip'
        req6 = urllib.request.Request(url6)
        resp6 = urllib.request.urlopen(req6)
        respData6 = resp6.read()
        extIP6 = respData6.decode('utf-8')

        #print IPs to console for troubleshooting
        print (extIP4)
        print (extIP6)

        #------------------------------

        # Check current subdomain IP, if matches don't overwork Google's DNS server
        currentIP = socket.gethostbyname(myDomain)

        if currentIP != extIP4:
            # connect to Google DDNS to update IP
            # Google example syntax per https://support.google.com/domains/answer/6147083
            # https://username:password@domains.google.com/nic/update?hostname=subdomain.yourdomain.com&myip=1.2.3.4

            # base64 encode username & password
            myUsrPass = myUname + ":" + myPasswd
            myUsrPass = base64.b64encode(bytes(myUsrPass, 'utf-8')).decode("ascii")
            print (myUsrPass)

            # encode data & user agent
            # Google DDNS only supports IPv4 for now so we will us it
            myData = urllib.parse.urlencode({'hostname' : myDomain, 'myip' : extIP4 }).encode("UTF-8")
            upUrl= '/nic/update?'
            upHost = 'domains.google.com'

            # URL query example & Headers
            # POST /nic/update?hostname=subdomain.yourdomain.com&myip=1.2.3.4 HTTP/1.1
            # Host: domains.google.com
            # Authorization: Basic base64-encoded-auth-string User-Agent: Chrome/41.0 your_email@yourdomain.com

            headers = {
                'Content-Type'  : "application/x-www-form-urlencoded",
                'User-Agent'    : 'Chrome/41.0',
                'Authorization' : 'Basic %s' % myUsrPass
                }

            # connect & update (need to include some catch for errors later)
            conn = http.client.HTTPSConnection(upHost)
            conn.request("POST", upUrl, myData, headers)
            upResp = conn.getresponse()
            print(upResp.status, upResp.reason)
            print(upResp.read().decode('utf-8'))

        else:
            print("Current DNS shows your IP " + extIP4 + " no need to bother Google DNS")
    except Exception as ex:
        print(ex)

def update_ddns():
    #------------------------------
    # all the user specific var
    # define google username & password for DDNS service
    myUname = settings.GOOGLE_DDNS_UNAME
    myPasswd = settings.GOOGLE_DDNS_PWD
    

    # define your subdomain to update
    myDomain = settings.GOOGLE_DDNS

    #------------------------------
    # Determine our current external IPs
    # use https://domains.google.com/checkip http server to obtain public IP, Google will return IPv6 so
    # other good server is http://ip.42.pl/raw which returns IPv4
    try:
        url4 = 'https://ip.42.pl/raw'
        req4 = requests.get(url4, verify=False)
        extIP4 = req4.text

        #print IPs to console for troubleshooting
        print (extIP4)

        # get zone dns records
        cf_url = f'{settings.CF_BASE_URL}/{settings.CF_ZONE_ID}/dns_records'
        headers = {
            'X-Auth-Email': settings.CF_EMAIL,
            'X-Auth-Key': settings.CF_API_KEY,
            'Content-Type': 'application/json',
        }

        cf_record = requests.get(cf_url, headers=headers)
        cf_record_df = pd.DataFrame(cf_record.json()['result'])
        
        record_id = cf_record_df[cf_record_df['name'].str.contains(myDomain)].iloc[0]['id']
        
        # update dns record
        cf_update_url = f'{cf_url}/{record_id}'
        cf_update = requests.put(cf_update_url, headers=headers, json={'type': 'A', 'name': myDomain, 'content': extIP4, 'ttl': 3600, 'proxied': True})
        print(cf_update.text)

    except Exception as ex:
        print(ex)