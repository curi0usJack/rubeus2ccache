#!/usr/bin/env python3

import os
import base64
import hashlib
import datetime
import argparse
import random
import string
from utils import logging
from utils.krbcredccache import KrbCredCCache
from pyasn1.codec.der import decoder, encoder
from impacket.krb5.asn1 import KRB_CRED, EncKrbCredPart

# It took Dirkjan like 10 minutes to write this function... Let that sink in...
def makeccache(rb64):
    ccachefile = 'out.ccache'
    creds = decoder.decode(base64.b64decode(rb64), asn1Spec=KRB_CRED())[0]
    if creds['enc-part']['etype'] != 0:
        raise Exception('Ticket info is encrypted with cipher other than null')
    enc_part = decoder.decode(creds['enc-part']['cipher'], asn1Spec=EncKrbCredPart())[0]
    tinfo = enc_part['ticket-info']
    ccache = KrbCredCCache()
    # Enumerate all
    for i, tinfo in enumerate(tinfo):
        ccache.fromKrbCredTicket(creds['tickets'][i], tinfo)

    return ccache    

#Main
msg = logging.msg()
parser = argparse.ArgumentParser(prog='rubeus2ccache', formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('-i', '--inputfile', required=True, help="Rubeus dump output file.")
args = parser.parse_args()

if os.path.exists(args.inputfile) == False:
    msg.error("Input file does not exist. Check your path.")
    exit(1)

rawinput = open(args.inputfile)
tickets = []
savedtickets = 0
newticket = False
inticket = False
line = True 
while line:
    line = rawinput.readline()
    if newticket:
        if len(line.strip()) == 0 and inticket == False:
            # We are at the beginning of the b64 data. Continue past the new line
            continue
        elif len(line.strip()) > 0 and inticket == False:
            # First line of the ticket data. process the data
            inticket = True
            ticketdata += line.strip()
        elif len(line.strip()) > 0 and inticket == True:
            # In the body of the ticket data. process the data
            ticketdata += line.strip()
        elif len(line.strip()) == 0 and inticket == True:
            # We are at the end of the data. Stop processing
            inticket = False
            newticket = False
            #print(ticketdata)
            tickets.append(ticketdata)
        else:
            # Should never get here. Throw an error
            raise Exception("You're in a block you should never be in. Fix & submit a PR. thx")
        
    if 'Base64EncodedTicket' in line: 
        newticket = True
        ticketdata = ""
    
rawinput.close()

if os.path.exists("./output") == False:
    os.mkdir("./output")

for t in tickets:
    ccache = makeccache(t)
    clientname = ccache.credentials[0].header.fields['client'].components[0].fields['data']
    endtimeutc = ccache.credentials[0].header.fields['time'].fields['endtime']
    renewutc = ccache.credentials[0].header.fields['time'].fields['renew_till']
    realm = ccache.credentials[0].header.fields['server'].realm.fields['data']
    endtimefileformat = datetime.datetime.utcfromtimestamp(endtimeutc).strftime('%m-%d-%Y-%H-%M-%S')
    endtimelogformat = datetime.datetime.utcfromtimestamp(endtimeutc).strftime('%m-%d-%Y %H:%M:%S')
    renewlogformat = datetime.datetime.utcfromtimestamp(renewutc).strftime('%m-%d-%Y %H:%M:%S')
    rando = ''.join(random.choices(string.ascii_letters, k=5))
    ccachename = clientname + "-" + endtimefileformat + "-" + realm + "_" + rando + ".ccache"

    if datetime.datetime.utcfromtimestamp(endtimeutc) > datetime.datetime.utcnow():
        message = "Parsed ticket. ClientName: {0} Realm: {1} EndTime: {2}. RenewTill: {3}".format(clientname, realm, endtimelogformat, renewlogformat)
        msg.ok(message)
        ccache.saveFile("./output/" + ccachename)
        savedtickets = savedtickets + 1
    else: 
        message = "Expired ticket. ClientName: {0} Realm: {1} EndTime: {2}. RenewTill: {3}".format(clientname, realm, endtimelogformat, renewlogformat)
        msg.error(message)

msg.success("Processed " + str(len(tickets)) + " Tickets. " + str(savedtickets) + " ccache files saved to ./output")
