# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
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

from lettuce.registry import world
from xivo_lettuce import form


def type_skill_rule_name(skill_rule_name):
    form.input.edit_text_field_with_id('it-queueskillrule-name', skill_rule_name)


def add_rule(rule):
    add_button = world.browser.find_element_by_id('lnk-add-row')
    add_button.click()
    textareas = world.browser.find_elements_by_xpath("//textarea[@id='it-queueskillrule-rule']")
    textareas[len(textareas) - 2].clear()
    textareas[len(textareas) - 2].send_keys(rule)


def is_displayed(skill_rule_content):
    element = world.browser.find_elements_by_xpath("//td[text()='%s']" % skill_rule_content)
    return len(element) > 0
