##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import logging
import asyncore
import errno
import os
import socket
import string
import struct
import sys
import threading
import zc.icp.interfaces
import zope.component

ICP_OP_INVALID = 0
ICP_OP_QUERY = 1
ICP_OP_HIT = 2
ICP_OP_MISS = 3
ICP_OP_ERR = 4
ICP_OP_SECHO = 10
ICP_OP_DECHO = 11
ICP_OP_MISS_NOFETCH = 21
ICP_OP_DENIED = 22

HEADER_LAYOUT = '!BBHIIII'
RESPONSE_LAYOUT = '%ds'
QUERY_LAYOUT = 'I' + RESPONSE_LAYOUT
MAX_DATAGRAM_LOG_LENGTH = 70

def check_url(url):
    policies = zope.component.getUtilitiesFor(zc.icp.interfaces.IICPPolicy)
    for name, policy in sorted(policies):
        result = policy(url)
        if result is not None:
            return result

    return 'ICP_OP_MISS'


def print_datagram(datagram):
    try:
        return format_datagram(datagram)
    except:
        return repr(datagram)


def handle_request(datagram, check_url=check_url):
    log_message = None
    out_header = HEADER_LAYOUT + RESPONSE_LAYOUT % 1
    out_group = [ICP_OP_ERR, 2, len(datagram), 0, 0, 0, 0, '\0']
    try:
        in_group = list(struct.unpack(HEADER_LAYOUT, datagram[:20]))
        opcode, version, length, number, options, opdata, sender_ip = in_group
    except struct.error:
        log_message = 'Error unpacking ICP header'
    else:
        out_group[2:4] = [struct.calcsize(out_header), number]
        if version == 2 and length == len(datagram) and length <= 16384:
            if opcode == ICP_OP_QUERY:
                if length > 24:
                    try:
                        (requester_ip, url) = struct.unpack(
                            '!' + QUERY_LAYOUT % (length - 24), datagram[20:])
                    except:
                        log_message = 'Error unpacking ICP query'
                    else:
                        in_group.extend([requester_ip, url])
                        out_header = HEADER_LAYOUT + RESPONSE_LAYOUT % len(url)
                        out_group[2] = struct.calcsize(out_header)
                        out_group[6:] = [sender_ip, url]
                        if url[-1:] == '\x00':
                            out_group[0] = globals()[check_url(url[:-1])]
                        else:
                            log_message = (
                                'URL in ICP query is not null-terminated')
                else:
                    log_message = 'Query is not long enough'

    if log_message:
        if len(datagram) > MAX_DATAGRAM_LOG_LENGTH:
            chunk_size = MAX_DATAGRAM_LOG_LENGTH / 2
            log_gram = datagram[:chunk_size] + '...' + datagram[-chunk_size:]
        else:
            log_gram = datagram

        logging.error('%s:\n    %r' % (log_message, log_gram))

    result = struct.pack(out_header, *out_group)
    return result

# We want our own, independent map for running an asyncore mainloop.
asyncore_map = {}

class ICPServer(asyncore.dispatcher):

    REQUESTS_PER_LOOP = 4

    def __init__(self, ip, port):
        asyncore.dispatcher.__init__(self, map=asyncore_map)
        self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.set_reuse_addr()
        self.bind((ip, port))
        if ip=='':
            addr = 'any'
        else:
            addr = ip

        self.log_info(
            'ICP server started\n\tAddress: %s\n\tPort: %s' % (addr, port))

    def handle_read(self):
        for i in range(self.REQUESTS_PER_LOOP):
            try:
                datagram, whence = self.socket.recvfrom(16384)
            except socket.error, e:
                if e[0] == errno.EWOULDBLOCK:
                    break
                else:
                    raise
            else:
                reply = handle_request(datagram)
                if reply:
                    self.socket.sendto(reply, whence)

    def readable(self):
        return 1

    def writable(self):
        return 0

    def handle_connect(self):
        pass

    def handle_write(self):
        self.log_info('unexpected write event', 'warning')

    def handle_error(self):
        # don't close the socket on error
        (file, fun, line), t, v, tbinfo = asyncore.compact_traceback()
        self.log_info('Problem in ICP (%s:%s %s)' % (t, v, tbinfo), 'error')


def start_server(ip='', port=3130):
    server = ICPServer(ip, port)
    thread = threading.Thread(target=asyncore.loop,
        kwargs=dict(map=asyncore_map))
    thread.setDaemon(True)
    thread.start()


template = """\
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  %-13s|   Version: %-3s|     Message Length: %-10s|
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Request Number: %-27X|
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Options: %-34X|
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Option Data: %-30X|
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Sender Host Address: %-22s|
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
|    Payload: %-50s|
|                                                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+"""

reverse_opcode_map = {
    0: 'ICP_OP_INVALID',
    1: 'ICP_OP_QUERY',
    2: 'ICP_OP_HIT',
    3: 'ICP_OP_MISS',
    4: 'ICP_OP_ERR',
    10: 'ICP_OP_SECHO',
    11: 'ICP_OP_DECHO',
    21: 'ICP_OP_MISS_NOFETCH',
    22: 'ICP_OP_DENIED',
    }

def format_datagram(datagram):
    header_size = struct.calcsize(HEADER_LAYOUT)
    parts = list(struct.unpack(HEADER_LAYOUT, datagram[:header_size]))
    parts[0] = reverse_opcode_map[parts[0]]
    payload = repr(datagram[header_size:])[1:-1]
    parts.append(payload)
    return template % tuple(parts)
