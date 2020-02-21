# Copyright 2019-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from requests import HTTPError


class ConfdUser:

    def __init__(self, context):
        self._context = context
        self._confd_client = context.confd_client

    def create(self, body):
        ring_seconds = body.pop('ring_seconds', None)
        if ring_seconds:
            body['ring_seconds'] = int(ring_seconds)

        with self._context.helpers.bus.wait_for_asterisk_reload(dialplan=True, pjsip=True, queue=True):
            user = self._confd_client.users.create(body)
        self._context.add_cleanup(self._confd_client.users.delete, user)
        return user

    def add_line(self, user, line):
        with self._context.helpers.bus.wait_for_asterisk_reload(dialplan=True, pjsip=True):
            self._confd_client.users(user).add_line(line)
        self._context.add_cleanup(self._confd_client.users(user).remove_line, line)

    def add_voicemail(self, user, voicemail):
        confd_user = self._confd_client.users(user)
        with self._context.helpers.bus.wait_for_asterisk_reload(pjsip=True):
            confd_user.add_voicemail(voicemail)
        self._context.add_cleanup(confd_user.remove_voicemail)

    def update_fallback(self, user, fallback):
        fallbacks = self._confd_client.users(user).list_fallbacks()
        old_fallbacks = fallbacks.copy()
        fallbacks.update(fallback)
        self._confd_client.users(user).update_fallbacks(fallbacks)
        self._context.add_cleanup(self._confd_client.users(user).update_fallbacks, old_fallbacks)

    def get_by(self, **kwargs):
        user = self._find_by(**kwargs)
        if not user:
            raise Exception('Confd user not found: {}'.format(kwargs))
        return user

    def import_users(self, csv):
        try:
            return self._confd_client.users.import_csv(csv)
        except HTTPError as e:
            return e.response

    def _find_by(self, **kwargs):
        users = self._confd_client.users.list(**kwargs)['items']
        for user in users:
            return user

    def update_funckeys(self, user, func_keys):
        with self._context.helpers.bus.wait_for_asterisk_reload(dialplan=True):
            self._confd_client.users(user).update_funckeys(func_keys)
