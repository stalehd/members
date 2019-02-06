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
from model import Member
from model import Country
import jinja2
import webapp2
from dbutils import is_valid, is_valid_email, is_valid_country
from google.appengine.ext import db
COOKIE_NAME = 'karn_profile'
SESSION_DURATION = 3600
FETCH_LIMIT = 100


class Form(webapp2.RequestHandler):
    def get_cookie(self):
        cookie = self.request.cookies.get(COOKIE_NAME)
        if not cookie:
            self.abort(400)

        fields = cookie.split(':')
        if len(fields) > 2 or len(fields) < 2:
            # Something's fishy
            self.response.delete_cookie(COOKIE_NAME)
            self.abort(400)

        memberno = fields[0]
        access_code = fields[1]
        return (memberno, access_code)

    def get_member(self, member_no):
        (memberno, access_code) = self.get_cookie()

        member = Member.get(member_no)
        if not member:
            self.abort(400)

        if not member.number == memberno:
            self.abort(400)

        if member.edit_access_code.lower().strip() != access_code:
            self.abort(400)

        return member

    def get(self, member_no):
        member = self.get_member(member_no)
        countries = Country.all().order('order').fetch(FETCH_LIMIT)

        # OK - everything checks out - show edit form
        template = JINJA_ENVIRONMENT.get_template(
            'templates/selfservice/profile_edit.html')

        data = {'member': member, 'countries': countries}
        self.response.write(template.render(data))

    def get_required(self, name):
        value = self.request.get(name)
        if not value or value.strip() == '':
            print 'Missing value ', name, 'from profile update. Sending 400.'
            # TODO: Do it nicer.
            self.abort(400)
        return value.strip()

    def post(self, member_no):
        member = self.get_member(member_no)

        member.name = self.get_required('name')
        member.address = self.get_required('address')
        member.zipcode = self.get_required('zip')
        member.city = self.get_required('city')
        country = Country.get(self.get_required('country'))

        email = self.get_required('email')
        if email != '':
            member.email = db.Email(email)

        mobile = self.get_required('mobile')
        if mobile != '':
            member.phone = db.PhoneNumber(mobile)

        home = self.request.get('fixed')
        if home != '':
            member.phone_home = db.PhoneNumber(home)

        work = self.request.get('work')
        if work != '':
            member.phone_work = db.PhoneNumber(work)

        member.put()
        member.update_index()

        template = JINJA_ENVIRONMENT.get_template(
            'templates/selfservice/profile_edit.html')
        countries = Country.all().order('order').fetch(FETCH_LIMIT)

        data = {'message': 'Medlemsprofilen din er oppdatert.',
                'member': member, 'countries': countries}
        self.response.write(template.render(data))
