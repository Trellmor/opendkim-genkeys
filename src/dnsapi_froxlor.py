# -*- coding: utf-8 -*-

#    OpenDKIM genkeys tool, Froxlor API
#    Copyright (C) 2022 Daniel Triendl <daniel@pew.cc>

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Uses the 'requests' package.

# Requires:
# dnsapi_data[0]        : API Endpoint
# dnsapi_domain_data[0] : API Key
# dnsapi_domain_data[1] : API Secret
# dnsapi_domain_data[2] : TTL in seconds, automatic if not specified
# key_data['plain']     : TXT record value in plain unquoted format

# POST URL: https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records

# Parameters:
# type    : 'TXT'
# name    : selector + '._domainkey.' + domain_suffix
# content : key_data['plain']
# ttl     : dnsapi_domain_data[1]

import datetime
import logging

import requests


def add( dnsapi_data, dnsapi_domain_data, key_data, debugging = False ):
    if len( dnsapi_data ) < 1:
        logging.error( "DNS API froxlor: API endpoint not configured" )
        return False,
    api_endpoint = dnsapi_data[0]
    if len( dnsapi_domain_data ) < 2:
        logging.error( "DNS API froxlor: domain data missing API data" )
        return False,
    api_key = dnsapi_domain_data[0]
    api_secret = dnsapi_domain_data[1]
    if len( dnsapi_domain_data ) > 2:
        try:
            ttl = int( dnsapi_domain_data[2] )
            if ttl < 300:
                ttl = 300
        except Exception:
            ttl = 18000
    else:
        ttl = 18000
    try:
        selector = key_data['selector']
        data = key_data['chunked']
        domain = key_data['domain']
    except KeyError as e:
        logging.error( "DNS API cloudflare: required information not present: %s", str( e ) )
        return False,
    if debugging:
        return True, key_data['domain'], selector
    
    hdr = {
        'Content-Type': 'application/json'
    }
    body = {
        'header': {
            'apikey': api_key,
            'secret': api_secret
        },
        'body': {
            'command': 'DomainZones.add',
            'params': {
                'domainname': domain,
                'record': selector + '._domainkey',
                'type': 'TXT',
                'content': data,
                'ttl': ttl
            }
        }
    }
    resp = requests.post( api_endpoint, json = body, headers = hdr )
    logging.info( "HTTP status: %d", resp.status_code )

    if resp.status_code == requests.codes.ok:
        success = resp.json()['status']
        if success == 200:
            result = True, key_data['domain'], selector, datetime.datetime.utcnow()
        else:
            result = False,
            logging.error( "DNS API cloudflare: failure:\n%s", resp.text )
    else:
        result = False,
        logging.error( "DNS API froxlor: HTTP error %d", resp.status_code )
        logging.error( "DNS API froxlor: error response body:\n%s", resp.text )

    return result


def delete( dnsapi_data, dnsapi_domain_data, record_data, debugging = False ):
    # TODO delete record
    return None
