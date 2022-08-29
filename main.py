#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# NOTES:
#
# Currently this will only boost the first eligible item per file and will wait until the next cyclic execution to auto-boost the next
# Numerology: https://github.com/Podnews-LLC/boostagram-numerology
#
# Command line Arguments:
# -m : Message 'I love your show!'
# -n : Node '030a58b8653d32b99200a2334cfe913e51dc7d155aa0116c176657a4f1722677a3'
# -s : Show Name 'Podcasting 2.0'
# -u : URL 'http://mp3s.nashownotes.com/pc20rss.xml'
# -i : feedID '920666'
# python3 main.py -m 'I love your show!' -n '030a58b8653d32b99200a233asdfasdfasdfd155aa0116c176657a4f1722677a3' -s 'Podcasting 2.0' -u 'http://mp3s.nashownotes.com/pc20rss.xml' -i 920666
#
# keysend_message: str = '{"podcast": "' + BAG_PODCAST + '", "url": "' + BAG_URL + '", "episode": "' + BAG_EPISODE + '", "ts": ' + str(BAG_TIMESTAMP_INT) + ', "time": "' + BAG_TIMESTAMP_STR + '", "value_msat": ' + str(BAG_MSAT) + ', "value_msat_total": ' + str(BAG_MSAT_TOTAL) + ', "action": "' + BAG_ACTION + '", "sender_name": "' + BAG_SENDER_NAME + '", "app_name": "' + BAG_APP_NAME + '", "message": "' + BAG_MESSAGE + '", "feedID": ' + str(BAG_FEEDID) + '}' ## Full statically defined KeySend Message for reference only

from google.protobuf.json_format import MessageToJson
from datetime import datetime
import lightning_pb2 as ln
import lightning_pb2_grpc as lnrpc
import grpc
import codecs
import binascii
import os
import logging
import subprocess
import json
import base64
import pycurl
import base64
from hashlib import sha256
from secrets import token_hex
from typing import Tuple
import httpx
import httpx._config
import ssl
from ssl import _create_unverified_context
import sys
import getopt

ssl._create_default_https_context = ssl._create_stdlib_context

# Constants Definition
TESTING_NODE = "030a58b8653d32b99200a23asedrfedse1dc7d155aa0116c176657a4f1722677a3" # My Testing GetAlby Wallet
BOOSTAGRAM_AMOUNT_SATOSHIS = 4761
##BOOSTAGRAM_AMOUNT_SATOSHIS = 10
BAG_PODCASTS = [
                {"shortname": "PC20",
                "name": "Podcasting 2.0",
                "url": "http://mp3s.nashownotes.com/pc20rss.xml",
                "feedid": 920666,
                "node": "03ae9f91a0cb8ff43840e3c322c4c61f019d8c1c3cea15a25cfc425ac605e61a4a",
                "boilerpretext": "Hi Dave and Adam, and listeners of Podcasting 2.0. ",
                "boilerposttext": " Anyway, I encourage anyone that isn't already listening to Causality to visit engineered.network as we analyse what went right & what went wrong..."},
                {"shortname": "Causality",
                "name": "Causality",
                "url": "https://engineered.network/causality/feed/index.xml",
                "feedid": 878147,
                "node": "030a58b8653d32b99200a23asedrfedse1dc7d155aa0116c176657a4f1722677a3",
                "boilerpretext": "Hi John, ",
                "boilerposttext": "...and that's a wrap"}
                ]

BAG_PODCAST = "Podcasting 2.0"
## BAG_URL = "https://your.url/index.xml" # The RSS Feed URL
## BAG_MSAT = 4761000
## BAG_MSAT_TOTAL = 4761000
BAG_ACTION = "boost"
BAG_SENDER_NAME = "John Booster"
BAG_APP_NAME = "PythonBoost"
BAG_MESSAGE = "This is a default message"
BAG_FEEDID = 878147

# Not required in a recurring / instantaneous Weekly Boost
## BAG_EPISODE = "Episode Title"
## BAG_TIMESTAMP_INT = 14
## BAG_TIMESTAMP_STR = "12:45"

# Pushover Notifications
PUSHOVER_ENABLE = True
PUSHOVER_USER_TOKEN = "<TOKEN>" # Insert your own User Token Here
PUSHOVER_API_TOKEN = "<TOKEN>" # Insert your own API Token Here
PUSHOVER_NOTIFICATION_TITLE = "Auto Boostagram Sent!"

