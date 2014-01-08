# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from xivo_acceptance.helpers import user_helper


@step(u'Given there is a call center supervisor "([^"]*)" "([^"]*)"')
def given_there_is_a_call_center_supervisor_firstname_lastname(step, firstname, lastname):
    user_data = {
        'firstname': firstname,
        'lastname': lastname,
        'client_profile': 'Supervisor',
        'client_username': firstname.lower(),
        'client_password': lastname.lower(),
        'enable_client': True,
    }
    user_helper.add_or_replace_user(user_data)
