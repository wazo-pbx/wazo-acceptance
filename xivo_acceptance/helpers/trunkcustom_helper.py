# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
# Copyright (C) 2016 Proformatique Inc.
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from lettuce import world


def add_or_replace_trunkcustom(interface):
    delete_trunkcustoms_with_interface(interface)
    add_trunkcustom(interface)


def add_trunkcustom(interface):
    trunk = world.confd_client.trunks.create({})
    endpoint_custom = world.confd_client.endpoints_custom.create({'interface': interface})
    world.confd_client.trunks(trunk).add_endpoint_custom(endpoint_custom)


def delete_trunkcustoms_with_interface(interface):
    endpoints_custom = world.confd_client.endpoints_custom.list(interface=interface)['items']
    for endpoint_custom in endpoints_custom:
        world.confd_client.endpoints_custom.delete(endpoint_custom['id'])
        if endpoint_custom['trunk']:
            world.confd_client.trunks.delete(endpoint_custom['trunk']['id'])
