# Copyright 2013-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import time

from behave import then
from hamcrest import (
    assert_that,
    all_of,
    greater_than,
    has_entries,
    less_than,
)
from xivo_test_helpers import until


def close_to(target, delta):
    minimum = target - delta
    maximum = target + delta
    return all_of(greater_than(minimum), less_than(maximum))


@then('I have the last call log matching')
def then_i_have_the_last_call_log_matching(context):
    expected = context.table[0].as_dict()
    expected_duration = int(expected.pop('duration', None))
    if expected.get('answered'):
        expected['answered'] = bool(expected['answered'])

    def _assert():
        actual = context.call_logd_client.cdr.list(direction='desc', limit=1, recurse=True)['items'][0]
        assert_that(actual, has_entries(expected))
        if expected_duration:
            assert_that(actual['duration'], close_to(expected_duration, 2))

    until.assert_(_assert, tries=5)
