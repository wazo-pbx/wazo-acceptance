# -*- coding: utf-8 -*-

from lettuce.registry import world


def get_asterisk_conf(file, var_name):
    command = ['xivo-confgen', 'asterisk/%s' % file, '|', 'grep', var_name]
    ret = world.ssh_client_xivo.out_call(command)
    if ret:
        val = ret.split('=')[1].strip()
        return val
    assert(False)


def logoff_agents(agent_numbers):
    for agent_number in agent_numbers:
        logoff_agent(agent_number)


def logoff_agent(agent_number):
    asterisk_command = 'agent logoff Agent/%s' % (agent_number)
    send_to_asterisk_cli(asterisk_command)


def send_to_asterisk_cli(asterisk_command):
    check_output_asterisk_cli(asterisk_command)


def check_output_asterisk_cli(asterisk_command):
    shell_command = ['asterisk', '-rx', '"%s"' % asterisk_command]
    output = world.ssh_client_xivo.out_call(shell_command)
    return output

