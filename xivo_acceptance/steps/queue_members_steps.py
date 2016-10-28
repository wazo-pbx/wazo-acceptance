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
from hamcrest import assert_that, has_entries
from lettuce import step, world

from xivo_acceptance.helpers import queue_helper, agent_helper


@step(u'When I request the following queue member:')
def when_i_request_the_following_queue_member(step):
    infos = complete_queue_member_infos(step.hashes[0])
    world.response = world.confd_client.queues.get_membership(infos['queue_id'], infos['agent_id'])


@step(u'When I edit the following queue member:')
def when_i_edit_the_following_queue_member(step):
    infos = complete_queue_member_infos(step.hashes[0])
    world.response = world.confd_client.queues.edit_membership(infos['queue_id'],
                                                               infos['agent_id'],
                                                               infos['penalty'])


@step(u'Then I get a queue membership with the following parameters:')
def then_i_get_a_queue_membership_with_the_following_parameters(step):
    queue_member = world.response.data
    expected_result = extract_queue_member(step.hashes[0])
    assert_that(queue_member, has_entries(expected_result))


@step(u'When I associate the following agent:')
def when_i_associate_the_following_agent(step):
    infos = complete_queue_member_infos(step.hashes[0])
    world.response = world.confd_client.queues.add_agent(infos['queue_id'],
                                                         infos['agent_id'],
                                                         infos['penalty'])


@step(u'When I remove the following agent from a queue:')
def when_i_remove_the_following_agent_from_a_queue(step):
    infos = complete_queue_member_infos(step.hashes[0])
    world.response = world.confd_client.queues.remove_agent(infos['queue_id'], infos['agent_id'])


def extract_queue_member(orig):
    return {'penalty': int(orig['penalty'])}


def complete_queue_member_infos(infos):
    result = {}
    if 'queue_name' in infos:
        result['queue_id'] = queue_helper.find_queue_id_with_name(infos['queue_name'])
    else:
        result['queue_id'] = infos['queue_id']
    if 'agent_number' in infos:
        result['agent_id'] = agent_helper.find_agent_id_with_number(infos['agent_number'])
    else:
        result['agent_id'] = int(infos['agent_id'])
    if 'penalty' in infos:
        result['penalty'] = int(infos['penalty'])
    return result
