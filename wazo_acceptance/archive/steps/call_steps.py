# -*- coding: utf-8 -*-
# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import time

from hamcrest import (
assert_that,
equal_to,
is_,
not_,
)
from lettuce import step, world

from xivo_ctid_ng_client import Client as CtidNgClient
from xivo_acceptance.helpers import (
asterisk_helper,
line_read_helper,
sip_config,
sip_phone,
user_helper,
)
from xivo_acceptance.lettuce import common

from linphonelib import ExtensionNotFoundException

CHAN_PREFIX = 'PJSIP'


@step(u'chan_test hangs up "([^"]*)"$')
def when_chan_test_hangs_up(step, channelid):
    cmd = u'channel request hangup {}/auto-{}'.format(CHAN_PREFIX, channelid)
    asterisk_helper.send_to_asterisk_cli(cmd)


@step(u'(?:Given|When) "([^"]*)" calls "([^"]*)" and waits until the end$')
def when_a_calls_exten_and_waits_until_the_end(step, name, exten):
    phone = step.scenario.phone_register.get_user_phone(name)
    phone.call(exten)
    common.wait_until(phone.is_hungup, tries=10)


@step(u'When "([^"]*)" calls "([^"]*)" and wait for "([^"]*)" seconds')
def when_someone_calls_an_exten_and_wait_for_n_seconds(step, name, exten, tries):
    phone = step.scenario.phone_register.get_user_phone(name)
    phone.call(exten)
    common.wait_until(phone.is_hungup, tries=int(tries))


@step(u'(?:When|Given) "([^"]*)" answers$')
def a_answers(step, name):
    phone = step.scenario.phone_register.get_user_phone(name)
    phone.answer()


@step(u'When "([^"]*)" answers on its contact "([^"]*)"')
def when_group1_answers_on_its_contact_group2(step, name, contact):
    phone = step.scenario.phone_register.get_user_phone(name, int(contact) - 1)
    phone.answer()


@step(u'When "([^"]*)" hangs up')
def when_a_hangs_up(step, name):
    phone = step.scenario.phone_register.get_user_phone(name)
    phone.hangup()


@step(u'When "([^"]*)" puts (?:his|her) call on hold')
def when_a_puts_his_call_on_hold(step, name):
    phone = step.scenario.phone_register.get_user_phone(name)
    phone.hold()


@step(u'When "([^"]*)" resumes (?:his|her) call')
def when_a_resumes_his_call(step, name):
    phone = step.scenario.phone_register.get_user_phone(name)
    phone.resume()


@step(u'When I reconfigure the phone "([^"]*)" on line (\d+)@(\w+)')
def when_i_reconfigure_the_phone_1_on_line_2_3(step, name, exten, context):
    step.scenario.phone_register.remove(name)
    line = line_read_helper.find_with_exten_context(exten, context)
    endpoint_sip = world.confd_client.endpoints_sip.get(line['endpoint_sip']['id'])
    phone_config = sip_config.create_config(world.config, step.scenario.phone_register, endpoint_sip)

    def phone_is_registered():
        return sip_phone.register_line(phone_config)

    phone = common.wait_until(phone_is_registered)
    assert_that(phone, is_(not_(None)))
    step.scenario.phone_register.add_registered_phone(phone, name)


@step(u'When "([^"]*)" transfers "([^"]*)" to "([^"]*)" with timeout "([^"]*)" via xivo-ctid-ng')
def when_1_transfers_2_to_3_with_timeout_4_via_xivo_ctid_ng(self, initiator, transferred, recipient_exten, timeout):
    transferred_uuid = user_helper.get_user_by_name(transferred)['uuid']
    initiator_uuid = user_helper.get_user_by_name(initiator)['uuid']

    calls = world.ctid_ng_client.calls.list_calls()['items']

    transferred_calls = [call for call in calls if call['user_uuid'] == transferred_uuid]
    try:
        transferred_call_id = transferred_calls[0]['call_id']
    except KeyError:
        raise Exception('No call found for user {} with UUID {}'.format(transferred, transferred_uuid))
    initiator_calls = [call for call in calls if call['user_uuid'] == initiator_uuid]
    try:
        initiator_call_id = initiator_calls[0]['call_id']
    except KeyError:
        raise Exception('No call found for user {} with UUID {}'.format(initiator, initiator_uuid))

    world.ctid_ng_client.transfers.make_transfer(transferred=transferred_call_id,
                                                 initiator=initiator_call_id,
                                                 context='default',
                                                 exten=recipient_exten,
                                                 timeout=int(timeout))


@step(u'Then "([^"]*)" is talking$')
def then_group1_is_talking(step, user):
    phone = step.scenario.phone_register.get_user_phone(user)
    common.wait_until(phone.is_talking, tries=3)


@step(u'Then "([^"]*)" is talking to "([^"]*)" on its contact "([^"]*)"')
def then_a_is_talking_to_b_on_its_contact_n(step, name_1, name_2, contact):
    phone = step.scenario.phone_register.get_user_phone(name_1, int(contact) - 1)
    common.wait_until(phone.is_talking, tries=3)
    assert_that(phone.is_talking_to(name_2), equal_to(True))


@step(u'When "([^"]*)" relocate its call to its contact "([^"]*)"')
def when_user_relocate_its_call_to_its_contact_nth(step, name, position):
    user = user_helper.get_user_by_name(name)
    line_id = user['lines'][0]['id']
    calls = world.ctid_ng_client.calls.list_calls()
    call = None
    for call in calls['items']:
        if call['user_uuid'] == user['uuid']:
            break

    if not call:
        raise AssertionError('No call found for {}'.format(name))

    phone = step.scenario.phone_register.get_user_phone(name, int(position) - 1)
    contact = phone.sip_contact_uri

    destination = {
        'line_id': line_id,
        'contact': contact,
    }
    token = step.scenario.user_tokens.get(name)
    ctid_ng_client = CtidNgClient(token=token, **world.config['ctid_ng'])
    ctid_ng_client.relocates.create_from_user(call['call_id'], 'line', destination)


def _sleep(seconds):
    time.sleep(float(seconds))
