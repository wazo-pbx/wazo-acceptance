# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from behave import given

_DESCRIPTION_TO_FEATURE = {
    'forwarding on no-answer': 'fwdrna',
    'forwarding on busy': 'fwdbusy',
    'unconditional forwarding': 'fwdunc',
    'do not disturb': 'enablednd',
    'incoming call filtering': 'incallfilter',
    'call recording': 'callrecord',
}

@given('the "{extension_name}" extension is disabled')
def given_the_extension_is_disabled(context, extension_name):
    context.helpers.extension_feature.disable(_DESCRIPTION_TO_FEATURE[extension_name])
