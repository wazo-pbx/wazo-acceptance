# -*- coding: utf-8 -*-
# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
import hashlib

import ldap.modlist


LDAP_URI = 'ldap://openldap-dev.lan.wazo.io:389/'
LDAP_LOGIN = 'cn=admin,dc=lan-quebec,dc=avencall,dc=com'
LDAP_PASSWORD = 'superpass'
LDAP_USER_GROUP = 'ou=people,dc=lan-quebec,dc=avencall,dc=com'


def sanitize_string(text):
    if isinstance(text, unicode):
        text = text.encode('utf-8')
    return text


def escape_ldap_string(text):
    return text.replace('\\', '\\\\')


def encode_entry(entry):
    return dict((key, sanitize_string(value)) for key, value in entry.iteritems())


def add_or_replace_ldap_entry(entry):
    entry = encode_entry(entry)
    ldap_server = connect_to_server()

    common_name = entry['cn']
    dn = _get_entry_id(common_name)

    if _ldap_has_entry(ldap_server, common_name):
        delete_entry(ldap_server, common_name)
    add_entry(ldap_server, dn, entry)

    ldap_server.unbind_s()


def generate_ldap_password(password):
    hasher = hashlib.sha1()
    hasher.update(password)
    payload = base64.b64encode(hasher.digest())
    return "{SHA}%s" % payload


def connect_to_server(uri=LDAP_URI):
    ldap_server = ldap.initialize(uri)
    ldap_server.simple_bind(LDAP_LOGIN, LDAP_PASSWORD)
    return ldap_server


def _ldap_has_entry(ldap_server, common_name):
    cn = escape_ldap_string(common_name)
    ldap_results = ldap_server.search_s(LDAP_USER_GROUP, ldap.SCOPE_SUBTREE, '(cn=%s)' % cn)
    if ldap_results:
        return True
    else:
        return False


def delete_entry(ldap_server, common_name):
    entry_id = _get_entry_id(common_name)
    ldap_server.delete_s(entry_id)


def _get_entry_id(common_name):
    cn = escape_ldap_string(common_name)
    return 'cn=%s,%s' % (cn, LDAP_USER_GROUP)


def add_entry(ldap_server, dn, entry):
    entry_encoded = ldap.modlist.addModlist(entry)
    ldap_server.add_s(dn, entry_encoded)
