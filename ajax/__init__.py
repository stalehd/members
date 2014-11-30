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
from model import ModelRange
LIMIT_ALL = 20000

class Range(webapp2.RequestHandler):
    def year(self, year):
        if year == 0:
            return datetime.date.today().year
        return year

    def prettyprint_years(self, start, stop):
        if stop == 0:
            return '%d-' % (start)
        return '%d-%d' % (start, stop)

    def get(self):
        ranges = ModelRange.all().fetch(500)
        # Some trickery to sort the ranges properly
        ranges = sorted(ranges, key=lambda range: -self.year(range.year_end))
        ret = []
        for modelrange in ranges:
            # Skip the generic one
            if modelrange.name != 'Alfa Romeo' and modelrange.name != 'Ukjent':
                ret.append({
                    'key': str(modelrange.key()),
                    'name': modelrange.name,
                    'years': self.prettyprint_years(modelrange.year_start, modelrange.year_end)})

        self.response.content_type = 'application/json'
        self.response.write(json.dumps(ret))


class Model(webapp2.RequestHandler):
    def year(self, year):
        if year == 0:
            return datetime.date.today().year
        return year

    def prettyprint_years(self, start, stop):
        if stop == 0:
            return '%d-' % (start)
        return '%d-%d' % (start, stop)

    def get(self, range_id):
        modelrange = ModelRange.get(range_id)
        ret = []
        if modelrange:
            models = modelrange.models.fetch(500)
            models = sorted(models, key=lambda model: -self.year(model.year_to))
            for model in models:
                ret.append({
                    'key': str(model.key()),
                    'name': model.name,
                    'tipo': model.typeno,
                    'motore': model.engine_code,
                    'years': self.prettyprint_years(model.year_from, model.year_to)
                    })

        self.response.content_type = 'application/json'
        self.response.write(json.dumps(ret))
