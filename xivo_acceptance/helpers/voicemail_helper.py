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

from hamcrest import assert_that, is_not, none
from lettuce import world
from requests.exceptions import HTTPError

from xivo_acceptance.lettuce import postgres


def add_or_replace_voicemail(parameters):
    delete_similar_voicemails(parameters)
    return create_voicemail(parameters)


def delete_similar_voicemails(parameters):
    if 'number' in parameters:
        number = parameters['number']
        context = parameters.get('context', 'default')
        voicemail = find_voicemail_by_number(number, context)
        if voicemail:
            delete_voicemail(voicemail['id'])


def create_voicemail(parameters):
    return world.confd_client.voicemails.create(parameters)


def delete_voicemail(voicemail_id):
    _delete_associations(voicemail_id)
    _delete_voicemail(voicemail_id)


def _delete_associations(voicemail_id):
    user_id = find_user_id_for_voicemail(voicemail_id)
    if user_id:
        world.confd_client.users(user_id).remove_voicemail()


def _delete_voicemail(voicemail_id):
    world.confd_client.voicemails.delete(voicemail_id)


def find_user_id_for_voicemail(voicemail_id):
    query = """
    SELECT
        id
    FROM
        userfeatures
    WHERE
        voicemailid = :voicemail_id
    """

    result = postgres.exec_sql_request(query, voicemail_id=voicemail_id)
    return result.scalar()


def find_voicemail_by_user_id(user_id):
    try:
        return world.confd_client.users(user_id).get_voicemail()['voicemail_id']
    except HTTPError:
        return None


def find_voicemail_by_number(number, context='default'):
    voicemails = world.confd_client.voicemails.list(number=number, context=context)['items']
    return voicemails[0] if voicemails else None


def get_voicemail_by_number(number, context='default'):
    voicemail = find_voicemail_by_number(number, context)
    assert_that(voicemail, is_not(none()),
                "voicemail %s@%s not found" % (number, context))
    return voicemail
