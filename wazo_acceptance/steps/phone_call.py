# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import time

from behave import step, then, when
from hamcrest import (
    assert_that,
    calling,
    not_,
    raises,
)
from linphonelib import ExtensionNotFoundException
from xivo_test_helpers import until

CHAN_PREFIX = 'PJSIP'


@step('"{tracking_id}" calls "{exten}"')
def step_a_calls_exten(context, tracking_id, exten):
    phone = context.phone_register.get_phone(tracking_id)
    phone.call(exten)


@step('"{tracking_id}" is ringing')
def step_user_is_ringing(context, tracking_id):
    phone = context.phone_register.get_phone(tracking_id)
    until.true(phone.is_ringing, tries=3)


@step('"{tracking_id}" is ringing on its contact "{contact_number}"')
def step_user_is_ringing_on_contact_number(context, tracking_id, contact_number):
    phone = context.phone_register.get_phone(tracking_id, int(contact_number) - 1)
    until.true(phone.is_ringing, tries=3)


@step('"{tracking_id}" is holding')
def step_user_is_holding(context, tracking_id):
    phone = context.phone_register.get_phone(tracking_id)
    until.true(phone.is_holding, context, tries=3)


@step('"{tracking_id}" is hungup')
def step_user_is_hungup(context, tracking_id):
    phone = context.phone_register.get_phone(tracking_id)
    until.true(phone.is_hungup, tries=3)


@step('"{tracking_id}" is hungup immediately')
def step_user_is_hungup_immediately(context, tracking_id):
    phone = context.phone_register.get_phone(tracking_id)
    _sleep(1)
    phone.is_hungup()


@step('"{tracking_id}" is talking')
def step_user_is_talking(context, tracking_id):
    phone = context.phone_register.get_phone(tracking_id)
    until.true(phone.is_talking, tries=3)


@step('"{tracking_id}" is talking to "{callerid}"')
def step_user_is_talking_to(context, tracking_id, callerid):
    phone = context.phone_register.get_phone(tracking_id)
    until.true(phone.is_talking_to, callerid, tries=3)


@step('"{tracking_id}" is talking to "{other_party_id}" on its contact "{contact_number}"')
def step_user_is_talking_to_other_party_with_contact(context, tracking_id, other_party_id, contact_number):
    phone = context.phone_register.get_phone(tracking_id, int(contact_number) - 1)
    until.true(phone.is_talking, tries=3)
    assert_that(phone.is_talking_to(other_party_id))


@step('"{tracking_id}" answers')
def step_user_answers(context, tracking_id):
    phone = context.phone_register.get_phone(tracking_id)
    phone.answer()


@step('"{tracking_id}" answers on its contact "{contact_number}"')
def step_user_answers_on_its_contact(context, tracking_id, contact_number):
    phone = context.phone_register.get_phone(tracking_id, int(contact_number) - 1)
    phone.answer()


@step('"{tracking_id}" hangs up')
def step_user_hangs_up(context, tracking_id):
    phone = context.phone_register.get_phone(tracking_id)
    phone.hangup()


@step('"{tracking_id}" calls "{exten}" and waits until the end')
def step_a_calls_exten_and_waits_until_the_end(context, tracking_id, exten):
    phone = context.phone_register.get_phone(tracking_id)
    phone.call(exten)
    until.true(phone.is_hungup, tries=10)


@step('"{tracking_id}" calls "{exten}" and waits for "{time}" seconds')
def step_a_calls_exten_and_waits_for_x_seconds(context, tracking_id, exten, time):
    phone = context.phone_register.get_phone(tracking_id)
    phone.call(exten)
    until.true(phone.is_hungup, tries=int(time))


@step('"{tracking_id}" puts his call on hold')
def step_user_puts_call_on_hold(context, tracking_id):
    phone = context.phone_register.get_phone(tracking_id)
    phone.hold()


@step('"{tracking_id}" resumes his call')
def step_user_resumes_call(context, tracking_id):
    phone = context.phone_register.get_phone(tracking_id)
    phone.resume()


