# Copyright 2019-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import time
import random
import string

from behave import given, then, when
from hamcrest import assert_that, equal_to, is_


def random_string(length, sample=string.ascii_lowercase):
    return ''.join(random.choice(sample) for _ in range(length))


@given('there is an authentication user')
def given_there_is_a_user(context):
    context.username = random_string(10)
    context.password = random_string(10, sample=string.printable)

    body = {
        'firstname': random_string(10),
        'username': context.username,
        'password': context.password,
    }
    context.helpers.user.create(body)


@given('there are authentication users with info')
def given_there_are_authentication_users_with_info(context):
    for row in context.table:
        body = {
            'firstname': row['firstname'],
            'username': row['username'],
            'password': row['password'],
        }
        context.helpers.user.create(body)


def _check_user_exists(context, username):
    return context.helpers.user.find_by(username=username) is not None


@then('I see a user with username "{username}"')
def then_i_see_a_user_with_username(context, username):
    assert _check_user_exists(context, username)


@then('the user with username "{username}" does not exist')
def then_the_user_with_username_does_not_exist(context, username):
    assert not _check_user_exists(context, username)


@given('there are telephony users with infos')
def given_there_are_telephony_users_with_infos(context):
    context.table.require_columns(['firstname'])
    for row in context.table:
        body = row.as_dict()

        confd_user = context.helpers.confd_user.create(body)

        user_body = {
            'uuid': confd_user['uuid'],
            'firstname': body['firstname'],
            'lastname': body.get('lastname'),
            'username': body.get('username') or random_string(10),
            'password': body.get('password') or random_string(10, sample=string.printable),
        }
        context.helpers.user.create(user_body)
        tracking_id = "{} {}".format(body['firstname'], body.get('lastname', '')).strip()

        if body.get('with_token', 'no') == 'yes':
            context.helpers.token.create(user_body['username'], user_body['password'], tracking_id)

        if not body.get('context'):
            # User has no line
            continue

        line = context.helpers.line.create(body)

        endpoint = body.get('endpoint', 'sip')
        if endpoint == 'sip':
            name = '-'.join([body['firstname'], body.get('lastname', '')])
            sip_body = context.helpers.endpoint_sip.generate_form(name)
            sip = context.helpers.endpoint_sip.create(sip_body)
            context.helpers.line.add_endpoint_sip(line, sip)
        elif endpoint == 'sccp':
            raise NotImplementedError()
        elif endpoint == 'custom':
            raise NotImplementedError()

        if body.get('exten') and body.get('context'):
            extension = context.helpers.extension.create(body)
            context.helpers.line.add_extension(line, extension)

        application_name = body.get('application')
        if application_name:
            application = context.helpers.application.get_by(name=application_name)
            context.helpers.line.add_application(line, application)

        context.helpers.confd_user.add_line(confd_user, line)

        if body.get('device'):
            device = context.helpers.device.get_by(mac=body['device'])
            context.helpers.line.add_device(line, device)

        if (body.get('voicemail_name')
                and body.get('voicemail_number')
                and body.get('voicemail_context')):
            voicemail = context.helpers.voicemail.create({
                'name': body['voicemail_name'],
                'context': body['voicemail_context'],
                'number': body['voicemail_number']
            })
            context.helpers.confd_user.add_voicemail(confd_user, voicemail)

        if body.get('agent_number'):
            agent = context.helpers.agent.create({'number': body['agent_number']})
            context.confd_client.users(confd_user).add_agent(agent)

        if endpoint == 'sip' and body.get('with_phone', 'yes') == 'yes':
            expected_event = {'uuid': confd_user['uuid'], 'line_state': 'available'}
            with context.helpers.bus.wait_for_event('chatd_presence_updated', expected_event):
                context.helpers.sip_phone.register_and_track_phone(tracking_id, sip)


