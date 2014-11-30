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
import datetime
from model import Member
from model import MembershipDues
from model import MemberType
from constants import MEMBER_TYPE_EXPIRED
from constants import DEFAULT_MEMBER_NAME
from constants import DEFAULT_MEMBER_STATUS_NAME

def expire_members():
    types = MemberType.all().fetch(30)
    expired_type = None
    for mt in types:
        if mt.name == MEMBER_TYPE_EXPIRED:
            expired_type = mt
            break
    if not expired_type:
        print 'Could not find member type for expired members'

    members = Member.all().fetch(3000)
    expired_count = 0
    last_year = datetime.datetime.now().year - 1
    for member in members:
        dues = MembershipDues.all().ancestor(member).fetch(30)
        all_paid = False
        for due in dues:
            if due.year >= last_year and due.paid:
                all_paid = True
                break
        if not all_paid and member.membertype.name == DEFAULT_MEMBER_NAME and member.status.name == DEFAULT_MEMBER_STATUS_NAME:
            print 'Member no', member.number, 'has an expired membership'
            member.membertype = expired_type
            member.put()
            expired_count = expired_count + 1

    print expired_count, 'memberships have been ended'
