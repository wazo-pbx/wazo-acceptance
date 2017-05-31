# -*- coding: utf-8 -*-

# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
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


from hamcrest import all_of
from hamcrest import assert_that
from hamcrest import ends_with
from hamcrest import has_entries
from hamcrest import has_item
from hamcrest import has_property
from lettuce import step, world
from xivo_acceptance.helpers import call_logs_helper, cel_helper
from xivo_acceptance.helpers.datetime_helper import close_to
from xivo_acceptance.lettuce import assets, common, sysutils


@step(u'Given there are no call logs$')
def given_there_are_no_call_logs(step):
    call_logs_helper.delete_all()


@step(u'Given I have only the following CEL entries:')
def given_i_have_only_the_following_cel_entries(step):
    cel_helper.delete_all()
    cel_helper.insert_entries(step.hashes)


@step(u'Given there are a lot of unprocessed calls')
def given_there_are_a_lot_of_calls(step):
    sql_file_name = 'cel-extract.sql'
    server_dir = '/tmp'
    assets.copy_asset_to_server(asset=sql_file_name, serverpath=server_dir)
    remote_path = '%s/%s' % (server_dir, sql_file_name)

    cel_insertion_command = ['sudo', '-u', 'postgres', 'psql', 'asterisk', '-f', remote_path]
    world.ssh_client_xivo.check_call(cel_insertion_command)


@step(u'Given there are only the following call logs:')
def given_there_are_only_the_following_call_logs(step):
    call_logs_helper.delete_all()
    call_logs_helper.create_call_logs(step.hashes)


@step(u'When I generate call logs$')
def when_i_generate_call_logs(step):
    command = ['xivo-call-logs']
    sysutils.send_command(command)


@step(u'When I generate call logs using the last (\d+) unprocessed CEL entries$')
def when_i_generate_call_logs_using_the_last_unprocessed_1_cel_entries(step, cel_count):
    command = ['xivo-call-logs', '-c', cel_count]
    sysutils.send_command(command)


@step(u'When I generate call logs twice in parallel')
def when_i_generate_call_logs_twice_in_parallel(step):
    command = ['xivo-call-logs', '&', 'xivo-call-logs']
    world.command_output = world.ssh_client_xivo.out_err_call(command)


@step(u'When I ask for the list of CEL via WebService:')
def when_i_ask_for_the_list_of_cel_via_webservice(step):
    list_infos = step.hashes[0]
    id_beg = list_infos['id beg']
    world.response = world.ws.cels.search_by_id(id_beg)


@step(u'Then I get a list with the following CEL:')
def then_i_get_a_list_with_the_following_cel(step):
    for cel in step.hashes:
        assert_that(world.response, has_item(_is_cel(cel)))


def _is_cel(cel):
    matchers = [has_property(key, value) for (key, value) in cel.iteritems()]
    return all_of(*matchers)


@step(u'Then I see that call log generation is already running')
def then_i_see_that_call_log_generation_is_already_running(step):
    assert_that(world.command_output.rstrip(), ends_with('An other instance of ourself is probably running.'))


@step(u'Then I should have the following call logs:')
def then_i_should_have_the_following_call_logs(step):
    for entry in step.hashes:
        assert call_logs_helper.has_call_log(entry), "Corresponding call_log entry was not found : %s" % entry


@step(u'Then I have the last call log matching:')
def then_i_have_the_last_call_log_matching(step):
    expected = dict(step.hashes[0])
    expected_duration = int(expected.pop('duration', None))
    if expected.get('answered'):
        expected['answered'] = bool(expected['answered'])

    def _assert():
        actual = world.call_logd_client.cdr.list(direction='desc', limit=1)['items'][0]
        assert_that(actual, has_entries(expected))
        if expected_duration:
            assert_that(actual['duration'], close_to(expected_duration, 2))

    common.wait_until_assert(_assert, tries=5)


@step(u'Then I should not have the following call logs:')
def then_i_should_not_have_the_following_call_logs(step):
    for entry in step.hashes:
        assert not call_logs_helper.has_call_log(entry), "Corresponding call_log entry was found : %s" % entry
