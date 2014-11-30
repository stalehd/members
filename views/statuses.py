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
from model import Status
import jinja2
import utils.auth
from utils.counter import DataStoreCounter

class List(utils.auth.AuthHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/statuses/list.html')

        statuses = Status.all().order('order').fetch(100)

        data = { 'statuses' : statuses, 'counter': DataStoreCounter() }
        self.response.write(template.render(data))

class Detail(utils.auth.AuthHandler):
    def get(self, status_id):
        template = JINJA_ENVIRONMENT.get_template('templates/statuses/detail.html')

        status = Status.get(status_id);
        data = { 'status': status }
        self.response.write(template.render(data))

    def post(self, status_id):
        if self.request.get('cancel') == '1':
            return self.redirect('/statuses')

        status = Status.get(status_id)
        status.name = self.request.get('statusname')
        status.order = int(self.request.get('order'))
        status.put()
        return self.redirect('/statuses')
