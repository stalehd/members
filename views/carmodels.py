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
from google.appengine.api import memcache
from google.appengine.ext import db
from model import CarModel
from model import ModelRange
import jinja2
import utils.auth
import utils.counter

class RangeList(utils.auth.AuthHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/carmodels/range_list.html')
        ranges = ModelRange.all().order('-year_start').fetch(500)
        data = { 'ranges' : ranges, 'counter': utils.counter.DataStoreCounter() }
        self.response.write(template.render(data))

class RangeDetail(utils.auth.AuthHandler):
    def get(self, range_id):
        template = JINJA_ENVIRONMENT.get_template('templates/carmodels/range_detail.html')
        model_range = ModelRange().get(range_id)

        data = {
            'range': model_range,
            'models': sorted(model_range.models, key=lambda x: -x.year_from),
            'counter': utils.counter.DataStoreCounter()
        }

        self.response.write(template.render(data))

    def post(self, range_id):
        if self.request.get('cancel') == '1':
            return self.redirect('/ranges')

        model = ModelRange.get(range_id)
        model.name = self.request.get('name')
        model.year_start = int(self.request.get('yearfrom'))
        model.year_end = int(self.request.get('yearto'))
        model.notes = self.request.get('notes')
        model.put()
        return self.redirect('/ranges')

class ModelDetail(utils.auth.AuthHandler):
    def get(self, range_id, model_id):
        template = JINJA_ENVIRONMENT.get_template('templates/carmodels/model_detail.html')
        model_range = ModelRange.get(range_id)
        car_model = CarModel.get(model_id)
        data = {
            'range': model_range,
            'model': car_model
        }
        self.response.write(template.render(data))

    def post(self, range_id, model_id):
        model_range = ModelRange.get(range_id)
        if self.request.get('cancel') == '1':
            return self.redirect('/ranges/' + str(model_range.key()) + '/edit')


        model = CarModel.get(model_id)
        model.name = self.request.get('name')
        model.year_from = int(self.request.get('yearfrom'))
        model.year_to = int(self.request.get('yearto'))
        model.typeno = self.request.get('tipo')
        model.engine_code = self.request.get('engine')
        url = self.request.get('image_url')
        if url != '':
            model.image_url = db.Link(url)
        model.notes = self.request.get('notes')
        model.put()
        return self.redirect('/ranges/' + str(model_range.key()) + '/edit')

