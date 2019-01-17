# -*- coding: utf-8 -*-
# Copyright (C) 2013-2014 Avencall
# SPDX-License-Identifier: GPL-3.0-or-later

from lettuce import step, world

from xivo_acceptance.helpers import trunksip_helper

IPBX_COUNT_URL = '/service/ipbx/index.php'
SIP_TRUNK_STAT_XPATH = "//div[@id='ipbx-stats']//tr[8]//td[%d]"

ENABLED_INDEX = 2
DISABLED_INDEX = 3
TOTAL_INDEX = 4


def _open_ipbx_count_url():
    world.browser.get('%s%s' % (world.config['frontend']['url'], IPBX_COUNT_URL))


def _sip_trunk_enabled_xpath():
    return SIP_TRUNK_STAT_XPATH % ENABLED_INDEX


def _sip_trunk_disabled_xpath():
    return SIP_TRUNK_STAT_XPATH % DISABLED_INDEX


def _sip_trunk_total_xpath():
    return SIP_TRUNK_STAT_XPATH % TOTAL_INDEX


def _get_enabled_sip_trunk_count():
    element = world.browser.find_element_by_xpath(_sip_trunk_enabled_xpath())
    return int(element.text)


def _get_disabled_sip_trunk_count():
    element = world.browser.find_element_by_xpath(_sip_trunk_disabled_xpath())
    return int(element.text)


def _get_total_sip_trunk_count():
    element = world.browser.find_element_by_xpath(_sip_trunk_total_xpath())
    return int(element.text)


@step(u'Given I have (\d+) enabled trunk')
def given_i_have_trunk(step, count):
    for i in range(int(count)):
        trunksip_helper.add_trunksip('169.10.0.54', 'trunk_%s' % i)


@step(u'Given i remember the number of available trunk as "([^"]*)"')
def given_i_remember_the_number__of_available_trunk_as(step, name_var):
    _open_ipbx_count_url()
    if not hasattr(world, 'remember_string'):
        world.remember_string = dict()
    world.remember_string[name_var] = _get_total_sip_trunk_count()


@step(u'When I open the ibpx count page')
def when_i_open_the_ipbx_count_page(step):
    _open_ipbx_count_url()


@step(u'Then I should have (\d+) more then remembered value "([^"]*)"')
def then_i_should_have_n_more_then_remembered_calue(step, count, name_var):
    try:
        nb_exist_trunk = world.remember_string[name_var]
    except Exception:
        assert(False)
    assert((int(nb_exist_trunk) + int(count)) == _get_total_sip_trunk_count())
