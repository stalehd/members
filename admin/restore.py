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

from config import JINJA_ENVIRONMENT
from config import Configuration
from google.appengine.ext import db
from google.appengine.ext import deferred
from google.appengine.api import search

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

LIMIT_ALL = 3000


"""
Du a database restore based on the JSON dumped by the DataDump class.
"""

def task_user_restore(userlist):
    for user in userlist:
        newuser = User()
        newuser.email = user['email']
        newuser.save()

def task_config_restore(settings):
    config = Configuration()
    for setting in settings:
        config.set(setting['name'], setting['value'])

def task_country_restore(items):
    for item in items:
        country = Country(key_name=item['countryId'])
        country.order = item['order']
        country.name = item['name']
        country.put()

def task_status_restore(items):
    for item in items:
        status = Status(key_name=item['statusId'])
        status.order = item['order']
        status.name = item['name']
        status.put()

def task_type_restore(items):
    for item in items:
        mtype = MemberType(key_name=item['typeId'])
        mtype.order = item['order']
        mtype.name = item['name']
        mtype.fee = item['fee']
        mtype.put()

def task_model_restore(items):
    model_count = 0
    for item in items:
        mrange = ModelRange()
        mrange.name = item['name']
        mrange.year_start = item['yearStart']
        mrange.year_end = item['yearEnd']
        mrange.notes = item['notes']
        mrange.put()
        for model in item['carModels']:
            carmodel = CarModel(key_name=model['modelId'])
            carmodel.name = model['name']
            carmodel.engine_code = model['engineCode']
            carmodel.typeno = model['typeNo']
            if model['imageUrl'] != None:
                carmodel.imageUrl = db.Link(model['imageUrl'])
            carmodel.year_from = model['yearFrom']
            carmodel.year_to = model['yearTo']
            carmodel.notes = model['notes']
            carmodel.model_range = mrange
            carmodel.put()
            model_count = model_count + 1

def string_to_date(datestr):
    import time
    import datetime
    try:
        t = time.strptime(datestr, '%Y-%m-%d')
        return datetime.date(t.tm_year, t.tm_mon, t.tm_mday)
    except ValueError:
        return None

def task_member_restore(items):

    for item in items:
        member = Member()
        member.number = item['number']
        member.address = item['address']
        if item['email'] != '' and item['email'] != None:
            member.email = db.Email(item['email'])
        member.name = item['name']
        member.member_since = string_to_date(item['memberSince'])
        if item['phone'] != '' and item['phone'] != None:
            member.phone = db.PhoneNumber(item['phone'])
        if item['phoneWork'] != '' and item['phoneWork'] != None:
            member.phone_work = item['phoneWork']
        if item['phoneHome'] != '' and item['phoneHome'] != None:
            member.phone_home = item['phoneHome']
        member.notes = item['notes']
        member.zipcode = item['zipcode']
        member.city = item['city']
        member.county = item['county']
        member.country = db.get(db.Key.from_path('Country', item['countryId']))
        member.status = db.get(db.Key.from_path('Status', item['statusId']))
        member.membertype = db.get(db.Key.from_path('MemberType', item['typeId']))
        member.put()

        for itemdue in item['membershipDues']:
            due = MembershipDues(parent=member, year=itemdue['year'],paid=itemdue['paid'])
            due.put()

        for itemcar in item['cars']:
            car = Car()
            car.member = member
            car.registration = itemcar['registration']
            car.model = db.get(db.Key.from_path('CarModel', itemcar['modelId']))
            car.bought_year = itemcar['boughtYear']
            car.sold_year = itemcar['soldYear']
            car.year = itemcar['year']
            car.notes = itemcar['notes']
            car.serial_no = itemcar['serialNo']
            car.put()

class DataRestore(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/backup/restore.html')
        self.response.write(template.render({ 'message': '' }))

    def post(self):
        template = JINJA_ENVIRONMENT.get_template('templates/backup/restore.html')
        self.response.write(template.render({ 'message': 'Importing ' + self.request.get('filename') } ))

        content = self.request.get('contents')
        data = json.loads(content)

        ts = datetime.datetime.now().strftime('%Y-%m-%dT%H%M%S')

        deferred.defer(task_user_restore, data['users'], _name=('users_%s' % ts))
        deferred.defer(task_config_restore, data['config'], _name=('config_%s' % ts))
        deferred.defer(task_country_restore, data['countries'], _name=('countries_%s' % ts))
        deferred.defer(task_type_restore, data['types'], _name=('types_%s' % ts))
        deferred.defer(task_status_restore, data['status'], _name=('status_%s' % ts))

        # The limit for each task is 100KB; must limit the car and member lists
        # to something manageable. Limit to 50 and 50 users, 10 and 10 car ranges
        model_list = data['modelRanges']
        work_list = list()
        counter = 0
        while len(model_list) > 0:
            work_list.append(model_list.pop())
            if len(work_list) == 10:
                counter = counter + 1
                deferred.defer(task_model_restore, work_list, _name=('car_model_%d_%s' % (counter, ts)))
                work_list = list()
        if len(work_list) > 0:
            counter = counter + 1
            deferred.defer(task_model_restore, work_list, _name=('car_model_%d_%s' % (counter, ts)))

        counter = 0
        member_list = data['members']
        work_list = list()
        while len(member_list) > 0:
            work_list.append(member_list.pop())
            if len(work_list) == 25:
                counter = counter + 1
                deferred.defer(task_member_restore, work_list, _countdown=60, _name=('members_%d_%s' % (counter, ts)))
                work_list = list()
        if len(work_list) > 0:
            counter = counter + 1
            deferred.defer(task_member_restore, work_list, _countdown=60, _name=('members_%d_%s' % (counter, ts)))
