# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from behave import then, when
from hamcrest import assert_that, is_
from xivo_test_helpers import until

from wazo_calld_client import Client as CalldClient


@then('"{firstname} {lastname}" call is "{status}"')
def then_firstname_lastname_call_is_status(context, firstname, lastname, status):
    user_uuid = context.helpers.confd_user.get_by(firstname=firstname, lastname=lastname)['uuid']
    _assert_call_property(context, user_uuid, call_property=status, property_value=True)


@then('"{firstname} {lastname}" call is not "{status}"')
def then_firstname_lastname_call_is_not_status(context, firstname, lastname, status):
    user_uuid = context.helpers.confd_user.get_by(firstname=firstname, lastname=lastname)['uuid']
    _assert_call_property(context, user_uuid, call_property=status, property_value=False)


@when('"{firstname} {lastname}" relocates its call to its contact "{contact_number}"')
def when_firstname_lastname_relocates_its_call_to_its_contact_number(
    context, firstname, lastname, contact_number
):
    tracking_id = "{} {}".format(firstname, lastname)

    token_uuid = context.helpers.token.get(tracking_id)['token']
    calld_client = CalldClient(**context.wazo_config['calld'])
    calld_client.set_token(token_uuid)

    contact = int(contact_number) - 1
    dst_line_sip = context.phone_register.get_phone(tracking_id, contact)
    dst_line_sip_username = dst_line_sip.sip_username

    dst_lines = context.confd_client.lines.list(search=dst_line_sip_username, recurse=True)
    dst_line_id = dst_lines['items'][0]['id']

    current_call_id = calld_client.calls.list_calls_from_user()['items'][0]['call_id']
    calld_client.relocates.create_from_user(
        initiator=current_call_id,
        destination='line',
        location={'line_id': dst_line_id, 'contact': dst_line_sip_username},
    )


def _assert_call_property(context, user_uuid, call_property, property_value):
    def call_is_status():
        call = context.helpers.call.get_by(user_uuid=user_uuid)
        assert_that(call[call_property], is_(property_value))

    until.assert_(call_is_status, tries=3)
