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
"""Various constants (that probably should be config options later on)"""

# Name of the ordinary member type
DEFAULT_MEMBER_NAME = 'Medlem'
# Name of the support membership type
DEFAULT_SUPPORT_MEMBER_NAME = 'Støttemedlem'

# Name of the status newly signed up members should be set to
SIGNUP_STATUS_NAME = 'Innmeldt'
# Name of status for members that have received welcome letter
WELCOME_LETTER_NAME = 'Velkomstpakke'
DEFAULT_MEMBER_STATUS_NAME = 'Medlem'

SERVER_URL = 'https://klubbalfaromeonorge.appspot.com'
PROFILE_URL = SERVER_URL + '/selfservice/profile'

DEFAULT_MODEL_NAME = 'Annen Alfa Romeo'

MEMBER_TYPE_EXPIRED = 'Utmeldt'