@given('"{firstname} {lastname}" has lines')
def given_user_has_lines(context, firstname, lastname):
    context.table.require_columns(['name', 'context'])
    confd_user = context.helpers.confd_user.get_by(firstname=firstname, lastname=lastname)
    tracking_id = "{} {}".format(firstname, lastname)
    for row in context.table:
        body = row.as_dict()

        line = context.helpers.line.create(body)

        endpoint = body.get('endpoint', 'sip')
        if endpoint == 'sip':
            name = '-'.join([firstname, lastname, body['name']])
            sip_body = context.helpers.endpoint_sip.generate_form(name, body.get('webrtc'))
            sip = context.helpers.endpoint_sip.create(sip_body)
            context.helpers.line.add_endpoint_sip(line, sip)
        else:
            raise NotImplementedError()

        if body.get('exten') and body['context']:
            extension = context.helpers.extension.find_by(
                exten=body['exten'],
                context=body['context'],
            )
            if not extension:
                extension = context.helpers.extension.create(body)
            context.helpers.line.add_extension(line, extension)

        context.helpers.confd_user.add_line(confd_user, line)

        if endpoint == 'sip' and body.get('with_phone', 'yes') == 'yes':
            expected_event = {'uuid': confd_user['uuid'], 'line_state': 'available'}
            with context.helpers.bus.wait_for_event('chatd_presence_updated', expected_event):
                context.helpers.sip_phone.register_and_track_phone(tracking_id, sip)


@given('"{firstname} {lastname}" has enabled "{dnd_name}" service')
def then_the_user_has_enabled_service(context, firstname, lastname, dnd_name):
    confd_user = context.helpers.confd_user.get_by(firstname=firstname, lastname=lastname)
    service = {'enabled': True}
    context.confd_client.users(confd_user).update_service(dnd_name, service)


@given('"{firstname} {lastname}" has schedule "{schedule}"')
def given_user_1_has_schedule_2(context, firstname, lastname, schedule):
    confd_user = context.helpers.confd_user.get_by(firtname=firstname, lastname=lastname)
    schedule = context.helpers.schedule.get_by(name=schedule)
    context.confd_client.users(confd_user).add_schedule(schedule['id'])


@given('"{firstname} {lastname}" has reconfigured the line "{exten}@{exten_context}"')
def when_i_reconfigure_the_phone_on_line(context, firstname, lastname, exten, exten_context):
    extension = context.helpers.extension.find_by(
        exten=exten,
        context=exten_context
    )
    line = context.confd_client.lines.get(extension['lines'][0]['id'])
    endpoint_sip = context.confd_client.endpoints_sip.get(line['endpoint_sip'])

    tracking_id = "{} {}".format(firstname, lastname)
    expected_event = {'line_state': 'available'}
    with context.helpers.bus.wait_for_event('chatd_presence_updated', expected_event):
        context.helpers.sip_phone.register_and_track_phone(tracking_id, endpoint_sip)


@given('"{firstname} {lastname}" has an "{forward_name}" forward set to "{exten}"')
def given_user_has_an_unconditional_forward_set_to_exten(context, firstname, lastname, forward_name, exten):
    confd_user = context.helpers.confd_user.get_by(firstname=firstname, lastname=lastname)
    forward = {'enabled': True, 'destination': exten}
    context.confd_client.users(confd_user).update_forward(forward_name, forward)


@then('"{firstname} {lastname}" has an "{forward_name}" forward set to "{exten}"')
def then_user_has_an_unconditional_forward_set_to_exten(context, firstname, lastname, forward_name, exten):
    confd_user = context.helpers.confd_user.get_by(firstname=firstname, lastname=lastname)
    forward = context.confd_client.users(confd_user).get_forward(forward_name)
    assert_that(forward['enabled'])
    assert_that(forward['destination'], equal_to(exten))


@then('"{firstname} {lastname}" has no "{forward_name}" forward')
def then_user_has_no_unconditional_forward(context, firstname, lastname, forward_name):
    confd_user = context.helpers.confd_user.get_by(firstname=firstname, lastname=lastname)
    forward = context.confd_client.users(confd_user).get_forward(forward_name)
    assert_that(forward['enabled'], is_(False))


