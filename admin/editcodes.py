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
from model import Member

def generate_edit_codes():
    """ Mass update edit codes for members """
    for member in Member.all().fetch(3000):
        member.generate_access_code()
        member.put()


def nonone():
    """ Mass update fields set to 'None'. Please don't ask. """
    for member in Member.all().fetch(3000):
        mod = False
        if member.email == 'None':
            member.email = None
            mod = True

        if member.phone == 'None':
            member.phone = None
            mod = True

        if member.phone_work == 'None':
            member.phone_work = None
            mod = True

        if member.phone_home == 'None':
            member.phone_home = None
            mod = True

        if member.address == 'None':
            member.address = None
            mod = True

        if mod:
            member.put()

