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
"""
Du a dump of the database. This will do a complete backup of the data in the
data store and can be used to restore the data when everything goes bump in the
night.

"Why write everything *again* you might ask. Well - from experience it is nice
to have an alternative to access your data. If GAE goes away it will be
possible to run the app 1990's style on a single computer, export the data when
(or if) everything comes back up and then continue as before. Backups are also
nice if something goes horribly wrong in the app itself and data gets deleted.
It might happen.
"""

import webapp2
import json
import datetime
import os

from google.appengine.ext import deferred
from google.appengine.ext import db
import cloudstorage as gcs

from config import JINJA_ENVIRONMENT
from config import BACKUP_BUCKET
from config import Configuration
from model import Member
from model import User
from model import Status
from model import Country
from model import MemberType
from model import ModelRange
from model import CarModel
from model import Car
from model import ConfigTuple
from model import MembershipDues

LIMIT_ALL = 10000

def task_do_backup(filename):
    dump = DataDump()

    contents = dump.get_json_dump()

    write_retry_params = gcs.RetryParams(backoff_factor=1.1)
    gcs_file = gcs.open(filename,
        'w',
        content_type='application/json',
        retry_params=write_retry_params)
    gcs_file.write(contents)
    gcs_file.close()

class DataDump:
    def do_backup(self):
        ts = datetime.datetime.now().strftime('%Y-%m-%dT%H%M%S')
        filename = '/%s/backups/backup_%s.json' % (BACKUP_BUCKET, ts)
        deferred.defer(task_do_backup, filename, _name='backup_' + ts)
        return filename

    """ Do a data dump of *everything*. Will break for large amounts of data
    but works just fine for smaller amounts """
    def get_json_dump(self):
        """ Dump everything as JSON """
        data_dump = {}
        #data_dump['members'] = self.get_members()

        data_dump['config'] = self.__to_list(ConfigTuple, lambda item: {
                'name': unicode(item.key().name()),
                'value': item.value
            })

        data_dump['users'] = self.__to_list(User, lambda item: {
                'email': unicode(item.email)
            })

        data_dump['status'] = self.__to_list(Status, lambda item: {
                'statusId': unicode(item.key()),
                'order' : item.order,
                'name': item.name
            })
        data_dump['types'] = self.__to_list(MemberType, lambda item: {
                'typeId': unicode(item.key()),
                'order': item.order,
                'name': item.name,
                'fee': item.fee
            })

        data_dump['countries'] = self.__to_list(Country, lambda item: {
                'countryId': unicode(item.key()),
                'order': item.order,
                'name': item.name
            })

        data_dump['modelRanges'] = self.__to_list(ModelRange, lambda item: {
                'name': item.name,
                'yearStart': item.year_start,
                'yearEnd': item.year_end,
                'notes': item.notes,
                'carModels': self.__get_collection(item.models, lambda item: {
                        'modelId': unicode(item.key()),
                        'name': item.name,
                        'engineCode': item.engine_code,
                        'typeNo': item.typeno,
                        'imageUrl': item.image_url,
                        'yearFrom': item.year_from,
                        'yearTo': item.year_to,
                        'notes': item.notes
                    })
            })

        # TODO: Options
        data_dump['members'] = self.__to_list(Member, lambda item: {
                'number': unicode(item.number),
                'address': unicode(item.address),
                'email': item.email,
                'name': unicode(item.name),
                'county': unicode(item.county),
                'memberSince': unicode(item.member_since),
                'countryId': unicode(item.country.key()),
                'typeId': unicode(item.membertype.key()),
                'statusId': unicode(item.status.key()),
                'phone': item.phone,
                'notes': item.notes,
                'zipcode': unicode(item.zipcode),
                'city': unicode(item.city),
                'phoneWork': item.phone_work,
                'phoneHome': item.phone_home,
                'cars': self.__get_collection(item.cars, lambda item: {
                        'modelId': unicode(item.model.key()),
                        'registration': item.registration,
                        'boughtYear': item.bought_year,
                        'soldYear': item.sold_year,
                        'year': item.year,
                        'notes': item.notes,
                        'serialNo': item.serial_no
                    }),
                'membershipDues': self.__get_collection(MembershipDues.all().ancestor(item).fetch(100), lambda item: {
                        'year': item.year,
                        'paid': item.paid
                    })
            })

        return json.dumps(data_dump)

    def __get_collection(self, collection, convert):
        """ Convert a collection into python objects """
        ret = []
        for item in collection:
            ret.append(convert(item))
        return ret

    def __to_list(self, entity, convert):
        """ Convert a data set into python objects """
        return self.__get_collection(entity.all().fetch(LIMIT_ALL), convert)