@when('"{firstname} {lastname}" does a blind transfer to "{exten}@{exten_context}" with API')
def when_user_does_a_blind_transfer_to_exten_with_api(context, firstname, lastname, exten, exten_context):
    confd_user = context.helpers.confd_user.get_by(firstname=firstname, lastname=lastname)
    initiator_call = context.helpers.call.get_by(user_uuid=confd_user['uuid'])
    transferred_call_id = next(iter(initiator_call['talking_to']))
    context.calld_client.transfers.make_transfer(
        transferred=transferred_call_id,
        initiator=initiator_call['call_id'],
        context=exten_context,
        exten=exten,
        flow='blind'
    )


@when('I import the following users ignoring errors')
def when_i_import_users_ignoring_errors(context):
    lines = [','.join(context.table.headings)]
    for row in context.table:
        lines.append(','.join(row))
    csv = '\n'.join(lines)

    response = context.helpers.confd_user.import_users(csv)
    context.import_response = response


@then('my import result has an error on line "{line_number}"')
def then_my_import_result_matches(context, line_number):
    for error in context.import_response['errors']:
        if error['details']['row_number'] == int(line_number):
            return
    raise AssertionError('Line number not matched')


@when('"{firstname} {lastname}" does an attended transfer to "{exten}@{exten_context}" with API')
def when_user_does_an_attended_transfer_to_exten_with_api(context, firstname, lastname, exten, exten_context):
    confd_user = context.helpers.confd_user.get_by(firstname=firstname, lastname=lastname)
    initiator_call = context.helpers.call.get_by(user_uuid=confd_user['uuid'])
    transferred_call_id = next(iter(initiator_call['talking_to']))
    transfer = context.calld_client.transfers.make_transfer(
        transferred=transferred_call_id,
        initiator=initiator_call['call_id'],
        context=exten_context,
        exten=exten,
        flow='attended'
    )
    context.transfer_id = transfer['id']


@when('"{firstname} {lastname}" cancel the transfer with API')
def when_user_cancel_the_transfer_with_api(context, firstname, lastname):
    # NOTE: Use a user token to GET /users/me/transfers OR implement GET /transfers
    context.calld_client.transfers.cancel_transfer(context.transfer_id)


@when('"{firstname} {lastname}" complete the transfer with API')
def when_user_complete_the_transfer_with_api(context, firstname, lastname):
    # NOTE: Use a user token to GET /users/me/transfers OR implement GET /transfers
    context.calld_client.transfers.complete_transfer(context.transfer_id)


@given('"{firstname} {lastname}" has function keys')
def given_the_user_has_function_keys(context, firstname, lastname):
    confd_user = context.helpers.confd_user.get_by(firstname=firstname, lastname=lastname)
    func_keys = {'keys': {}}
    for row in context.table:
        body = row.as_dict()
        func_keys['keys'][f'{body["position"]}'] = _build_funckey(context, body)
    context.helpers.confd_user.update_funckeys(confd_user, func_keys)


def _build_funckey(context, row):
    type_ = row['destination_type']
    if type_ == 'forward':
        destination = {
            'type': type_,
            'forward': row['destination_forward'],
            'exten': row['destination_exten'] if row['destination_exten'] else None,
        }
    elif type_ == 'service':
        destination = {'type': type_, 'service': row['destination_service']}
    elif type_ == 'agent':
        agent = context.helpers.agent.get_by(number=row['destination_agent'])
        destination = {
            'type': type_,
            'agent_id': agent['id'],
            'action': row['destination_action'],
        }
    elif type_ == 'bsfilter':
        call_filter = context.helpers.call_filter.get_by(name=row['destination_filter_name'])
        firstname, lastname = row['destination_filter_member'].split(' ', 1)
        for user in call_filter['surrogates']['users']:
            if user['firstname'] == firstname and user['lastname'] == lastname:
                destination = {
                    'type': type_,
                    'filter_member_id': user['member_id'],
                }
                break

    return {
        'blf': row.get('blf') == 'true',
        'label': row.get('label'),
        'destination': destination,
    }


