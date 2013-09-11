# -*- coding: utf-8 -*-


from xivo_lettuce.restapi.v1_1 import ws_utils_session as ws_utils

DEVICES_URL = 'devices'


def create_device(parameters):
    return ws_utils.rest_post(DEVICES_URL, parameters)


def synchronize(device_id):
    return ws_utils.rest_get('%s/%s/synchronize' % (DEVICES_URL, device_id))


def delete_device(device_id):
    return ws_utils.rest_delete("%s/%s" % (DEVICES_URL, device_id))


def get_device(device_id):
    return ws_utils.rest_get("%s/%s" % (DEVICES_URL, device_id))


def device_list(parameters={}):
    return ws_utils.rest_get(DEVICES_URL, params=parameters)

def reset_to_autoprov(device_id):
    return ws_utils.rest_get('%s/%s/autoprov' % (DEVICES_URL, device_id))


def associate_line_to_device(device_id, line_id):
    return ws_utils.rest_get('%s/%s/associate_line/%s' % (DEVICES_URL, device_id, line_id))


def remove_line_from_device(device_id, line_id):
    return ws_utils.rest_get('%s/%s/remove_line/%s' % (DEVICES_URL, device_id, line_id))

def edit_device(device_id, parameters):
    return ws_utils.rest_put("%s/%s" % (DEVICES_URL, device_id), parameters)