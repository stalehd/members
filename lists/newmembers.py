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
import datetime
LIMIT_ALL = 2000

class NewMemberList(ReportGenerator):
    """ List of new member in the last 6 months """
    def id(self):
        return 'nye_medlemmer'

    def name(self):
        return u'Nye medlemmer siste 120 dager'

    def description(self):
        return u"""Liste over medlemmer som har meldt seg inn de siste 120
        dagene, dvs ca fire måneder."""

    def report_task(self):
        diff = datetime.timedelta(days=120)
        cutoff_date = datetime.date.today() - diff

        filename = self.get_filename(self.id())
        member_list = Member.all().fetch(LIMIT_ALL)

        lines = list()
        lines.append('number;name;zip;city;date')
        for member in member_list:
            if member.member_since >= cutoff_date:
                lines.append('"%s";"%s";"%s";"%s";"%s"' % (
                    unicode(member.number), unicode(member.name),
                    unicode(member.zipcode), unicode(member.city),
                    member.member_since.isoformat()))

        self.write_report(filename, lines)
