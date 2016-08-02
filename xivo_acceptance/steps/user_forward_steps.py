# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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


from lettuce import step
from lettuce.registry import world

from xivo_acceptance.helpers import user_helper


@step(u'Given user "([^"]*)" has (enabled|disabled) "([^"]*)" forward to "([^"]*)"')
def given_user_has_forward_to(step, fullname, enabled, forward_name, destination):
    user_uuid = user_helper.get_user_by_name(fullname)['uuid']
    forward = {'enabled': enabled == 'enabled', 'destination': destination}
    world.confd_client.users(user_uuid).update_forward(forward_name, forward)
