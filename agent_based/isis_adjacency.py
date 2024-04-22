#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# Checks based on the ISIS-MIB.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#
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


from typing import List, Dict, Union
import ipaddress
from cmk.base.plugins.agent_based.agent_based_api.v1 import (
    register,
    SNMPTree,
    exists,
    Service,
    Result,
    State,
    ServiceLabel
)


def parse_isis_adjacency(string_table):
    parsed = {}
    adjacency = {}
    last_state = None

    for (adj_state, adj_address) in string_table:
        if adj_state != '':
            last_state = int(adj_state)

        elif adj_address != '':
            adj_address_bytes = bytes([ord(x) for x in adj_address])
            adj_ip_address = ipaddress.ip_address(adj_address_bytes)
            if len(adj_address) == 4:
                adjacency['Neighbor IPv4'] = adj_ip_address.compressed
                adjacency['State'] = last_state
                parsed[adjacency['Neighbor IPv4']] = adjacency
                adjacency = {}
            elif len(adj_address) == 16:
                adjacency['Neighbor IPv6'] = adj_ip_address.compressed
                adjacency['State'] = last_state
                parsed[adjacency['Neighbor IPv6']] = adjacency
                adjacency = {}
            else:
                continue

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


class ISISAdjacencyDiscoveryParams:
    def __init__(self, params) -> None:
        self.subnets: List[ipaddress.ip_network] = [
            ipaddress.ip_network(subnet)
            for subnet in params.get("subnets")["subnets"]
        ]
        self.negate: bool = params.get("subnets")["negate"]
        self.my_labels: Union[List[ServiceLabel], None] = [
            ServiceLabel(k, v)
            for k, v in params.get("labels").items()
        ] if params.get("labels") else None

    def discover(self, ip_address: str) -> bool:
        ip = ipaddress.ip_address(ip_address)
        for subnet in self.subnets:
            print("subnet: ", subnet, "ip: ", ip, "negate: ", self.negate)
            if ip in subnet:
                return not self.negate
        return self.negate

    @property
    def labels(self) -> Union[List[ServiceLabel], None]:
        return self.my_labels


def discover_isis_adjacency(params: List, section: Dict):
    discovery_rules = [
        ISISAdjacencyDiscoveryParams(param) for param in params if param.get("subnets")
    ]
    for name, service in section.items():
        if discovery_rules:
            for rule in discovery_rules:
                if rule.discover(
                    service.get('Neighbor IPv4', service.get('Neighbor IPv6', ''))
                ):
                    yield Service(item=name, labels=rule.labels)
                    break
        else:
            yield Service(item=name)


def check_isis_adjacency(item, section):
    if item not in section:
        return

    state = int(section[item]['State'])

    if section[item].get('Neighbor IPv4'):
        address = section[item]['Neighbor IPv4']
    else:
        address = section[item]['Neighbor IPv6']
    summary = 'State with neighbor %s is %s' % (address, ISIS_ADJ_STATE_MAP[state])

    if state == 3:
        yield Result(state=State.OK, summary=summary)
    elif state == 2:
        yield Result(state=State.WARN, summary=summary)
    else:
        yield Result(state=State.CRIT, summary=summary)


register.check_plugin(
    name='isis_adjacency',
    service_name='IS-IS Status Neighbor %s',
    discovery_function=discover_isis_adjacency,
    check_function=check_isis_adjacency,
    discovery_ruleset_type=register.RuleSetType.ALL,
    discovery_default_parameters={},
    discovery_ruleset_name="isis_adjacency_discovery",
)
