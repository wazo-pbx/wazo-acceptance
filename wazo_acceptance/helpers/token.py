# Copyright 2019-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_auth_client import Client as AuthClient


class Token:

    def __init__(self, context):
        self._context = context
        self._tokens = {}

    def create(self, username, password, tracking_id=None, **kwargs):
        auth_client = AuthClient(
            username=username,
            password=password,
            **self._context.wazo_config['auth']
        )

        token_key = tracking_id or username
        existing_token = self._tokens.get(token_key)
        if existing_token:
            return existing_token

        token_data = auth_client.token.new(**kwargs)
        self._tokens[token_key] = token_data
        self._context.add_cleanup(self.delete, token_key)
        return token_data

    def get(self, token_key):
        return self._tokens.get(token_key)

    def delete(self, token_key):
        token_info = self._tokens.get(token_key)
        if token_info:
            self._context.auth_client.token.revoke(token_info)
            self._tokens.pop(token_key)
