# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from hamcrest import assert_that, equal_to, instance_of
from lettuce import step, world
from selenium.webdriver.common.action_chains import ActionChains
from xivo_ws.exception import WebServiceRequestError

from xivo_acceptance.action.webi import agent as agent_action_webi
from xivo_acceptance.helpers import agent_helper, auth_helper
from xivo_acceptance.lettuce import common, form, func
from xivo_agentd_client import Client as AgentdClient
from xivo_agentd_client.error import AgentdClientError


@step(u'Given there is a agent "([^"]+)" "([^"]*)" with extension "([^"]+)"$')
def given_there_is_a_agent_in_context_with_number(step, firstname, lastname, extension):
    number, context = func.extract_number_and_context_from_extension(extension)
    agent_helper.delete_agents_with_number(number)
    agent_data = {
        'firstname': firstname,
        'lastname': lastname,
        'number': number,
        'context': context
    }
    agent_helper.add_agent(agent_data)


@step(u'Given there is no agents logged')
def given_there_is_no_agents_logged(step):
    agent_helper.unlog_all_agents()


@step(u'Given I log agent "([^"]*)" on extension "([^"]*)"')
def given_i_log_the_phone(step, agent_number, extension):
    agent_helper.login_agent(agent_number, extension)


@step(u'Given there is no agent with id "([^"]*)"')
def given_there_is_no_agent_with_id(step, agent_id):
    try:
        agent_helper.delete_agent_with_id(agent_id)
    except WebServiceRequestError as e:
        if e.code != 404:
            raise


@step(u'When I log agent "([^"]*)"$')
def when_i_log_agent_1(step, agent_number):
    agent_helper.login_agent(agent_number)


@step(u'When I log agent "([^"]*)", ignoring errors$')
def when_i_log_agent_1_ignoring_errors(step, agent_number):
    agent_helper.login_agent(agent_number, ignore_error=True)


@step(u'When I log agent "([^"]*)" from the phone$')
def when_i_log_agent_1_from_the_phone(step, agent_number):
    agent_helper.login_agent_from_phone(agent_number, step.scenario.phone_register)


@step(u'When I unlog agent "([^"]*)"$')
def when_i_unlog_agent_group1(step, agent_number):
    agent_helper.logoff_agent(agent_number)


@step(u'When I unlog agent "([^"]*)", ignoring errors$')
def when_i_unlog_agent_group1_ignoring_errors(step, agent_number):
    agent_helper.logoff_agent(agent_number, ignore_error=True)


@step(u'When I unlog agent "([^"]*)" from the phone$')
def when_i_unlog_agent_group1_from_the_phone(step, agent_number):
    agent_helper.logoff_agent_from_phone(agent_number, step.scenario.phone_register)


@step(u'When I pause agent "([^"]*)"')
def when_i_pause_agent_1(step, agent_number):
    agent_helper.pause_agent(agent_number)


@step(u'When I unpause agent "([^"]*)"')
def when_i_unpause_agent_1(step, agent_number):
    agent_helper.unpause_agent(agent_number)


@step(u'When I create an agent "([^"]*)" "([^"]*)" "([^"]*)"$')
def when_i_create_an_agent(step, firstname, lastname, number):
    agent_helper.delete_agents_with_number(number)
    common.open_url('agent', 'addagent', {'group': '1'})
    agent_action_webi.type_agent_info(firstname, lastname, number)
    form.submit.submit_form()


@step(u'When I create an agent "([^"]*)" "([^"]*)" "([^"]*)" in group "([^"]*)"$')
def when_i_create_an_agent_in_group(step, firstname, lastname, number, agent_group):
    agent_helper.delete_agents_with_number(number)
    group_id = agent_action_webi.get_agent_group_id(agent_group)
    common.open_url('agent', 'addagent', {'group': group_id})
    agent_action_webi.type_agent_info(firstname, lastname, number)
    form.submit.submit_form()


@step(u'When I search an agent "([^"]*)"')
def when_i_search_an_agent_group1(step, search):
    common.open_url('agent', 'listagent', {'group': '1'})
    form.input.edit_text_field_with_id('it-toolbar-search', search)
    form.submit.submit_form('it-toolbar-subsearch')


