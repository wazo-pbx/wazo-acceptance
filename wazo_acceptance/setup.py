# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import logging

from requests.exceptions import HTTPError

from wazo_call_logd_client import Client as CallLogdClient
from wazo_calld_client import Client as CalldClient
from wazo_dird_client import Client as DirdClient
from wazo_provd_client import Client as ProvdClient
from wazo_setupd_client import Client as SetupdClient
from xivo_agentd_client import Client as AgentdClient
from xivo_amid_client import Client as AmidClient
from xivo_auth_client import Client as AuthClient
from xivo_confd_client import Client as ConfdClient

from . import auth
from . import debug
from .config import load_config
from .helpers.asterisk_helper import AsteriskHelper
from .helpers.context_helper import ContextHelper
from .ssh import SSHClient
from .sysutils import RemoteSysUtils

logger = logging.getLogger(__name__)


def setup_agentd_client(context):
    context.agentd_client = AgentdClient(**context.wazo_config['agentd'])
    context.agentd_client.set_token(context.token)
    auth.register_for_token_renewal(context.agentd_client.set_token)


def setup_amid_client(context):
    context.amid_client = AmidClient(**context.wazo_config['amid'])
    context.amid_client.set_token(context.token)
    auth.register_for_token_renewal(context.amid_client.set_token)


def setup_call_logd_client(context):
    context.call_logd_client = CallLogdClient(**context.wazo_config['call_logd'])
    context.call_logd_client.set_token(context.token)
    auth.register_for_token_renewal(context.call_logd_client.set_token)


def setup_confd_client(context):
    context.confd_client = ConfdClient(**context.wazo_config['confd'])
    context.confd_client.set_token(context.token)
    auth.register_for_token_renewal(context.confd_client.set_token)


def setup_calld_client(context):
    context.calld_client = CalldClient(**context.wazo_config['calld'])
    context.calld_client.set_token(context.token)
    auth.register_for_token_renewal(context.calld_client.set_token)


def setup_dird_client(context):
    context.dird_client = DirdClient(**context.wazo_config['dird'])
    context.dird_client.set_token(context.token)
    auth.register_for_token_renewal(context.dird_client.set_token)


def setup_auth_token(context):
    context.auth_client = AuthClient(
        username='wazo-acceptance',
        password='hidden',
        **context.wazo_config['auth']
    )
    context.token = auth.new_auth_token(context)
    context.auth_client.set_token(context.token)
    auth.register_for_token_renewal(context.auth_client.set_token)


def setup_provd_client(context):
    context.provd_client = ProvdClient(**context.wazo_config['provd'])
    context.provd_client.set_token(context.token)
    auth.register_for_token_renewal(context.provd_client.set_token)


def setup_setupd_client(context):
    context.setupd_client = SetupdClient(**context.wazo_config['setupd'])
    context.setupd_client.set_token(context.token)
    auth.register_for_token_renewal(context.setupd_client.set_token)


def setup_tenant(context):
    name = context.wazo_config['default_tenant']
    try:
        tenants = context.auth_client.tenants.list(name=name)['items']
    except HTTPError:
        logger.exception('Error or Unauthorized to list tenants')
        return

    if not tenants:
        logger.exception('failed to get default tenant')
        return

    context.auth_client.set_tenant(tenants[0]['uuid'])
    context.confd_client.set_tenant(tenants[0]['uuid'])


def setup_config(context, extra_config_dir=None):
    context.wazo_config = load_config(extra_config_dir)


def setup_consul(context):
    command = 'cat /var/lib/consul/master_token'.split()
    context.wazo_config['consul_token'] = context.ssh_client.out_call(command).strip()


def setup_logging(context):
    debug.setup_logging(context.wazo_config)


@debug.logcall
def setup_ssh_client(context):
    context.ssh_client = SSHClient(
        hostname=context.wazo_config['wazo_host'],
        login=context.wazo_config['ssh_login'],
    )


class Helpers:
    pass


def setup_helpers(context):
    context.helpers = Helpers()
    context.helpers.asterisk = AsteriskHelper(context.ssh_client)
    context.helpers.context = ContextHelper(context.confd_client)


def setup_remote_sysutils(context):
    context.remote_sysutils = RemoteSysUtils(context.ssh_client)