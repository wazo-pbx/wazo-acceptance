# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

import time


def _rec_update_dict(base_dict, overlay_dict):
    for k, v in overlay_dict.iteritems():
        if isinstance(v, dict):
            old_v = base_dict.get(k)
            if isinstance(old_v, dict):
                _rec_update_dict(old_v, v)
            else:
                base_dict[k] = {}
                _rec_update_dict(base_dict[k], v)
        elif isinstance(v, list):
            if k in base_dict:
                base_dict[k].extend(v)
            else:
                base_dict[k] = v
        else:
            base_dict[k].append(v)


def extract_number_and_context_from_extension(extension, default_context='default'):
    if '@' in extension:
        number, context = extension.split('@', 1)
    else:
        number = extension
        context = default_context
    return number, context


def st_time(func):
    """
        st decorator to calculate the total time of a func
    """

    def st_func(*args, **keyArgs):
        t1 = time.time()
        r = func(*args, **keyArgs)
        t2 = time.time()
        print "Function=%s, Time=%s" % (func.__name__, t2 - t1)
        return r

    return st_func


def compare_list_of_dict_recursive_expected_key_value(expecteds, results):
    for dict_expected in expecteds:
        assert_dict = {}
        iterator = 0
        for dict_result in results:
            assert_dict[iterator] = 1
            for key_expected, value in dict_expected.iteritems():
                if key_expected in dict_result and value == dict_result[key_expected]:
                    assert_dict[iterator] = assert_dict[iterator] + 1
            iterator = iterator + 1
        assert_res = False
        for iter_value_result in assert_dict.itervalues():
            if iter_value_result >= len(dict_expected):
                assert_res = True

    return assert_res
