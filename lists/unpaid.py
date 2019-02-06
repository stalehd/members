# -*- coding: utf-8 -*-
"""List of unpaid membership dues"""
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
from model import MembershipDues
from model import Member
from lists import ReportGenerator

LIMIT_ALL = 10000
YEAR_MAX = 25


class UnpaidMembershipDues(ReportGenerator):
    """ Report with unpaid membership dues """

    def id(self):
        return 'exmembers'

    def name(self):
        return u'Ikke betalt kontingent innenværende år'

    def description(self):
        return u"""Liste over de som ikke har betalt kontingent inneværende år
        eller i fjor. Dette inkluderer ikke de som har kontingenten satt til 0,
        slik som Alfanytt og Hedersmedlemmer."""

    def report_task(self):
        filename = self.get_filename(self.id())
        member_list = Member.all().fetch(LIMIT_ALL)
        current_year = datetime.datetime.now().year
        final_list = list()

        for member in member_list:
            # Skip if the member doesn't pay fees
            if member.membertype.fee == 0:
                continue

            # Retrieve dues and check if status is set to paid
            dues = MembershipDues.all().ancestor(member).fetch(YEAR_MAX)
            paid = False
            for due in dues:
                if due.year == current_year:
                    paid = due.paid
                    break
            if not paid:
                final_list.append(member)

        # Make CSV file
        lines = list()
        lines.append(
            'number;name;address;zip;city;country;email;phone;member_since;type;status\n')
        for member in final_list:
            datestr = ''
            if member.member_since:
                datestr = member.member_since.strftime('%Y-%m-%d')
            phonestr = ''
            if member.phone and member.phone != 'None':
                phonestr = unicode(member.phone)
            emailstr = ''
            if member.email and member.email != 'None':
                emailstr = unicode(member.email)
            lines.append('"%s";"%s";"%s";"%s";"%s";"%s";"%s";"%s";%s;"%s";"%s"\n' % (
                unicode(member.number), unicode(
                    member.name), unicode(member.address),
                unicode(member.zipcode), unicode(
                    member.city), unicode(member.country.name),
                emailstr, phonestr, datestr,
                unicode(member.membertype.name), unicode(member.status.name)))

        self.write_report(filename, lines)
