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
"""Misc utilities that interacts with the database. Sort of."""

from model import Member
import datetime
import os
from google.appengine.api import mail
from constants import DEFAULT_MODEL_NAME
from model import CarModel

def create_new_member_no():
    """Assign new member no. Not *that* time critical but some form of
    transactions would be nice. Or required. This makes my hair stand up
    but...

    It works."""

    members = Member.all().order('-number').fetch(1)
    return str(int(members[0].number) + 1)

def get_default_model():
    """Return the default model name"""
    return CarModel.all().filter('name', DEFAULT_MODEL_NAME).fetch(1)[0]


def calculate_price(membertype):
    """Calculate the fee."""
    today = datetime.date.today()
    if today.month > 6:
        return membertype.fee / 2
    return membertype.fee


def is_valid(param):
    """Check if parameter exists and isn't blank."""
    if not param or param.strip() == '':
        return False
    return True

def is_valid_country(country, countries):
    """Check that a string matches one of the existing countries."""

    if not is_valid(country):
        return False

    print 'valid country'
    for element in countries:
        if str(element.key()) == country:
            return True

    return False

def is_valid_email(email):
    """Ensure email address is valid. Not very complicated checks."""

    if not is_valid(email):
        return False

    if not mail.is_email_valid(email):
        return False

    return True
