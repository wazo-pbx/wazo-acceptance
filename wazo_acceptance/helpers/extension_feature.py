# Copyright 2019-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


class ExtensionFeature:

    def __init__(self, context):
        self._context = context
        self._confd_client = context.confd_client

    def _get_by(self, **kwargs):
        user = self._find_by(**kwargs)
        if not user:
            raise Exception('ExtensionFeature not found: {}'.format(kwargs))
        return user

    def _find_by(self, **kwargs):
        extensions_features = self._confd_client.extensions_features.list(**kwargs)['items']
        for extension in extensions_features:
            return extension

    def _update(self, body):
        old_feature = self._get_by(search=body['feature'])

        new_feature = old_feature.copy()
        new_feature.update(body)

        with self._context.helpers.bus.wait_for_asterisk_reload(dialplan=True):
            self._confd_client.extensions_features.update(new_feature)

        self._context.add_cleanup(self._confd_client.extensions_features.update, old_feature)

    def enable(self, feature_name, extension=None):
        feature = {
            'feature': feature_name,
            'enabled': True,
        }
        if extension:
            feature['exten'] = '_{}.'.format(extension)
        self._update(feature)

    def disable(self, feature_name, extension=None):
        feature = {
            'feature': feature_name,
            'enabled': False,
        }
        if extension:
            feature['exten'] = '_{}.'.format(extension)
        self._update(feature)
