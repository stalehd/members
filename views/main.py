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
from google.appengine.api import search

import jinja2
import utils.auth
import utils.counter
import webapp2
import constants
from model import Member

LIMIT = 200

class StartPage(utils.auth.AuthHandler):
    def skip_member(self, document):
        for field in document.fields:
                if field.name == 'type' and field.value == constants.MEMBER_TYPE_EXPIRED:
                    return True
        return False

    def members_with_status(self, status_name):
        index = search.Index(name='members')
        results = index.search(query=search.Query('status:' + status_name, options=search.QueryOptions(limit=LIMIT)))

        ret = list()
        for document in results:
            if not self.skip_member(document):
                ret.append(Member.search_member_from_document(document))
        return ret

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/start.html')


        data = {
            'counter': utils.counter.DataStoreCounter(),
            'signed_up': self.members_with_status(constants.SIGNUP_STATUS_NAME),
            'welcome_letter': self.members_with_status(constants.WELCOME_LETTER_NAME)
            }
        self.response.write(template.render(data))

    def get_entity_count(self, entity):
        count = memcache.get(entity)
        if count is not None:
            return count
        return 0

