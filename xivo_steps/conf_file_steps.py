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

from lettuce.decorators import step
from xivo_lettuce import sysutils


@step(u'Then cti configuration file correctly generated')
def then_cti_configuration_file_correctly_generated(step):
    CTI_INI_FILE = '/etc/pf-xivo/xivo-web-interface/cti.ini'
    CTI_INI_CONTENT_RESULT = """\
[general]
datastorage = "postgresql://xivo:proformatique@localhost/xivo?charset=utf8"

[queuelogger]
datastorage = "postgresql://asterisk:proformatique@localhost/asterisk?charset=utf8"
"""
    cti_ini_content = sysutils.get_content_file(CTI_INI_FILE)
    assert cti_ini_content == CTI_INI_CONTENT_RESULT
