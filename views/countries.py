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
from google.appengine.ext import db
from model import Country
import jinja2
import utils.auth
from utils.counter import DataStoreCounter

class List(utils.auth.AuthHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/countries/list.html')

        countries = Country.all().order('order').fetch(500)
        data = { 'countries' : countries, 'counter': DataStoreCounter() }
        self.response.write(template.render(data))

    def post(self):
        if (self.request.get('action') == 'delete'):
            print 'Will delete '+self.request.get('deletelist')
        return self.redirect('/countries')


class Detail(utils.auth.AuthHandler):
    def get(self, country_key):
        template = JINJA_ENVIRONMENT.get_template('templates/countries/detail.html')
        country = Country.get(country_key)
        data = { 'country_key': country_key, 'country': country }
        self.response.write(template.render(data))

    def post(self, country_key):
        if (self.request.get('cancel') == '1'):
            return self.redirect('/countries')

        country = Country.get(country_key)
        country.order = int(self.request.get('order'))
        country.name = self.request.get('countryname')
        country.put()
        return self.redirect('/countries')

