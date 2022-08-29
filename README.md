# pybooster
Tool for sending Boostagrams from your own node either via the command line or via a JSON pre-programmed file, written in Python.

INSTALLATION INSTRUCTIONS

Tested on Python 3.7.3
Refer: https://github.com/lightningnetwork/lnd/blob/master/docs/grpc/python.md

Ubuntu: (Steps tested on 19.04, should be similar on more recent releases)
- Ensure python3 --version reports 3.7.3 or above
- If you're using an OLD distro like 19.04, you'll probably need to grab the archived repos:
- - sudo sed -i -re 's/([a-z]{2}\.)?archive.ubuntu.com|security.ubuntu.com/old-releases.ubuntu.com/g' /etc/apt/sources.list
- - sudo apt-get update && sudo apt-get dist-upgrade
- Install pip3 if not already installed, install it from the default repo, but then upgrade pip and wheel to the latest versions immediately afterward:
- - sudo apt install python3-pip
- - sudo -H pip3 install --upgrade pip
- - sudo pip3 install --upgrade wheel
- - sudo pip3 install testresources setuptools
- Install the libraries needed for PIP to install the gRPC tools we need to use:
- - sudo apt-get install libnss3 libnss3-dev libcurl4-gnutls-dev librtmp-dev
- Finally, you can install the tools themselves:
- - sudo pip3 install grpcio grpcio-tools googleapis-common-protos pycurl

Alpine: (Steps tested on 3.14)
- Ensure python3 --version reports 3.7.3 or above (Tested on v3.10.5)
- Install pip3 if not already installed, install it from the default repo, but then upgrade pip and wheel to the latest versions immediately afterward:
- - apk add py3-pip
- - pip3 install --upgrade pip
- Install the tools themselves:
- - pip3 install grpcio grpcio-tools googleapis-common-protos pycurl

macOS: (Steps required on )
- - export PYCURL_SSL_LIBRARY=openssl
- - pip3 install grpcio grpcio-tools googleapis-common-protos pycurl


On a Raspiblitz things are easier since most of the above tools have already been installed:
- - cd /home/admin
- Note: Some other optional packages pre-install the LibCurl libraries, but to make sure you have them install them anyway:
- - sudo apt install libcurl4-gnutls-dev libcurl4-openssl-dev libcurl4-nss-dev
- - export PYCURL_SSL_LIBRARY=nss
- - sudo pip3 install grpcio grpcio-tools googleapis-common-protos pycurl
- Note: Upgrade to latest grpcio just in case:
- - sudo pip3 install --upgrade grpcio

Common to all: (Once all dependancies installed)
- From your home directory clone two Git Repos, and download the proto file you need:
- - git clone https://github.com/Podcastindex-org/extractlv
- - cd extractlv
- - git clone https://github.com/googleapis/googleapis.git
- - curl -o lightning.proto -s https://raw.githubusercontent.com/lightningnetwork/lnd/master/lnrpc/lightning.proto
- Finally, compile the required tool files:
- - python3 -m grpc_tools.protoc --proto_path=googleapis:. --python_out=. --grpc_python_out=. lightning.proto

USAGE AND CONFIGURATION

This simple script can be used in conjunction with the PushOver notification service to send a message once a Boost-A-Gram is sent. Go to Pushover.Net and create an application for the Notifier, then add your PUSHOVER_USER_TOKEN and PUSHOVER_API_TOKEN to the Definitions section of the script. You can disable PUSHOVER_ENABLE by setting it to False if you want to.

Node Details: The script will run on your local machine (Raspiblitz/Umbrel) or on any hosted Lightning Node with gRPC enabled and port 10009 opened. The default directories are for a Raspiblitz installation. If you want to run it remotely, you need your TLS Certificate and Admin Macaroon extracted from your Node. Put those files in a convenient location on the machine you're calling the script from and update the MACAROON_LOCATION and TLSCERT_LOCATION accordingly. Note that if you have a TLS certificate, it's probably signed against a URL, and some sites use DuckDNS for this purpose. Either way update the NODE_ADDRESS to your Node's URL. If you're running behind TOR you might need to configure further.

This script will send one push notification for every Boost-A-Gram sent. It was developed to be installed on two different machines - one a Virtual Machine that is always running and the other from the local desktop machine on-demand via the user manually. For this reason it has two sets of file paths that are selectable (refer VM_ACTIVE variable below).

KEY VARIABLES

BOOSTAGRAM_AMOUNT_SATOSHIS - Set the amount of your Boostagrams in Satoshis (not MilliSATS!)
ENABLE_FILE_BOOSTAGRAMS - If True, command line arguments will not be used and the JSON file will instead. If False the JSON file will be used and command line arguments will be ignored.
VM_ACTIVE - If True, the file paths for TLS Certificate, Macaroon and JSON file are for those on a specific machine. If False, the file paths are for a different machine.

TESTING VARIABLES

TESTING_NODE - The address of your own testing node. Highly advisable to trial this on a wallet/node on a service such as Alby before trying it on the real thing!
FORCE_TEST_WALLET - Force the script to use your Test Wallet


Set up a Cron Tab if you're intending to run it automatically. For weekly shows once a day should be fine:

0 0 * * * cd /[HOME DIRECTORY]/pybooster && /usr/bin/python /[HOME DIRECTORY]/pybooster/main.py >> /[HOME DIRECTORY]/pybooster/pybooster.log

PODCAST LIST CUSTOMISATION

Add, modify, remove shows from the BAG_PODCASTS array as needed:

BAG_PODCASTS = [
                {"shortname": "PC20",
                "name": "Podcasting 2.0",
                "url": "http://mp3s.nashownotes.com/pc20rss.xml",
                "feedid": 920666,
                "node": "03ae9f91a0cb8ff43840e3c322c4c61f019d8c1c3cea15a25cfc425ac605e61a4a",
                "boilerpretext": "Hi Dave and Adam, and listeners of Podcasting 2.0. ",
                "boilerposttext": " Anyway, I encourage anyone that isn't already listening to Causality to visit engineered.network as we analyse what went right & what went wrong & we discover that many outcomes can be predicted, planned for & even prevented and you too can decide if the listener that called me a dreamy narrator was right…or not."}
              }


WISH LIST
-------
* Pass Boostagram amount via JSON or command line - Is that a good idea or not?



CHANGE LOG

v.0.1
-------
* Initial Release
* Supports sending Boost-A-Grams via command line arguements or by JSON using a repeating Cron Job.
