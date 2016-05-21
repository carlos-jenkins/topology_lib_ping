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
from os import devnull

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


def _ping_cmd(count, destination, interval):
    """
    Helper that allows to build a ping command with the base parameters.
    """
    assert count > 0
    assert destination
    assert interval is None or interval > 0

    addr = ip_address(destination)
    base_cmd = 'ping'
    if addr.version == 6:
        base_cmd = 'ping6'

    cmd = [base_cmd, '-c', str(count), destination]
    if interval is not None:
        cmd.append('-i')
        cmd.append(str(interval))

    return cmd


def ping_parse(raw_stdout):
    """
    Parse ping stdout.

    :param str raw_stdout: Ping stdout to be parsed.
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
    for line in raw_stdout.splitlines():
        m = match(PING_RE, line)
        if m:
            return {
                k: (int(v) if v is not None else 0)
                for k, v in m.groupdict().items()
            }

    raise Exception('Could not parse ping result')


def ping(enode, count, destination, interval=None, shell=None):
    """
    Perform a ping and parse the result.

    :param enode: Engine node to communicate with.
    :type enode: topology.platforms.base.BaseNode
    :param int count: Number of packets to send.
    :param str destination: The destination host.
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
    cmd = _ping_cmd(count, destination, interval)

    ping_raw = enode(' '.join(cmd), shell=shell)
    assert ping_raw

    return ping_parse(ping_raw)


def ping_background(
        enode, count, destination,
        filename=devnull, interval=None, shell=None):
    """
    Perform a ping and parse the result.

    :param enode: Engine node to communicate with.
    :type enode: topology.platforms.base.BaseNode
    :param int count: Number of packets to send.
    :param str destination: The destination host.
    :param str filename: Filename to redict the stdout of ping.
    :param float interval: The wait interval in seconds between each packet.
    :param str shell: Shell name to execute commands. If ``None``, use the
     Engine Node default shell.
    :rtype: int
    :return: The pid of the ping process.
    """
    assert filename

    cmd = _ping_cmd(count, destination, interval)
    cmd.append('>> {} &'.format(filename))

    pid = enode(' '.join(cmd), shell=shell)

    m = match(PROCESS_RE, pid)
    if not m:
        raise Exception('Could not parse ping pid')

    return int(m.groupdict()['process'])


__all__ = ['ping_parse', 'ping', 'ping_background']
