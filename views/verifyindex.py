# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# Portello membership system
# Copyright (C) 2015 Klubb Alfa Romeo Norge
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
"""
Do index check. Iterate over all elements in the member database, check if 
the entry is in the index. If not - log warning and add to index.

Annoying but There Be Bugs.
"""

from google.appengine.ext import db
import logging
from google.appengine.api import search
from model import Member

LIMIT_ALL = 4000

def do_index_verification():
	member_list = Member.all().fetch(LIMIT_ALL)
	index = search.Index(name='members')
	for member in member_list:
		query =

		result = index.search(query=search.Query('number:' + member.number, options=search.QueryOptions(limit=10)))
		logging.debug('Found ' + str(len(result))) + ' members with number ' + member.number
		