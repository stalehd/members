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
import logging


def expire_members():
    logging.info('Expiring memberships')
    types = MemberType.all().fetch(10000)
    expired_type = None
    for mt in types:
        if mt.name == MEMBER_TYPE_EXPIRED:
            expired_type = mt
            break
    if not expired_type:
        logging.info(
            'Could not find member type for expired members. Exiting.')
        return

    members = Member.all().fetch(10000)
    expired_count = 0
    this_year = datetime.datetime.now().year
    total = 0
    for member in members:
        total = total + 1
        dues = MembershipDues.all().ancestor(member).filter('year', this_year).fetch(100)
        all_paid = False
        for due in dues:
            #logging.info('%s: Y: %s, paid: %s' % (member.number, due.year, due.paid))
            if not all_paid and due.year == this_year and due.paid:
                all_paid = True
                # print 'All paid for %s ' % (member.number)

        if not all_paid:
            if member.membertype.name == DEFAULT_MEMBER_NAME:
                if member.status.name == DEFAULT_MEMBER_STATUS_NAME:
                    print ('Member no %s has an expired membership (type is %s, status is %s); new type will be %s' %
                           (member.number, member.membertype.name, member.status.name, expired_type.name))

                    member.membertype = expired_type
                    member.put()
                    expired_count = expired_count + 1

    print ('%d memberships of %d will be expired' % (expired_count, total))
