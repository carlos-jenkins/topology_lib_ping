# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
topology_lib_ping communication library implementation.
"""

from __future__ import unicode_literals, absolute_import
from __future__ import print_function, division

from re import match

from ipaddress import ip_address


PING_RE = (
    r'^(?P<transmitted>\d+) packets transmitted, '
    r'(?P<received>\d+) received,'
    r'( \+(?P<errors>\d+) errors,)? '
    r'(?P<loss_pc>\d+)% packet loss, '
    r'time (?P<time_ms>\d+)ms$'
)

PROCESS_RE = (
    r'\[\w*\] (?P<process>\d+)'
)


def ping(enode, count, destination, save_file=False, background=False, interval=None, shell=None):
    """
    Perform a ping and parse the result.

    :param enode: Engine node to communicate with.
    :type enode: topology.platforms.base.BaseNode
    :param int count: Number of packets to send.
    :param str destination: The destination host.
    :param bool background: Use & to send background
    :param bool save_file: Save file into tmp
    :param float interval: The wait interval in seconds between each packet.
    :param str shell: Shell name to execute commands. If ``None``, use the
     Engine Node default shell.
    :rtype: dict
    :return: The parsed result of the ping command in a dictionary of the form:

     ::

        {
            'transmitted': 0,
            'received': 0,
            'errors': 0,
            'loss_pc': 0,
            'time_ms': 0
        }
    """
    assert count > 0
    assert destination

    addr = ip_address(destination)
    cmd = 'ping'
    if addr.version == 6:
        cmd = 'ping6'

    cmd = [cmd, '-c', str(count), destination]
    if interval is not None:
        assert interval > 0
        cmd.append('-i')
        cmd.append(str(interval))

    if save_file is True:
        cmd.append('>> /tmp/ping.txt')

    if background is True:
        cmd.append('&')

    ping_raw = enode(' '.join(cmd), shell=shell)
    assert ping_raw

    for line in ping_raw.splitlines():
        if save_file is True and background is True:
            m = match(PROCESS_RE, line)
        else:
            m = match(PING_RE, line)
        if m:
            return {
                k: (int(v) if v is not None else 0)
                for k, v in m.groupdict().items()
            }

    raise Exception('Could not parse ping result')


__all__ = ['ping']
