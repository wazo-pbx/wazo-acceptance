# -*- coding: utf-8 -*-

from lettuce import step
from xivo_lettuce.common import open_url
from xivo_lettuce.manager import profile_manager
from selenium.common.exceptions import NoSuchElementException
from xivo_lettuce import common, form


@step(u'Given there is no profile "([^"]*)"')
def given_there_is_no_profile_1(step, profile_name):
    profile_manager.delete_profile_if_exists(profile_name)


@step(u'Given I add a profile')
def given_i_add_a_profile(step):
    open_url('profile', 'add')


@step(u'Given I remove all services')
def given_i_remove_all_services(step):
    profile_manager.remove_all_services()


@step(u'Given I add a XLet "([^"]*)"')
def given_i_add_a_xlet_1(step, xlet_label):
    profile_manager.add_xlet(xlet_label)


@step(u'Given there is a profile "([^"]*)" with no services and xlets:')
def given_there_is_a_profile_1_with_no_services_and_xlets(step, profile_name):
    profile_manager.delete_profile_if_exists(profile_name)
    common.open_url('profile', 'add')
    profile_manager.type_profile_names(profile_name, profile_name)
    profile_manager.remove_all_services()
    common.go_to_tab('Xlets')
    cti_profile_config = step.hashes
    for cti_profile_element in cti_profile_config:
        xlet_name = cti_profile_element['xlet']
        profile_manager.add_xlet(xlet_name)
    form.submit_form()


@step(u'When I add the CTI profile "([^"]*)" with errors')
def when_i_add_the_cti_profile_1_with_errors(step, profile_name):
    common.open_url('profile', 'add')
    profile_manager.type_profile_names(profile_name, profile_name)
    form.submit_form_with_errors()


@step(u'When I add the CTI profile "([^"]*)"')
def when_i_add_the_cti_profile_1(step, profile_name):
    common.open_url('profile', 'add')
    profile_manager.type_profile_names(profile_name, profile_name)
    form.submit_form()


@step(u'Then I can\'t remove profile "([^"]*)"')
def then_i_see_errors(step, profile_label):
    common.open_url('profile', 'list')
    table_line = common.find_line(profile_label)
    try:
        table_line.find_element_by_xpath(".//a[@title='Delete']")
    except NoSuchElementException:
        pass
    else:
        raise Exception('CTI profile %s should not be removable' % profile_label)