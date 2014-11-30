# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# Portello membership system
# Copyright (C) 2014 Klubb Alfa Romeo Norge
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# -------------------------------------------------------------------------
"""Configuration methods and class"""
import jinja2
import os.path
from model import ConfigTuple

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

DUES_AHEAD = 2
FIRST_YEAR_WITH_DUES = 2009
BACKUP_BUCKET='portellobackup'
REPORT_BUCKET='portelloreports'
CONFIG_NAME = 'ConfigTuple'

class Configuration(object):
    """Simple config class with get and set methods"""
    defaults = {
        'WELCOME_MAIL_SENDER' : u'KARN Webmaster <karn.webmaster@gmail.com>',
        'WELCOME_MAIL_SUBJECT':
            u'Velkommen som medlem i Klubb Alfa Romeo Norge!',
        'NOTIFICATION_MAIL_SUBJECT': u'Et nytt KARN-medlem har registrert seg',
        'NOTIFICATION_MAIL_RECIPIENTS': u'stalehd@gmail.com',
        'GIRO_ACCOUNT_NO': '1607 56 53933',
        'GIRO_SUBJECT': u'Velkommen som medlem i Klubb Alfa Romeo Norge',
        'GIRO_TEXT': u"""For å få tilsendt medlemskort må du betale denne giroen. Merk giroen med medlemsnummeret slik at vi kan
se at du har betalt.

Du kan redigere medlemsprofilen din (adresse, telefonnummer og epostadresse) ved å gå til

        {{ profile_url }}

og logge inn med medlemsnummeret ditt ({{ member_no }}) og innloggingskoden
({{ access_code }}). Det neste medlemskortet ditt vil ha denne koden trykt på baksiden.

Dersom du har noen spørsmål kan du sende e-post til kasserer@klubbalfaromeo.no eller
webmaster@klubbalfaromeo.no.

Nok en gang: Velkommen!""",
        'GIRO_ADDRESS': u'KLUBB ALFA ROMEO NORGE\n\nPb. 7170 Bedriftspostkontoret\n0301 OSLO',
        'GIRO_MESSAGE': u'Kontingent medl. {{ member_no }}',
        'GIRO_PROFILE_URL': u'https://klubbalfaromeonorge.appspot.com/selfservice/profile',
        'WELCOME_MAIL_TEXT': u"""Velkommen som medlem i Klubb Alfa Romeo Norge!

Det neste steget nå er å betale inn årskontigenten for {{ year }} på kroner {{ member.member_type.fee }},-
til kontonummer {{ account_no }} og merke innbetalingen med medlemsnummeret
ditt ({{ member.number }}). Etter den 1. juli blir det halv kontingent.

Når din innbetaling er registrert vil du motta en velkomstpakke i posten.

Ta kontakt med kasserer@klubbalfaromeo.no dersom du har noen spørsmål.

Vi har registrert følgende informasjon om deg i registeret:

Navn:           {{ member.name }}
Adresse:        {{ member.address }}
                {{ member.zipcode }} {{ member.city }}
                {{ member.country.name }}

Epost:          {{ member.email }}

Telefon:        {{ member.phone }}
Telefon hjem:   {{ member.phone_home }}
Telefon arbeid: {{ member.phone_work }}

Type medlem:     {{ member.member_type.name }}


Dersom du ønsker å endre adresseinformasjonen din så kan du gjøre det ved å gå til

     {{ profile_url }}

og taste inn medlemsnummeret ditt ({{ member.number }}) samt koden {{ member.edit_access_code }}.

Her kan du endre adresse, epostadresse og føre opp Alfaene du eier eller har eid.
Bilregisteret er selvfølgelig helt frivillig!


Nok en gang: Velkommen!"""
    }

    def get(self, name):
        """Get config tuple from data store; return default if no tuple is found"""
        config_value = ConfigTuple.get_or_insert(name, value=self.defaults[name])
        return config_value.value

    def set(self, name, value):
        """Save configuration tuple to data store"""
        config_tuple = ConfigTuple.get_by_key_name(name)
        if not config_tuple:
            config_tuple = ConfigTuple(key_name=name)
        config_tuple.value = value
        config_tuple.put()