@step(u'When I remove agent "([^"]*)" "([^"]*)"')
def when_i_remove_agent(step, firstname, lastname):
    common.remove_line('%s %s' % (firstname, lastname))


@step(u'When I remove agent group "([^"]*)"')
def when_i_remove_agent_group(step, agent_group_name):
    common.remove_line(agent_group_name)


@step(u'When I remove selected agent group')
def when_i_remove_selected_agent_group(step):
    element_to_hover_over = world.browser.find_element_by_xpath("//img[@id='toolbar-bt-advanced']")
    hover = ActionChains(world.browser).move_to_element(element_to_hover_over)
    delete_href = element_to_hover_over.find_element_by_xpath("//a[@id='toolbar-advanced-menu-delete']")
    hover.move_to_element(delete_href)
    hover.click()
    hover.perform()
    alert = world.browser.switch_to_alert()
    alert.accept()


@step(u'When I change the agent "([^"]*)" password to "([^"]*)"')
def when_i_change_the_agent_password_to_group1(step, number, password):
    agent_id = agent_helper.find_agent_id_with_number(number)
    common.open_url('agent', 'editagent', {'group': '1', 'id': agent_id})
    agent_action_webi.change_password(password)
    form.submit.submit_form()


@step(u'When I create an agent group "([^"]*)"')
def when_i_create_an_agent_group(step, agent_group_name):
    agent_action_webi.remove_agent_group_if_exist(agent_group_name)
    common.open_url('agent', 'add')
    form.input.edit_text_field_with_id('it-agentgroup-name', agent_group_name)
    form.submit.submit_form()


@step(u'When I select a list of agent group "([^"]*)"')
def when_i_select_an_agent_group(step, agent_group_list):
    common.open_url('agent', 'list')
    list = agent_group_list.split(',')
    agent_action_webi.select_agent_group_list(list)


@step(u'When I request the agent statuses with an invalid token')
def when_i_request_the_agent_statuses_with_an_invalid_token(step):
    token = auth_helper.new_invalid_token_id()
    agentd_client = AgentdClient(world.config['xivo_host'],
                                 token=token,
                                 verify_certificate=False)
    _agentd_request(agentd_client.agents.get_agent_statuses)


def _agentd_request(fun, *args):
    world.agentd_response = None
    world.agentd_exception = None
    try:
        world.agentd_response = fun(*args)
    except Exception as e:
        world.agentd_exception = e


@step(u'Then I get an "invalid token" response from xivo-agentd')
def then_i_get_an_invalid_token_response_from_xivo_agentd(step):
    assert_that(world.agentd_exception, instance_of(AgentdClientError))
    assert_that(world.agentd_exception.error, equal_to('invalid token or unauthorized'))


@step(u'Then agent "([^"]*)" is displayed in the list of "([^"]*)" agent group')
def then_agent_group1_is_displayed_in_the_list_of_group2_agent_group(step, agent_name, agent_group):
    assert agent_action_webi.is_agent_in_agent_group(agent_group, agent_name)


@step(u'Then agent "([^"]*)" is not displayed in the list of "([^"]*)" agent group')
def then_agent_is_not_displayed_in_the_list_of_default_agent_group(step, agent_name, agent_group):
    assert not agent_action_webi.is_agent_in_agent_group(agent_group, agent_name)


@step(u'Then agent group "([^"]*)" has "([^"]*)" agents')
def then_agent_group_has_x_agents(step, agent_group, nb_agents):
    nb_agents = int(nb_agents)

    assert_that(agent_action_webi.get_nb_agents_in_group(agent_group), equal_to(nb_agents))


@step(u'Then the agent "([^"]*)" password is "([^"]*)"')
def then_the_agent_password_is(step, number, password):
    current_password = agent_helper.find_agent_password_with_number(number)

    assert_that(current_password, equal_to(password))


@step(u'Then the agent "([^"]*)" is logged')
def then_the_agent_group1_is_logged(step, agent_number):
    assert agent_helper.is_agent_logged(agent_number)


@step(u'Then the agent "([^"]*)" is not logged')
def then_the_agent_group1_is_not_logged(step, agent_number):
    assert not agent_helper.is_agent_logged(agent_number)
