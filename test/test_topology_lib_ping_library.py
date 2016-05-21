# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Hewlett Packard Enterprise Development LP
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
Test suite for Topology ping Communication Library.
"""

from __future__ import unicode_literals

from subprocess import check_output
from distutils.spawn import find_executable

from deepdiff import DeepDiff
from pytest import mark  # noqa

from topology_lib_ping.library import ping_parse, ping


def _enode(cmd, shell=None):
    """
    Helper - unckeched mock for the enode that will run the command on the
    host.

    FIXME: Improve!
    """
    return check_output(cmd, shell=True).decode('utf-8')


PING_RAW = """\
PING localhost (127.0.0.1) 56(84) bytes of data.
64 bytes from localhost (127.0.0.1): icmp_seq=1 ttl=64 time=0.069 ms
64 bytes from localhost (127.0.0.1): icmp_seq=2 ttl=64 time=0.066 ms
64 bytes from localhost (127.0.0.1): icmp_seq=3 ttl=64 time=0.067 ms
64 bytes from localhost (127.0.0.1): icmp_seq=4 ttl=64 time=0.063 ms
64 bytes from localhost (127.0.0.1): icmp_seq=5 ttl=64 time=0.064 ms
64 bytes from localhost (127.0.0.1): icmp_seq=6 ttl=64 time=0.065 ms
64 bytes from localhost (127.0.0.1): icmp_seq=7 ttl=64 time=0.064 ms
64 bytes from localhost (127.0.0.1): icmp_seq=8 ttl=64 time=0.064 ms
64 bytes from localhost (127.0.0.1): icmp_seq=9 ttl=64 time=0.061 ms
64 bytes from localhost (127.0.0.1): icmp_seq=10 ttl=64 time=0.064 ms

--- localhost ping statistics ---
10 packets transmitted, 10 received, 0% packet loss, time 9000ms
rtt min/avg/max/mdev = 0.061/0.064/0.069/0.009 ms
"""


def test_ping_parse():
    """
    Test that the ping_parse function works as expected.
    """
    result = ping_parse(PING_RAW)
    expected = {
        'received': 10,
        'errors': 0,
        'loss_pc': 0,
        'transmitted': 10,
        'time_ms': result.get('time_ms', -1)
    }

    ddiff = DeepDiff(result, expected)
    assert not ddiff


@mark.skipif(
    find_executable('ping') is None,
    reason='ping command unavailable'
)
def test_ping():
    result = ping(_enode, 10, '127.0.0.1', interval=0.5)
    expected = {
        'received': 10,
        'errors': 0,
        'loss_pc': 0,
        'transmitted': 10,
        'time_ms': result.get('time_ms', -1)
    }

    ddiff = DeepDiff(result, expected)
    assert not ddiff


@mark.skipif(
    find_executable('ping6') is None,
    reason='ping6 command unavailable'
)
def test_ping6():
    result = ping(_enode, 5, '::1', interval=0.6)
    expected = {
        'received': 5,
        'errors': 0,
        'loss_pc': 0,
        'transmitted': 5,
        'time_ms': result.get('time_ms', -1)
    }

    ddiff = DeepDiff(result, expected)
    assert not ddiff
