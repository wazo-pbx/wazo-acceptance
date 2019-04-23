# -*- coding: utf-8 -*-
# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import time

from hamcrest import assert_that
from hamcrest import contains
from hamcrest import contains_inanyorder
from hamcrest import empty
from hamcrest import has_entries
from hamcrest import has_key
from lettuce import step, world

from xivo_acceptance.helpers import asterisk_helper
from xivo_acceptance.helpers import bus_helper
from xivo_acceptance.helpers import voicemail_helper


@step(u'When a message is left on voicemail "([^"]*)" by "([^"]*)"')
def when_a_message_is_left_on_voicemail(step, mailbox, cid_name):
    vm_number, vm_context = mailbox.split(u'@', 1)
    # start the call to the voicemail
    cmd = u'test newid leavevm *97{} {} 555 {} SIP'.format(vm_number, vm_context, cid_name)
    asterisk_helper.send_to_asterisk_cli(cmd)
    # press '#' to leave a message right away
    time.sleep(2)
    cmd = u'test dtmf SIP/auto-leavevm #'
    asterisk_helper.send_to_asterisk_cli(cmd)
    # hangup after leaving a small message
    time.sleep(2)
    cmd = u'channel request hangup SIP/auto-leavevm'
    asterisk_helper.send_to_asterisk_cli(cmd)


@step(u'When a message is checked and kept on voicemail "([^"]*)"')
def when_a_message_is_checked_and_kept_on_voicemail(step, mailbox):
    vm_number, vm_context = mailbox.split(u'@', 1)
    # start the call to the voicemail
    cmd = u'test newid checkvm *99{} {} 555 Test SIP'.format(vm_number, vm_context)
    asterisk_helper.send_to_asterisk_cli(cmd)
    # press '1' to listen to first message
    time.sleep(2)
    cmd = u'test dtmf SIP/auto-checkvm 1'
    asterisk_helper.send_to_asterisk_cli(cmd)
    # press '1' to skip announce
    time.sleep(1)
    cmd = u'test dtmf SIP/auto-checkvm 1'
    asterisk_helper.send_to_asterisk_cli(cmd)
    # hangup after hearing the message
    time.sleep(2)
    cmd = u'channel request hangup SIP/auto-checkvm'
    asterisk_helper.send_to_asterisk_cli(cmd)


@step(u'When a message is checked and deleted on voicemail "([^"]*)"')
def when_a_message_is_checked_and_deleted_on_voicemail(step, mailbox):
    vm_number, vm_context = mailbox.split(u'@', 1)
    # start the call to the voicemail
    cmd = u'test newid checkvm *99{} {} 555 Test SIP'.format(vm_number, vm_context)
    asterisk_helper.send_to_asterisk_cli(cmd)
    # press '1' to listen to first message
    time.sleep(2)
    cmd = u'test dtmf SIP/auto-checkvm 1'
    asterisk_helper.send_to_asterisk_cli(cmd)
    # press '1' to skip announce
    time.sleep(1)
    cmd = u'test dtmf SIP/auto-checkvm 1'
    asterisk_helper.send_to_asterisk_cli(cmd)
    # press '7' to delete the message
    time.sleep(1)
    cmd = u'test dtmf SIP/auto-checkvm 7'
    asterisk_helper.send_to_asterisk_cli(cmd)
    # hangup
    time.sleep(1)
    cmd = u'channel request hangup SIP/auto-checkvm'
    asterisk_helper.send_to_asterisk_cli(cmd)


@step(u'Then I receive a voicemail message event "([^"]*)" on the queue "([^"]*)" with data')
def then_i_receive_a_voicemail_message_event_on_queue(step, event_name, queue_name):
    events = bus_helper.get_messages_from_bus(queue_name)
    assert_that(events, contains(has_entries({'name': event_name, 'data': has_key('message')})))
    message = _flatten_message(events[0]['data']['message'])
    assert_that(message, has_entries(step.hashes.first))


@step(u'Then there\'s the following messages in voicemail "([^"]*)"')
def then_there_is_the_following_messages_in_voicemail(step, mailbox):
    vm_number, vm_context = mailbox.split(u'@', 1)
    vm_conf = voicemail_helper.get_voicemail_by_number(vm_number, vm_context)
    voicemail = world.ctid_ng_client.voicemails.get_voicemail(vm_conf['id'])
    messages = _flatten_voicemail_messages(voicemail)
    expected_messages = [has_entries(row) for row in step.hashes]
    assert_that(messages, contains_inanyorder(*expected_messages))


@step(u'Then there\'s no message in voicemail "([^"]*)"')
def then_there_is_no_message_in_voicemail(step, mailbox):
    vm_number, vm_context = mailbox.split(u'@', 1)
    vm_conf = voicemail_helper.get_voicemail_by_number(vm_number, vm_context)
    voicemail = world.ctid_ng_client.voicemails.get_voicemail(vm_conf['id'])
    messages = _flatten_voicemail_messages(voicemail)
    assert_that(messages, empty())


def _flatten_voicemail_messages(voicemail):
    flat_messages = []
    for folder in voicemail['folders']:
        for message in folder['messages']:
            flat_message = dict(message)
            flat_message['folder_type'] = folder['type']
            flat_message['folder_name'] = folder['name']
            flat_message['folder_id'] = folder['id']
            flat_messages.append(flat_message)
    return flat_messages


def _flatten_message(message):
    flat_message = dict(message)
    folder = flat_message.pop('folder')
    flat_message['folder_type'] = folder['type']
    flat_message['folder_name'] = folder['name']
    flat_message['folder_id'] = folder['id']
    return flat_message


def _extract_voicemail_info_to_confd(row):
    voicemail = dict(row)

    if 'max_messages' in voicemail and voicemail['max_messages'] is not None and voicemail['max_messages'].isdigit():
        voicemail['max_messages'] = int(voicemail['max_messages'])

    for key in ['attach_audio', 'delete_messages', 'ask_password']:
        if key in voicemail:
            voicemail[key] = (voicemail[key] == 'true')

    return voicemail