@when('"{firstname} {lastname}" disable all forwards')
def when_the_user_disable_all_forwards(context, firstname, lastname):
    confd_user = context.helpers.confd_user.get_by(firstname=firstname, lastname=lastname)
    forwards = {
        'busy': {'enabled': False},
        'noanswer': {'enabled': False},
        'unconditional': {'enabled': False},
    }
    context.confd_client.users(confd_user).update_forwards(forwards)


@when('"{firstname} {lastname}" enable forwarding on no-answer to "{exten}"')
def when_the_user_enable_forwarding_on_no_answer_to(context, firstname, lastname, exten):
    confd_user = context.helpers.confd_user.get_by(firstname=firstname, lastname=lastname)
    forward = {'destination': exten, 'enabled': True}
    context.confd_client.users(confd_user).update_forward('noanswer', forward)


@when('"{firstname} {lastname}" enable forwarding on busy to "{exten}"')
def when_the_user_enable_forwarding_on_busy_to(context, firstname, lastname, exten):
    confd_user = context.helpers.confd_user.get_by(firstname=firstname, lastname=lastname)
    forward = {'destination': exten, 'enabled': True}
    context.confd_client.users(confd_user).update_forward('busy', forward)


@when('"{firstname} {lastname}" enable unconditional forwarding to "{exten}"')
def when_the_user_enable_unconditional_forwarding_to(context, firstname, lastname, exten):
    confd_user = context.helpers.confd_user.get_by(firstname=firstname, lastname=lastname)
    forward = {'destination': exten, 'enabled': True}
    context.confd_client.users(confd_user).update_forward('unconditional', forward)


@when('"{firstname} {lastname}" enable DND')
def when_the_user_enable_dnd(context, firstname, lastname):
    confd_user = context.helpers.confd_user.get_by(firstname=firstname, lastname=lastname)
    service = {'enabled': True}
    context.confd_client.users(confd_user).update_service('dnd', service)


@when('"{firstname} {lastname}" disable DND')
def when_the_user_disable_dnd(context, firstname, lastname):
    confd_user = context.helpers.confd_user.get_by(firstname=firstname, lastname=lastname)
    service = {'enabled': False}
    context.confd_client.users(confd_user).update_service('dnd', service)


@when('"{firstname} {lastname}" enable incoming call filtering')
def when_the_user_enable_incoming_call_filtering(context, firstname, lastname):
    confd_user = context.helpers.confd_user.get_by(firstname=firstname, lastname=lastname)
    service = {'enabled': True}
    context.confd_client.users(confd_user).update_service('incallfilter', service)


@when('"{firstname} {lastname}" disable incoming call filtering')
def when_the_user_disable_incoming_call_filtering(context, firstname, lastname):
    confd_user = context.helpers.confd_user.get_by(firstname=firstname, lastname=lastname)
    service = {'enabled': False}
    context.confd_client.users(confd_user).update_service('incallfilter', service)


@when('"{firstname} {lastname}" press function key "{position}"')
def when_the_user_press_function_key(context, firstname, lastname, position):
    confd_user = context.helpers.confd_user.get_by(firstname=firstname, lastname=lastname)
    line = context.confd_client.lines.get(confd_user['lines'][0]['id'])
    device = context.provd_client.devices.get(line['device_id'])
    config = context.provd_client.configs.get(device['config'])
    exten = config['raw_config']['funckeys'][position]['value']
    tracking_id = f'{firstname} {lastname}'
    phone = context.phone_register.get_phone(tracking_id)
    phone.call(exten)


@given('"{firstname} {lastname}" enable call filter "{filter_name}"')
def when_the_user_active_call_filter(context, firstname, lastname, filter_name):
    call_filter = context.helpers.call_filter.get_by(name=filter_name)
    member_id = None
    for user in call_filter['surrogates']['users']:
        if user['firstname'] == firstname and user['lastname'] == lastname:
            member_id = user['member_id']
            break
    if not member_id:
        raise Exception('Surrogate not found: {} {}'.format(firstname, lastname))

    tracking_id = f'{firstname} {lastname}'
    phone = context.phone_register.get_phone(tracking_id)
    phone.call(f'*37{member_id}')
    time.sleep(5)  # call processing
