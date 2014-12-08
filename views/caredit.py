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
""" Car editing view. Enable quick edit of cars to clean up the data """

from config import JINJA_ENVIRONMENT
from google.appengine.ext import db
from model import Car
from model import CarModel

import dbutils
import jinja2
import utils.auth
import datetime
import config

class LookupReg(object):
    def reformat(self, registration):
        return registration.upper().replace(' ', '')

    def get_link(self, registration):
        if not registration:
            return ''
        if registration.strip() == '':
            return ''

        return """
<a target="_blank" href="http://www.vegvesen.no/Kjoretoy/Eie+og+vedlikeholde/Periodisk+kjoretoykontroll/Kontrollfrist?registreringsnummer=%s">%s</a>
            """ % (self.reformat(registration), registration)

class CarEdit(utils.auth.AuthHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/caredit/list.html')

        unknown = CarModel.all().filter('name =', 'Annet').fetch(5)
        assert len(unknown)==1
        unknown_cars = Car.all().filter('model =', unknown[0]).fetch(50)

        other = CarModel.all().filter('name =', 'Annen Alfa Romeo').fetch(5)
        assert len(other)==1
        other_cars = Car.all().filter('model =', other[0]).fetch(50)

        data = { 'cars': other_cars + unknown_cars, 'linker': LookupReg() }
        self.response.write(template.render(data))

    def post(self):
        import datetime

        car_key = self.request.get('car_key')
        model_key = self.request.get('model_key')

        car = Car.get(car_key)
        car.model = CarModel.get(model_key)
        car.notes = ''
        car.put()
        print 'Updated car model to',car.model.name
        ts = datetime.datetime.now()
        return self.redirect('/caredit?tag='+str(ts.time().microsecond))

