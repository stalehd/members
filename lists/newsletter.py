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
LIMIT_ALL = 10000
class NewsletterRecipients(ReportGenerator):
    """ Address list for newsletter recipients """
    def id(self):
        return 'gazzetta'

    def name(self):
        return u'Adresseliste for Gazzetta'

    def description(self):
        return u""" Adresseliste for distribusjon av Gazzetta. Inkluderer alle
        som har medlemstypen 'medlem' og 'hedersmedlem'  (Windows-1252/ANSI tegnsett) """

    def report_task(self):
        filename = self.get_filename(self.id())
        member_list = Member.all().fetch(LIMIT_ALL)

        lines = list()
        lines.append('number;name;address;zip;city;country;type\n')
        for member in member_list:
            typename = member.membertype.name
            if typename == u'Medlem' or typename == u'Hedersmedlem':
                lines.append('"%s";"%s";"%s";"%s";"%s";"%s";"%s"\n' % (
                    unicode(member.number), unicode(member.name), unicode(member.address),
                    unicode(member.zipcode), unicode(member.city), unicode(member.country.name),
                    typename))

        self.write_report(filename, lines, 'cp1252')
