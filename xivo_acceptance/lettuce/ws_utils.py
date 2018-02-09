# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import json
import re

from hamcrest import assert_that, has_key, equal_to
import requests


DEFAULT_CONTENT_TYPE = 'application/json'


class WsUtils(object):
    '''
    This helper class is a forerunner of a library
    proposing methods for easy implementation of
    REST web services
    '''

    def __init__(self, rest_configuration_obj):
        self.config = rest_configuration_obj
        self.baseurl = self._prepare_baseurl(self.config)

    def _prepare_baseurl(self, rest_configuration_obj):
        protocol = rest_configuration_obj.protocol
        hostname = rest_configuration_obj.hostname
        port = rest_configuration_obj.port

        baseurl = "%s://%s:%s" % (protocol, hostname, port)

        api_version = rest_configuration_obj.api_version
        if api_version is not None:
            baseurl = '%s/%s' % (baseurl, api_version)

        return baseurl

    def _prepare_session(self, rest_configuration_obj):
        session = requests.Session()
        session.headers.update({'Content-Type': rest_configuration_obj.content_type})
        session.headers.update({'Accept': rest_configuration_obj.content_type})
        session.verify = False

        username = rest_configuration_obj.auth_username
        password = rest_configuration_obj.auth_passwd
        if username and password:
            session.auth = requests.auth.HTTPDigestAuth(username, password)

        return session

    def rest_get(self, path, **kwargs):
        return self._request('GET', path, **kwargs)

    def rest_post(self, path, payload, **kwargs):
        data = json.dumps(payload)
        return self._request('POST', path, data=data, **kwargs)

    def rest_put(self, path, payload=None, **kwargs):
        data = json.dumps(payload) if payload else ''
        return self._request('PUT', path, data=data, **kwargs)

    def rest_delete(self, path, **kwargs):
        return self._request('DELETE', path, **kwargs)

    def _request(self, method, path, *args, **kwargs):
        path = path.lstrip('/')
        url = "%s/%s" % (self.baseurl, path)
        session = self._prepare_session(self.config)
        if 'headers' in kwargs:
            session.headers.update(kwargs['headers'])
        response = session.request(method, url, *args, **kwargs)
        if response.status_code == 500:
            response.raise_for_status()
        return self._process_response(response)

    def _process_response(self, response):
        status_code = response.status_code
        body = response.text
        headers = response.headers

        return RestResponse(response.url, status_code, headers, body)


class RestResponse(object):

    def __init__(self, url, status, headers, raw_data):
        self.url = url
        self.status = status
        self.headers = headers
        self.raw_data = raw_data

    @property
    def data(self):
        try:
            return json.loads(self.raw_data)
        except:
            return self.raw_data

    def items(self):
        self.check_status()
        assert_that(self.data, has_key('items'))
        return self.data['items']

    def status_ok(self):
        return self.status in (200, 201, 204)

    def resource(self):
        self.check_status()
        return self.data

    def check_status(self, code=None):
        msg = "Status code was '%d'. Response: %s" % (self.status, self.raw_data)
        if code:
            assert_that(self.status, equal_to(code), msg)
        else:
            assert_that(self.status_ok(), msg)

    def check_regex(self, regex):
        matches = re.search(regex, self.raw_data)
        msg = "Regex '%s' did not match. Response: %s" % (regex, self.raw_data)
        assert_that(matches, msg)


class RestConfiguration(object):

    def __init__(self, protocol, hostname, port, auth_username=None, auth_passwd=None,
                 api_version=None, content_type=DEFAULT_CONTENT_TYPE):
        self.protocol = protocol
        self.hostname = hostname
        self.port = port
        self.auth_username = auth_username
        self.auth_passwd = auth_passwd
        self.api_version = api_version
        self.content_type = content_type