# Node Details
VM_ACTIVE = False
MACAROON_LOCATION_MACOS = "/Users/john/Documents/LND/admin.macaroon" # macOS
MACAROON_LOCATION_VM = "/root/pybooster/admin.macaroon" # Alpine VM
TLSCERT_LOCATION_MACOS = "/Users/john/Documents/LND/fullchain.cer" # macOS
TLSCERT_LOCATION_VM = "/root/certs/fullchain.cer" # Alpine VM
BOOSTAGRAM_FILE_LOCATION_MACOS =  "/Users/john/Documents/pybooster/boostagrams.json" # macOS
BOOSTAGRAM_FILE_LOCATION_VM =  "/root/pybooster/boostagrams.json" # Alpine VM

NODE_ADDRESS = "node.duckdns.org" # Personal Raspiblitz
##ENABLE_FILE_BOOSTAGRAMS = True
ENABLE_FILE_BOOSTAGRAMS = False
##FORCE_TEST_WALLET = True
FORCE_TEST_WALLET = False

#
# Functions
#

def b64_hex_transform(plain_str: str) -> str:
    a_string = bytes.fromhex(plain_str)
    return base64.b64encode(a_string).decode()


def b64_transform(plain_str: str) -> str:
    return base64.b64encode(plain_str.encode()).decode()

#
# Main function
#

def main(argv):
    os.environ["GRPC_SSL_CIPHER_SUITES"] = 'HIGH+ECDSA'
    boostpodcast = boostpodcastshortname = boostdate = boostmessage = boostnode = boosturl = boostboilerpretext = boostboilerposttext = macaroonlocation = tlscertlocation = boostagramfilelocation = url = ""
    boostfeedid = 0
    headers = ctx = data = options = []
    boostmillisats = BOOSTAGRAM_AMOUNT_SATOSHIS * 1000
    processboostagram = False

    # Test for Command Line Arguments
    try:
        options, arguments = getopt.getopt(argv,"hm:n:s:u:i:",["message=","node=","show=","url=","feedid="])
    except getopt.GetoptError:
        print('Command line arguments not or incorrectly provided')

    for option, argument in options:
        if option == '-h':
            print('main.py -m <message> -n <node> -s <showname> -u <url> -i <feedid>')
            sys.exit()
        elif option in ("-m", "--message"):
            boostmessage = argument
        elif option in ("-n", "--node"):
            boostnode = argument
        elif option in ("-s", "--showname"):
            boostpodcast = argument
        elif option in ("-u", "--url"):
            boosturl = argument
        elif option in ("-i", "--feedid"): # Convert FeedID into an integer
            boostfeedid = int(argument)
