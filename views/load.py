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
from model import Car
from model import CarModel
from model import Country
from model import Member
from model import MembershipDues
from model import MemberType
from model import ModelRange
from model import Status
from model import User
import jinja2
import utils.auth
import utils.carconversion
import webapp2

class Loader(webapp2.RequestHandler):
    typelist = None
    statuslist = None
    countrylist = None

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/loader/loader.html')
        data = { 'request_body': self.request.get('data') }
        self.response.write(template.render(data))


    def import_countries(self, country_csv):
        countries = []
        lines = country_csv.split('\n')
        for line in lines:
            if len(line.strip()) > 0:
                fields = line.split(';')
                country = Country()
                country.order = int(fields[0])
                country.name = fields[1].strip()
                country.local_name = fields[2].strip()
                country.put()
                countries.append(country)

        return countries;

    def import_statuses(self, status_csv):
        statuses = []
        lines = status_csv.split('\n')
        for line in lines:
            if len(line.strip()) > 0:
                fields = line.split(';')
                status = Status()
                status.order = int(fields[0])
                status.name = fields[1].strip()
                status.put()
                statuses.append(status)

        return statuses;

    def import_types(self, type_csv):
        types = []
        lines = type_csv.split('\n')
        for line in lines:
            if len(line.strip()) > 0:
                fields = line.split(';')
                membertype = MemberType()
                membertype.order = int(fields[0])
                membertype.name = fields[1].strip()
                membertype.fee = int(fields[2])
                membertype.put()
                types.append(membertype)

        return membertype;

    def string_to_date(self, datestr):
        import time
        import datetime
        try:
            t = time.strptime(datestr, '%d.%m.%Y')
            return datetime.date(t.tm_year, t.tm_mon, t.tm_mday)
        except ValueError:
            return None

    def get_country(self, name):
        for country in self.countrylist:
            if country.name == name:
                return country
        print '*** Could not find country ', name, '-- wtf?'
        return None

    def string_to_country(self, countrystr):
        name = countrystr.strip()
        if name == '':
            return self.get_country('Norge')
        if name == 'DANMARK':
            return self.get_country('Danmark')
        if name == 'England':
            return self.get_country('England')
        if name == 'FINLAND':
            return self.get_country('Finland')
        if name == 'Polen':
            return self.get_country('Polen')
        if name == 'Sverige':
            return self.get_country('Sverige')
        if name == 'USA':
            return self.get_country('USA')
        if name == 'United Arab Emirates':
            return self.get_country('United Arab Emirates')
        if name == 'Norge':
            return self.get_country('Norge')

        print 'Warning: Don''t know how to country',countrystr,'defaulting to Norge'
        return self.get_country('Norge')

    def get_member_type(self, name):
        for mtype in self.typelist:
            if mtype.name == name:
                return mtype
        print '!'*80
        print 'Could not find member type',name,'Using none'
        print '!'*80
        return None

    def string_to_type(self, typestr):
        if typestr == 'Alfanytt':
            return self.get_member_type(u'Alfanytt')
        if typestr == 'Standardmedlem':
            return self.get_member_type(u'Medlem')
        if typestr == 'Styremedlem':
            return self.get_member_type(u'Medlem')
        if typestr == u'Støttemedlem':
            return self.get_member_type(u'Støttemedlem')
        if typestr == u'Æresmedlem':
            return self.get_member_type(u'Hedersmedlem')

        print '*'*80
        print 'Can''t member type',typestr,'defaulting to Medlem'
        return self.get_member_type(u'Medlem')

    def get_status(self, name):
        for status in self.statuslist:
            if status.name == name:
                return status
        print 'Can''t status',name,'this bad'
        return None

    def add_due(self, member, year, paid):
        due = MembershipDues(parent=member, year=year, paid=paid)
        due.put()

    def unmangle(self, lines):
        EXPECTED=36

        ret = list()
        all_line = ''
        first_line = True
        for line in lines:
            if len(line.strip()) == 0:
                continue

            # skip first line in file
            if first_line:
                first_line = False
                continue

            line = line.strip()
            if len(all_line) > 0:
                line = all_line + ' ' + line

            all_fields = line.split(';')
            verbose = False
            if len(all_fields) < EXPECTED:
                all_line = line
            if len(all_fields) == EXPECTED:
                ret.append(all_fields)
                all_line = ''
            if len(all_fields) > EXPECTED:
                print 'BUGGER',len(all_fields)
                all_line = ''
        return ret

    def import_members(self, member_csv):
        member_csv = member_csv.split('\n')
        lines = self.unmangle(member_csv)

        count = 0
        for fields in lines:
            #fields.reverse()
            print '-'*80
            print fields
            print '='*80
            fields.reverse()
            member = Member()

            (fee2009, fee2010, fee2011,
                fee2012, fee2013, fee2014) = (
                    fields.pop(), fields.pop(), fields.pop(),
                    fields.pop(), fields.pop(), fields.pop())

            member.address = fields.pop()
            # Skip the cars
            for carno in range(1,6):
                (car, registration) = (fields.pop(), fields.pop())

            email = fields.pop()
            if email != '':
                member.email = db.Email(email)

            (lastname, firstname) = (fields.pop(), fields.pop())
            full_name = firstname + ' ' + lastname
            member.name = full_name.strip()

            member.county = fields.pop().strip()
            member_since = fields.pop()
            date = self.string_to_date(member_since)
            if date:
                member.member_since = date
            else:
                print 'Error converting date from',member_since

            country = fields.pop().strip()
            if country == '':
                country = 'Norge'
            member.country = self.string_to_country(country)
            member.membertype = self.string_to_type(fields.pop())
            member.number = fields.pop()
            mobile = fields.pop()
            if mobile != '':
                member.phone = db.PhoneNumber(mobile)

            member.notes = fields.pop()
            member.zipcode = fields.pop()
            member.city = fields.pop()
            work = fields.pop()
            home = fields.pop()
            if work != '':
                member.phone_work = db.PhoneNumber(work)
            if home != '':
                member.phone_home = db.PhoneNumber(home)
            member.status = self.get_status('Medlem')
            member.generate_access_code()
            member.put()

            self.add_due(member, 2009, fee2009=='Betalt')
            self.add_due(member, 2010, fee2010=='Betalt')
            self.add_due(member, 2011, fee2011=='Betalt')
            self.add_due(member, 2012, fee2012=='Betalt')
            self.add_due(member, 2013, fee2013=='Betalt')
            self.add_due(member, 2014, fee2014=='Betalt')
            count = count + 1


        print 'Imported',count,'members'

    def import_model_range(self, csv):
        lines = csv.split('\n')
        imported = 0
        for line in lines:
            if len(line.strip()) == 0:
                print 'Skipping line',line
                continue
            model_range = ModelRange()
            fields = line.strip().split(';')
            model_range.name = fields[0]
            model_range.year_start = int(fields[1])
            model_range.year_end = int(fields[2])
            model_range.put()
            imported = imported+1
        print imported,'ranges imported'

    def get_range(self, ranges, name):
        for model_range in ranges:
            if model_range.name.strip() == name.strip():
                return model_range
        print 'WARNING: Unknown range: ' + name
        return None

    def import_car_models(self, csv):
        ranges = ModelRange.all().fetch(100)
        imported = 0
        lines = csv.split('\n')
        for line in lines:
            if len(line.strip()) == 0:
                print 'Skipping line',line
                continue
            model = CarModel()
            fields = line.strip().split(';')
            model.model_range = self.get_range(ranges, fields[0].strip())
            model.name = fields[1].strip()
            model.engine_code = fields[2].strip()
            model.typeno = fields[3].strip()
            if fields[4].strip() != '':
                model.image_url = db.Link(fields[4].strip())
            model.year_from = int(fields[5])
            model.year_to = int(fields[6])
            model.notes = fields[7].strip()
            model.put()
            imported = imported + 1
        print imported,'models imported'

    ranges = None
    models = None
    def get_model(self, model_name):
        for model in self.models:
            if model.name == model_name:
                return model
        print 'WARNING: Unknown model name:',model_name
        return None

    def print_member_car(self, car, range_name, model_name, note):
        line = u'%d; %s => %s/%s' % (car.year, unicode(car.description), range_name, model_name)
        print line.encode('ascii', 'ignore')

    def create_member_car(self, car, range_name, model_name, note):
        members = Member.all().filter('number',car.memberno).fetch(10)
        if len(members) == 0:
            print 'WARNING: Could not look up member with no.',car.memberno
            return

        member_car = Car()
        member_car.member = members[0]
        member_car.model = self.get_model(model_name)
        member_car.registration = car.registration
        member_car.year = int(car.year)
        member_car.notes = note
        member_car.serial_no = ''
        member_car.put()

    def import_member_cars(self, csv):
        import traceback
        from utils.carconversion import MemberCar
        self.models = CarModel.all().fetch(2000)

        cars = []
        lines = csv.split('\n')
        for line in lines:
            if len(line.strip()) == 0:
                continue

            fields = line.split(';')
            fields.reverse()
            car = MemberCar(memberno=fields.pop())
            car.description = fields.pop().strip()
            car.registration = fields.pop().strip()
            year = fields.pop().strip()
            if year != '':
                car.year = int(year)
            else:
                car.year = 0
            cars.append(car)

        print len(cars), 'cars imported'
        print len(self.models), 'models to use'
        try:
            print utils.carconversion.CarRank.do_matching(self.models, cars, self.create_member_car)
        except Exception as ex:
            print 'Exception matching car: ',ex
            print '*'*80
            traceback.print_exc()
            print '*'*80


    def import_users(self, csv):
        lines = csv.split('\n')
        for line in lines:
            if len(line.strip()) == 0:
                continue
            user = User()
            user.email = line.strip()
            user.put()

    def post(self):
        template = JINJA_ENVIRONMENT.get_template('templates/loader/loader.html')

        content = self.request.get('type')

        countries = []
        if content == 'countries.csv':
            countries = self.import_countries(self.request.get('data'))

        statuses = []
        if content == 'status.csv':
            statuses = self.import_statuses(self.request.get('data'))

        types = []
        if content == 'types.csv':
            types = self.import_types(self.request.get('data'))

        if content == 'member.csv':
            self.statuslist = Status.all().fetch(100)
            self.typelist = MemberType.all().fetch(100)
            self.countrylist = Country.all().fetch(100)
            self.import_members(self.request.get('data'))

        if content == 'model_ranges.csv':
            self.import_model_range(self.request.get('data'))

        if content == 'car_models.csv':
            self.import_car_models(self.request.get('data'))

        if content == 'cars.csv':
            self.import_member_cars(self.request.get('data'))

        if content == 'users.csv':
            self.import_users(self.request.get('data'))

        self.response.write(template.render())

