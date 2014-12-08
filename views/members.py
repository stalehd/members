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
""" The members view. """

from config import JINJA_ENVIRONMENT
from google.appengine.api import memcache
from google.appengine.api import search
from google.appengine.ext import db
from model import Car
from model import CarModel
from model import Country
from model import Member
from model import MemberType
from model import Status
from model import MembershipDues
import dbutils
import jinja2
import utils.auth
import datetime
import config

LIMIT = 50

class List(utils.auth.AuthHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/members/member_list.html')
        countries = Country.all().order('order').fetch(LIMIT)
        statuses = Status.all().order('order').fetch(LIMIT)
        types = MemberType.all().order('order').fetch(LIMIT)

        # TODO: Make sensible
        query_string = ''
        current_search = self.request.get('search')
        query_string +=  current_search

        current_status = self.request.get('status')
        if current_status != '':
            if query_string != '':
                query_string += ' AND '
            query_string += 'status:' + current_status

        current_type = self.request.get('type')
        if current_type != '':
            if query_string != '':
                query_string += ' AND '
            query_string += 'type:'+ current_type

        current_country = self.request.get('country')
        if current_country and current_country != '':
            if query_string != '':
                query_string += ' AND '
            query_string += 'country:' + current_country

        index = search.Index(name='members')
        result = index.search(query=search.Query(query_string, options=search.QueryOptions(limit=LIMIT)))

        members = list()
        for document in result.results:
            members.append(Member.search_member_from_document(document))

        members = sorted(members, key=lambda x: x.number)

        current_status_name = current_status
        current_type_name = current_type

        total = memcache.get('member_count')
        if not total:
            total = 0

        data = {
            'countries': countries,
            'statuses': statuses,
            'types': types,
            'members': members,
            'current_status': current_status,
            'current_type': current_type,
            'current_search': current_search,
            'found': result.number_found,
            'shown': len(members),
            'total': total
        }
        self.response.write(template.render(data))

class Detail(utils.auth.AuthHandler):
    def __add_missing_dues(self, dues, start, stop):
        years = range(start, stop + 1)
        for due in dues:
            if due.year in years:
                years.remove(due.year)
        for year in years:
            dues.append(MembershipDues(year=year, paid=False))

    def get(self, member_id):
        template = JINJA_ENVIRONMENT.get_template('templates/members/member_detail.html')
        countries = Country.all().order('order').fetch(LIMIT)
        statuses = Status.all().order('order').fetch(LIMIT)
        types = MemberType.all().order('order').fetch(LIMIT)
        member = Member.get(member_id)
        dues = MembershipDues.all().ancestor(member).fetch(25)
        current_year = datetime.datetime.now().year
        self.__add_missing_dues(dues, max(config.FIRST_YEAR_WITH_DUES, member.member_since.year), current_year + config.DUES_AHEAD)
        dues = sorted(dues, key=lambda item: item.year, reverse=True)
        data = {
            'countries': countries,
            'statuses': statuses,
            'types': types,
            'member': member,
            'dues': dues,
            'current_year': current_year
        }
        self.response.write(template.render(data))

    def save_dues(self, member):
        current_dues = MembershipDues.all().ancestor(member).fetch(25)
        current_year = datetime.datetime.now().year
        for year in range(current_year + config.DUES_AHEAD, config.FIRST_YEAR_WITH_DUES, -1):
            due_value = self.request.get('due' + str(year))
            if not due_value:
                continue
            paid = True if due_value == 'True' else False
            exists = False
            for due in current_dues:
                if due.year == year:
                    exists = True
                    if due.paid != paid:
                        due.paid = paid
                        due.put()
            if not exists:
                new_due = MembershipDues(parent=member, year=year, paid=paid)
                new_due.put()

    def post(self, member_id):

        if self.request.get('cancel') == '1':
            return self.redirect('/members')

        if self.request.get('operation') == 'delete_car':
            car = Car.get(self.request.get('car_key'))
            if car:
                car.delete()
            return self.redirect('/members/' + member_id + '/edit')



        member = Member.get(member_id)

        if self.request.get('operation') == 'new_car':
            car = Car()
            car.member = member
            car.model = dbutils.get_default_model()
            car.registration = ''
            car.year = 0
            car.notes = ''
            car.serial_no = ''
            car.put()
            return self.redirect('/members/' + member_id + '/car/' + str(car.key()) + '/edit' )

        member.name = self.request.get('name')
        member.address = self.request.get('address')
        member.zipcode = self.request.get('zip')
        member.city = self.request.get('city')
        member.country = Country.get(self.request.get('country'))
        phone = self.request.get('mobile').strip()
        if phone != '':
            member.phone = db.PhoneNumber(phone)
        else:
            member.phone = None
        email = self.request.get('email').strip()
        if email != '':
            member.email = db.Email(email)
        else:
            member.email = None
        home = self.request.get('fixed').strip()
        if home != '':
            member.phone_home = db.PhoneNumber(home)
        else:
            member.phone_home = None
        work = self.request.get('work').strip()
        if work != '':
            member.phone_work = db.PhoneNumber(work)
        else:
            member.phone_work = None
        member.membertype = MemberType.get(self.request.get('type'))
        member.status = Status.get(self.request.get('status'))
        member.notes = self.request.get('note')

        if self.request.get('access_code') == '':
            member.generate_access_code()
        # TODO: Options

        member.put()
        member.update_index()

        # save membership dues
        self.save_dues(member)

        return self.redirect('/members')


class MemberProcess(utils.auth.AuthHandler):
    def get_status(self, status_name):
        for status in Status.all().fetch(50):
            if status.name == status_name:
                return status
        return None

    """ Quick processing resource - progresses member through statuses """
    def post(self, member_id):
        import constants
        member = Member.get(member_id)
        if member.status.name == constants.SIGNUP_STATUS_NAME:
            member.status = self.get_status(constants.WELCOME_LETTER_NAME)
            # update the status to paid membership due.
            dues = MembershipDues.all().ancestor(member).fetch(25)
            current_year = datetime.datetime.now().year
            found = False
            for due in dues:
                if due.year == current_year:
                    due.paid = True
                    found = True
                    print 'Updated existing due'
                    due.put()
            if not found:
                print 'Due not found, created new'
                due = MembershipDues(parent=member, year=current_year, paid=True)
                due.put()
            member.put()
        elif member.status.name == constants.WELCOME_LETTER_NAME:
            member.status = self.get_status(constants.DEFAULT_MEMBER_STATUS_NAME)
            member.put()
        destination = self.request.get('return')
        return self.redirect(destination)

class CarDetail(utils.auth.AuthHandler):
    def get(self, member_id, car_id):
        template = JINJA_ENVIRONMENT.get_template('templates/members/car_detail.html')
        member = Member.get(member_id)
        car = Car.get(car_id)

        selector_template = JINJA_ENVIRONMENT.get_template('templates/carselector.html')

        data = {
            'car': car,
            'member': member,
            'carselector_html': selector_template.render()
        }
        self.response.write(template.render(data))

    def post(self, member_id, car_id):
        if self.request.get('cancel') == '1':
            return self.redirect('/members/' + member_id + '/edit')

        car = Car.get(car_id)
        car.registration = self.request.get('registration')
        yearstr = self.request.get('year')
        year = 0
        if yearstr != '':
            year = int(self.request.get('year'))

        if year > 0:
            car.year = year
        else:
            car.year = None

        yearstr = self.request.get('bought')
        year = 0
        if yearstr != '':
            year = int(self.request.get('bought'))
        if year > 0:
            car.bought_year = year
        else:
            car.bought_year = None

        yearstr = self.request.get('sold')
        year = 0
        if yearstr != '':
            year = int(self.request.get('sold'))

        if year > 0:
            car.sold_year = year
        else:
            car.sold_year = None

        model_key = self.request.get('model_key')
        if not car.model or not str(car.model.key()) == model_key:
            car.model = CarModel.get(model_key)

        car.serial_no = self.request.get('serial_no')
        car.notes = self.request.get('note')
        car.put()
        return self.redirect('/members/' + member_id + '/edit')
