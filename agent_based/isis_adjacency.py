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

# Example excerpt from SNMP data:
# snmpwalk of .1.3.6.1.2.1.138.1.6.1.1.2
# ISIS-MIB::isisISAdjState.1024.1 = INTEGER: up(3)
# ISIS-MIB::isisISAdjState.1096.1 = INTEGER: up(3)
#
# snmpwalk of .1.3.6.1.2.1.138.1.6.3.1.3
# ISIS-MIB::isisISAdjIPAddrAddress.1024.1.1 = Hex-STRING: C0 A8 00 01
# ISIS-MIB::isisISAdjIPAddrAddress.1024.1.2 = Hex-STRING: FE 80 00 00 00 00 00 00 8C 21 B3 16 7D 4E A9 DD
# ISIS-MIB::isisISAdjIPAddrAddress.1096.1.1 = Hex-STRING: 0A 00 00 01
# ISIS-MIB::isisISAdjIPAddrAddress.1096.1.2 = Hex-STRING: FE 80 00 00 00 00 00 00 43 A8 BC 11 83 9C 88 2C

from .agent_based_api.v1 import (
    register,
    SNMPTree,
    exists,
    Service,
    Result,
    State,
)


def parse_isis_adjacency(string_table):
    parsed = {}
    adjacency = {}

    for (adj_state, adj_address) in string_table:
        if adj_state != '':
            adjacency['State'] = int(adj_state)

        elif adj_address != '':
            if len(adj_address) == 4:
                adjacency['Neighbor IPv4'] = '.'.join(format(ord(x), 'd') for x in adj_address)
            else:
                continue

        if 'State' in adjacency and 'Neighbor IPv4' in adjacency:
            parsed[adjacency['Neighbor IPv4']] = adjacency
            adjacency = {}

    return parsed


register.snmp_section(
    name='isis_adjacency',
    detect=exists('.1.3.6.1.2.1.138.1.1.1.1.0'),
    fetch=SNMPTree(
        base='.1.3.6.1.2.1.138.1.6',
        oids=[
            '1.1.2',  # ISIS-MIB::isisISAdjState
            '3.1.3',  # ISIS-MIB::isisISAdjIPAddrAddress
        ],
    ),
    parse_function=parse_isis_adjacency,
)


ISIS_ADJ_STATE_MAP = {
    1: 'down',          # CRIT
    2: 'initializing',  # WARN
    3: 'up',            # OK
    4: 'failed',        # CRIT
}


def discover_isis_adjacency(section):
    for service in section.keys():
        yield Service(item=service)


def check_isis_adjacency(item, section):
    if item not in section:
        return

    state = int(section[item]['State'])
    address = section[item]['Neighbor IPv4']
    summary = 'State with neighbor %s is %s' % (address, ISIS_ADJ_STATE_MAP[state])

    if state == 3:
        yield Result(state=State.OK, summary=summary)
    elif state == 2:
        yield Result(state=State.WARN, summary=summary)
    else:
        yield Result(state=State.CRIT, summary=summary)


register.check_plugin(
    name='isis_adjacency',
    service_name='ISIS Status Neighbor %s',
    discovery_function=discover_isis_adjacency,
    check_function=check_isis_adjacency,
)
