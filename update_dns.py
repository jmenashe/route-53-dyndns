#! /usr/bin/env python
"""
Updates a Route53 hosted A alias record with the current ip of the system,
as reported by ipify.org.
This script is a slight modification of Jacob Sanford's original work:
  https://github.com/JacobSanford/route-53-dyndns
"""
import boto.route53
import logging
import os, sys
from optparse import OptionParser
import re
from re import search
import socket

__author__ = "Jacob Menashe"
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Jacob Menashe"
__email__ = "jmenashe@gmail.com"
__status__ = "Development"

parser = OptionParser()
parser.add_option('-R', '--record', type='string', dest='record_to_update', help='The A record to update.')
parser.add_option('-v', '--verbose', dest='verbose', default=False, help='Enable Verbose Output.', action='store_true')
parser.add_option('-s', '--secure', dest='secure', default=False, help='Use a secure connection to the ip address provider.', action='store_true')
(options, args) = parser.parse_args()

if options.record_to_update is None:
    logging.error('Please specify an A record with the -R switch.')
    parser.print_help()
    sys.exit(-1)
if options.verbose:
    logging.basicConfig(
        level=logging.INFO,
		stream=sys.stdout
    )


# use ipify to get ip
from requests import get
protocol = 'https' if options.secure else 'http'
current_ip = get('%s://api.ipify.org' % protocol).text

record_to_update = options.record_to_update
zone_to_update = '.'.join(record_to_update.split('.')[-2:])

try:
    socket.inet_aton(current_ip)
    conn = boto.route53.connect_to_region(os.getenv('AWS_CONNECTION_REGION', 'us-east-1'))
    zone = conn.get_zone(zone_to_update)
    for record in zone.get_records():
        if search(r'<Record:' + record_to_update, str(record)):
            if current_ip in record.to_print():
                logging.info('Record IP matches, doing nothing.')
                sys.exit()
            logging.info('IP does not match, update needed.')
            zone.delete_a(record_to_update)
            zone.add_a(record_to_update, current_ip)
            sys.exit()
    logging.info('Record not found, add needed')
    zone.add_a(record_to_update, current_ip)
except socket.error:
    logging.info('Invalid IP format obtained from URL (' + current_ip + ')')
