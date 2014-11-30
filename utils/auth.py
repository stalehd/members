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
"""Override the default request handler to add (simple) authentication
for resources."""

from google.appengine.api import memcache
from google.appengine.api import users
from model import User
import webapp2

class AuthHandler(webapp2.RequestHandler):
    """Authentication handler. Extend this to require a valid
    user (not only authenticated but one in the users element)"""

    def dispatch(self):
        """Overridden"""

        user_list = memcache.get('app_users')
        if not user_list:
            user_list = []
            for user in User.all().fetch(100):
                user_list.append(str(user.email))
            memcache.set('app_users', user_list)

        user = users.get_current_user()
        if not user or not user.email() in user_list:
            self.redirect('/static/nofly.html')
            return
        super(AuthHandler, self).dispatch()

