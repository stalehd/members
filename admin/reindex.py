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

import webapp2
import json
import datetime

from config import JINJA_ENVIRONMENT
from config import Configuration
from google.appengine.ext import db
from google.appengine.ext import deferred
from google.appengine.api import search

from model import Member
from model import MembershipDues
from admin import Admin

LIMIT_ALL = 3000

def reindex_stuff(dummy):
    a = Admin()
    a.rebuild_index()

class Reindex(webapp2.RequestHandler):
    def get(self):
        ts = datetime.datetime.now().strftime('%Y-%m-%dT%H%M%S')

        deferred.defer(reindex_stuff, [], _name=('rebuild_index_'+ts))

        self.response.write('Task submitted')

