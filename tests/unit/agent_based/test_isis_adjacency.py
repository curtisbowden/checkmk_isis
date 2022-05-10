#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# Checks based on the ISIS-MIB.
#
# Copyright (C) 2022 Curtis Bowden <curtis.bowden@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import pytest  # type: ignore[import]
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    Result,
    Service,
    State,
)
from cmk.base.plugins.agent_based import isis_adjacency


@pytest.mark.parametrize('string_table, result', [
    (
        [['3', ''], ['', 'À¨\x00\x01'], ['', 'þ\x80\x00\x00\x00\x00\x00\x00\x8c!³\x16}N©Ý'], ['3', ''], ['', '\n\x00\x00\x01'], ['', 'þ\x80\x00\x00\x00\x00\x00\x00C¨¼\x11\x83\x9c\x88,']],
        {
            '10.0.0.1': {'Neighbor IPv4': '10.0.0.1', 'State': 3},
            '192.168.0.1': {'Neighbor IPv4': '192.168.0.1', 'State': 3}
        }
    ),
])
def test_parse_isis_adjacency(string_table, result):
    assert isis_adjacency.parse_isis_adjacency(string_table) == result


@pytest.mark.parametrize('section, result', [
    (
        {
            '10.0.0.1': {'Neighbor IPv4': '10.0.0.1', 'State': 3},
            '192.168.0.1': {'Neighbor IPv4': '192.168.0.1', 'State': 3}
        },
        [Service(item='10.0.0.1'), Service(item='192.168.0.1')]
    ),
])
def test_discover_isis_adjacency(section, result):
    assert list(isis_adjacency.discover_isis_adjacency(section)) == result


@pytest.mark.parametrize('item, section, result', [
    ('', {}, []),
    (
        'foo',
        {
            '10.0.0.1': {'Neighbor IPv4': '10.0.0.1', 'State': 3},
            '192.168.0.1': {'Neighbor IPv4': '192.168.0.1', 'State': 3}
        },
        []
    ),
    (
        '10.0.0.1',
        {
            '10.0.0.1': {'Neighbor IPv4': '10.0.0.1', 'State': 3},
            '192.168.0.1': {'Neighbor IPv4': '192.168.0.1', 'State': 1}
        },
        [Result(state=State.OK, summary='State with neighbor 10.0.0.1 is up')]
    ),
    (
        '10.0.0.1',
        {
            '10.0.0.1': {'Neighbor IPv4': '10.0.0.1', 'State': 1},
            '192.168.0.1': {'Neighbor IPv4': '192.168.0.1', 'State': 3}
        },
        [Result(state=State.CRIT, summary='State with neighbor 10.0.0.1 is down')]
    ),
])
def test_check_isis_adjacency(monkeypatch, item, section, result):
    assert list(isis_adjacency.check_isis_adjacency(item, section)) == result