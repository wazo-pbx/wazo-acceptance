# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from behave import given


@given('the extension "{extension}@{asterisk_context}" is disabled')
def given_the_extension_is_disabled(context, extension, asterisk_context):
    extension = context.helpers.extension.get_by(context=asterisk_context, exten=extension)
    context.helpers.extension.disable(extension['id'])
