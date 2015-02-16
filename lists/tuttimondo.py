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
from lists import ReportGenerator
import constants
from model import Member
from model import MembershipDues
import datetime

YEAR_MAX = 25
LIMIT_ALL = 2000
class TuttiMondo(ReportGenerator):
    """ Everything in the database """
    def id(self):
        return 'tuttimondo'

    def name(self):
        return u'Alle medlemmer med betaling'

    def description(self):
        return u"""  med navn, nummer, adresse, epost og betalt-status for 3 år fram og tilbake i tid."""

    def report_task(self):
        filename = self.get_filename(self.id())
        member_list = Member.all().fetch(LIMIT_ALL)

        current_year = datetime.datetime.now().year
        year_range = range(current_year - 3, current_year + 3)

        lines = list()
        lines.append('number;name;address;zip;city;country;type')
        for year in year_range:
            lines.append(';fee' + str(year))
        lines.append('\n')

        for member in member_list:
            typename = member.membertype.name
            lines.append('"%s";"%s";"%s";"%s";"%s";"%s";"%s"' % (
                unicode(member.number), unicode(member.name), unicode(member.address),
                unicode(member.zipcode), unicode(member.city), unicode(member.country.name),
                typename))
            due_list  = {}
            for year in year_range:
                due_list['year' + str(year)] = 0

            for due in MembershipDues.all().ancestor(member).fetch(YEAR_MAX):
                key = 'year' + str(due.year)
                if key in due_list:
                    if due.paid:
                        due_list[key] = 1

            for year in year_range:
                lines.append(';' + str(due_list['year' + str(year)]))

            lines.append('\n')

        self.write_report(filename, lines)
