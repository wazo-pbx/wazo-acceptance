# Copyright 2019-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class Extension:

    def __init__(self, context):
        self._context = context
        self._confd_client = context.confd_client

    def create(self, body):
        body.setdefault('context', 'default')
        with self._context.helpers.bus.wait_for_asterisk_reload(dialplan=True):
            extension = self._confd_client.extensions.create(body)
        self._context.add_cleanup(self._confd_client.extensions.delete, extension)
        return extension

    def get_by(self, **kwargs):
        extension = self.find_by(**kwargs)
        if not extension:
            raise Exception('Extension not found: {}'.format(kwargs))
        return extension

    def find_by(self, **kwargs):
        extensions = self._confd_client.extensions.list(**kwargs)['items']
        for extension in extensions:
            return extension

    def disable(self, extension_id):
        self._confd_client.extensions.update({'id': extension_id, 'enabled': False})