#    print('Message is', boostmessage, 'Node is', boostnode, 'Show Name is', boostpodcast, 'URL is', boosturl, 'FeedID is', str(boostfeedid))

    if VM_ACTIVE:
        macaroonlocation = MACAROON_LOCATION_VM
        tlscertlocation = TLSCERT_LOCATION_VM
        boostagramfilelocation = BOOSTAGRAM_FILE_LOCATION_VM
    else:
        macaroonlocation = MACAROON_LOCATION_MACOS
        tlscertlocation = TLSCERT_LOCATION_MACOS
        boostagramfilelocation = BOOSTAGRAM_FILE_LOCATION_MACOS

    if ENABLE_FILE_BOOSTAGRAMS:
        currentboosttime = datetime.now()
        lastboostfile = os.path.expanduser('lastboost.db')
        if os.path.exists(lastboostfile):
            with open(lastboostfile) as lastboostfiledata:
                lastboostfiledataraw = lastboostfiledata.readlines()
                lastboostfiledatarawarray = [i.strip() for i in lastboostfiledataraw]
                lastboosttime = datetime.strptime(lastboostfiledatarawarray[0], '%Y-%m-%d %H:%M:%S')
        else:
            lastboosttime = datetime.now()

        # Open and read in all Boostagrams from file
        boostagramfile = os.path.expanduser(boostagramfilelocation)
        if os.path.exists(boostagramfile):
            with open(boostagramfile) as boostagramfiledata:
                boostagramdataraw = boostagramfiledata.read()
                boostagram_array = json.loads(boostagramdataraw)
        else:
            boostagram_array = []

        for boostagram in boostagram_array:
            boostagramtime = datetime.strptime(boostagram['date'], '%Y-%m-%d %H:%M:%S')
            if (currentboosttime > boostagramtime) and (boostagramtime > lastboosttime):
                boostpodcastshortname = boostagram['podcast']
                boostdate = boostagram['date']
                boostmessage = boostagram['message']
                break

        if boostmessage and boostpodcastshortname and boostdate:
            processboostagram = True

            for podcast in BAG_PODCASTS: # Extract Node details from Array
                if boostpodcastshortname == podcast['shortname']:
                    boostpodcast = podcast['name']
                    boostnode = podcast['node']
                    boosturl = podcast['url']
                    boostfeedid = podcast['feedid']
                    boostboilerpretext = podcast['boilerpretext']
                    boostboilerposttext = podcast['boilerposttext']

    else: # ENABLE_FILE_BOOSTAGRAMS is disabled (Command Line only)
        if boostmessage and boostnode and boostpodcast and boosturl and (boostfeedid > 0): # Enough information to send a Boostagram
            processboostagram = True
        else: # Unable to boost, get out!
            processboostagram = False

    if processboostagram:
        # Open and read in the Macaroon
        with open(os.path.expanduser(macaroonlocation), 'rb') as f:
            macaroon_bytes = f.read()
            macaroon = codecs.encode(macaroon_bytes, 'hex')

        # Open and read in the TLS Certificate
        cert = open(os.path.expanduser(tlscertlocation), 'rb').read()
        creds = grpc.ssl_channel_credentials(cert)
        channel = grpc.secure_channel(NODE_ADDRESS + ':10009', creds)
        stub = lnrpc.LightningStub(channel)

        if boostnode:
            if FORCE_TEST_WALLET:
                boostnode = TESTING_NODE

            macaroon = codecs.encode(open(macaroonlocation, "rb").read(), "hex")
            headers = {"Grpc-Metadata-macaroon": macaroon}
            dest = b64_hex_transform(boostnode) # Base 64 encoded destination bytes
            pre_image = token_hex(32) # We generate a random 32 byte Hex pre_image here.
            payment_hash = sha256(bytes.fromhex(pre_image)) # This is the hash of the pre-image

            boostfullmessage = ""
            if boostboilerpretext:
                boostfullmessage += boostboilerpretext

            if boostmessage:
                boostfullmessage += boostmessage

            if boostboilerposttext:
                boostfullmessage += boostboilerposttext

            if not boostfullmessage:
                boostfullmessage = BAG_MESSAGE

            pushover_message = boostmessage

            keysend_message: str = '{"podcast": "' + boostpodcast + \
                '", "url": "' + boosturl + \
                '", "value_msat": ' + str(boostmillisats) + \
                ', "value_msat_total": ' + str(boostmillisats) + \
                ', "action": "' + BAG_ACTION + \
                '", "sender_name": "' + BAG_SENDER_NAME + \
                '", "app_name": "' + BAG_APP_NAME + \
                '", "message": "' + boostfullmessage + \
                '", "feedID": ' + str(boostfeedid) + \
                '}'

        # The record 5482373484 is special: it carries the pre_image to the destination so it can be compared with the hash we pass via the payment_hash
        dest_custom_records = {
            5482373484: b64_hex_transform(pre_image),
            7629169: b64_transform(keysend_message),
            696969: b64_transform("2mapEmLBOr1wkqd1FiLG")
        }

        url = f"https://{NODE_ADDRESS}:8080/v1/channels/transactions"
        data = {
            "dest": dest,
            "amt": BOOSTAGRAM_AMOUNT_SATOSHIS,
            "payment_hash": b64_hex_transform(payment_hash.hexdigest()),
            "dest_custom_records": dest_custom_records,
        }

        ctx = _create_unverified_context()
        ctx.set_ciphers('ALL')
        ctx.options &= ~ssl.OP_NO_SSLv3 # allow ssl3.0, Default forbidden. Without this won't run on macOS

        response = httpx.post(url=url, headers=headers, data=json.dumps(data), verify=ctx, timeout=None)
        print(json.dumps(response.json(), indent=2))

        if boostdate and not FORCE_TEST_WALLET:
            print("Boosted at " + currentboosttime)
            lastboostfile = os.path.expanduser('lastboost.db')
            with open(lastboostfile, 'w') as lastboostfiledata:
                lastboostfiledata.write(boostdate)

            if PUSHOVER_ENABLE and pushover_message:
                crl = pycurl.Curl()
                crl.setopt(crl.URL, 'https://api.pushover.net/1/messages.json')
                crl.setopt(pycurl.HTTPHEADER, ['Content-Type: application/json' , 'Accept: application/json'])
                data = json.dumps({"token": PUSHOVER_API_TOKEN, "user": PUSHOVER_USER_TOKEN, "title": PUSHOVER_NOTIFICATION_TITLE, "message": pushover_message })
                crl.setopt(pycurl.POST, 1)
                crl.setopt(pycurl.POSTFIELDS, data)
                crl.perform()
                crl.close()

# End Main Function

if __name__ == "__main__":
    main(sys.argv[1:])

# End Script
