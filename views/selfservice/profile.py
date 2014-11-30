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
from config import JINJA_ENVIRONMENT
import jinja2
import webapp2
from model import Member

COOKIE_NAME = 'karn_profile'
SESSION_DURATION = 3600
FETCH_LIMIT = 100

class Login(webapp2.RequestHandler):
    def get(self):
        # Delete the cookie and show the login form
        self.response.delete_cookie(COOKIE_NAME)
        template = JINJA_ENVIRONMENT.get_template('templates/selfservice/profile_login.html')
        self.response.write(template.render())

    def create_cookie(self, memberno, access_code):
        cookie_value = '%s:%s' % (memberno, access_code)
        self.response.set_cookie(COOKIE_NAME, value=str(cookie_value), max_age=SESSION_DURATION, overwrite=True)

    def get_required(self, name):
        value = self.request.get(name)
        if not value or value.strip() == '':
            self.abort(400)

        return value.strip().lower()

    def post(self):
        # User (tries to) log in. Check member no and access code.
        try:
            memberno = self.get_required('memberno')
            access_code = self.get_required('accesscode')

            members = Member.all().filter('number', memberno).fetch(1)
            if len (members) < 1:
                self.abort(400)

            if members[0].edit_access_code.lower() != access_code:
                self.abort(400)

            self.create_cookie(memberno, access_code)

            return self.redirect('profile/' + str(members[0].key()) + '/edit')

        except Exception as ex:
            print 'Got exception:',ex
            # bounce to login page
            self.response.delete_cookie(COOKIE_NAME)
            return self.redirect('profile')


class Logout(webapp2.RequestHandler):
    """ Simple logout handler -- just delete the cookie and redirect to profile page """

    def get(self):
        self.response.delete_cookie(COOKIE_NAME)
        return self.redirect('profile')