@when('a call is started')
def when_a_call_is_started(context):

    def _call(caller, callee, hangup, dial, talk_time=0, ring_time=0):
        caller_phone = context.phone_register.get_phone(caller)
        callee_phone = context.phone_register.get_phone(callee)
        first_to_hangup = caller_phone if hangup == 'caller' else callee_phone

        caller_phone.call(dial)
        _sleep(ring_time)
        callee_phone.answer()
        _sleep(talk_time)
        first_to_hangup.hangup()

    for call_info in context.table:
        _call(**call_info.as_dict())


@when('I wait "{seconds}" seconds')
@when('I wait "{seconds}" seconds for the call processing')
@when('I wait "{seconds}" seconds for the call processing with slow machine')
@when('I wait "{seconds}" seconds for the call to be forwarded')
@when('I wait "{seconds}" seconds for the end of ringing time')
@when('I wait "{seconds}" seconds for the timeout to not expire')
@when('I wait "{seconds}" seconds for wazo-calld load to drop')
@when('I wait "{seconds}" seconds to play unreachable message')
@when('I wait "{seconds}" seconds to simulate call center')
def when_i_wait_n_seconds(context, seconds):
    _sleep(seconds)


@then('"{tracking_id}" last dialed extension was not found')
def then_user_last_dialed_extension_was_not_found(context, tracking_id):
    # XXX(afournier): phone.last_call_result does not work here - the fact that the extension does
    # not exist is not a problem for linphone-daemon. It does not trigger an error.
    phone = context.phone_register.get_phone(tracking_id)
    assert_that(not_(phone.is_talking))


@when('chan_test calls "{exten}@{exten_context}" with id "{channel_id}"')
def when_chan_test_calls_with_id(context, exten, exten_context, channel_id):
    cmd = 'test newid {channel_id} {exten} {context} chan-test-num chan-test-name {prefix}'.format(
        channel_id=channel_id,
        exten=exten,
        context=exten_context,
        prefix=CHAN_PREFIX,
    )
    context.helpers.asterisk.send_to_asterisk_cli(cmd)


@when('chan_test calls "{exten}@{exten_context}"')
def when_chan_test_calls(context, exten, exten_context):
    cmd = 'test new {exten} {context} chan-test-num chan-test-name {prefix}'.format(
        exten=exten,
        context=exten_context,
        prefix=CHAN_PREFIX,
    )
    context.helpers.asterisk.send_to_asterisk_cli(cmd)


@when('chan_test queues DTMF "{digit}" on channel with id "{channel_id}"')
def when_chan_test_queues_dtmf(context, digit, channel_id):
    cmd = 'test dtmf {prefix}/auto-{channel_id} {digit}'.format(
        prefix=CHAN_PREFIX,
        channel_id=channel_id,
        digit=digit,
    )
    context.helpers.asterisk.send_to_asterisk_cli(cmd)


@when('chan_test hangs up channel with id "{channel_id}"')
def when_chan_test_hangs_up_channel_with_id(context, channel_id):
    cmd = 'channel request hangup {prefix}/auto-{channel_id}'.format(
        prefix=CHAN_PREFIX,
        channel_id=channel_id,
    )
    context.helpers.asterisk.send_to_asterisk_cli(cmd)


@when('incoming call received from "{incall_name}" to "{exten}@{exten_context}"')
@when('incoming call received from "{incall_name}" to "{exten}@{exten_context}" with callerid "{callerid}"')
def when_incoming_call_received_from_name_to_exten(context, incall_name, exten, exten_context, callerid=None):
    body = {'context': exten_context}
    trunk = context.helpers.trunk.create(body)
    template = context.helpers.endpoint_sip.get_template_by(label='global')
    body = {
        'name': incall_name,
        'auth_section_options': [
            ['username', incall_name],
            ['password', incall_name],
        ],
        'endpoint_section_options': [],
        'templates': [template],
    }
    if callerid:
        body['endpoint_section_options'].append(['callerid', callerid])
    sip = context.helpers.endpoint_sip.create(body)
    context.helpers.trunk.add_endpoint_sip(trunk, sip)
    phone = context.helpers.sip_phone.register_and_track_phone(incall_name, sip)
    until.true(phone.is_registered, tries=3)
    phone.call(exten)


def _sleep(seconds):
    time.sleep(float(seconds))
