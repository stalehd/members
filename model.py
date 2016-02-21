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
"""Data model for app."""
from google.appengine.ext import db
from google.appengine.api import search
from google.appengine.api import memcache
import datetime
YEAR_MAX = 25

class Country(db.Model):
    """Country. Just to make things simple."""

    # Sorting order.
    order = db.IntegerProperty(default=1)

    # Local name.
    name = db.StringProperty()

    # Name of country when sending snail-mail
    local_name = db.StringProperty()

class Status(db.Model):
    """Member state. Not to be confused with member *type*."""

    order = db.IntegerProperty(default=1)
    name = db.StringProperty()


class MemberType(db.Model):
    """Types of member."""

    order = db.IntegerProperty(default=1)
    name = db.StringProperty()
    fee = db.IntegerProperty()
    active = db.BooleanProperty(default=True)


class SearchMember():
    """ A pseudo-member generated from the search results. Not used as proper
    members """
    pass

class Member(db.Model):
    """A member"""

    number = db.StringProperty(indexed=True)
    address = db.StringProperty()
    email = db.EmailProperty(required=False)
    name = db.StringProperty()
    county = db.StringProperty()
    member_since = db.DateProperty(required=False)
    country = db.ReferenceProperty(Country, collection_name='members')
    membertype = db.ReferenceProperty(MemberType, collection_name='members')
    status = db.ReferenceProperty(Status, collection_name='members')
    phone = db.PhoneNumberProperty(required=False)
    notes = db.TextProperty(required=False)
    zipcode = db.StringProperty()
    city = db.StringProperty()
    phone_work = db.PhoneNumberProperty(required=False)
    phone_home = db.PhoneNumberProperty(required=False)
    user = db.UserProperty(required=False)
    edit_access_code = db.StringProperty(required=False)
    last_change = datetime.datetime.now()
    magazine_count = db.IntegerProperty(required=False, default=1)
    
    def put(self, **kwargs):
        # update the last_change flag
        self.last_change = datetime.datetime.now()
        super(Member, self).put(**kwargs)

        # Update search index with updated values after saving. Note that
        # this is half-assed and puts via db.put() must be handled
        # differently.
        self.update_index()

    @classmethod
    def search_member_from_document(cls, document):
        ret = SearchMember()
        ret.key = document.doc_id
        for field in document.fields:
            if field.name == 'number':
                ret.number = field.value
            if field.name == 'name':
                ret.name = field.value
            if field.name == 'address':
                ret.address = field.value
            if field.name == 'country':
                ret.country = field.value
            if field.name == 'type':
                ret.membertype = field.value
            if field.name == 'email':
                ret.email = field.value
            if field.name == 'status':
                ret.status = field.value
            if field.name == 'phone':
                ret.phone = field.value
            if field.name == 'zip':
                ret.zipcode = field.value
            if field.name == 'city':
                ret.city = field.value
        return ret

    def create_document(self):
        """ Create document to enable full-text search """
        if not self.membertype:
            print 'Missing member type for', ascii(self.name), self.number

        fieldlist = [
            search.TextField(name='name', value=self.name),
            search.TextField(name='address', value=self.address),
            search.TextField(name='country', value=self.country.name),
            search.TextField(name='county', value=self.county),
            search.TextField(name='notes', value=self.notes),
            search.TextField(name='status', value=self.status.name),
            search.TextField(name='type', value=self.membertype.name),
            search.TextField(name='number', value=self.number),
            search.TextField(name='zip', value=self.zipcode),
            search.TextField(name='city', value=self.city)
        ]
        if self.member_since:
            search.DateField(name='membersince', value=self.member_since),
        if self.email:
            fieldlist.append(search.TextField(name='email', \
                value=self.email))
        if self.phone:
            fieldlist.append(search.TextField(name='phone', \
                value=self.phone))
        if self.phone_work:
            fieldlist.append(search.TextField(name='phone_work', \
                value=self.phone_work))
        if self.phone_home:
            fieldlist.append(search.TextField(name='phone_home', \
                value=self.phone_home))

        current_year = datetime.datetime.now().year
        paid_dues = {}
        for year in range(current_year-5, current_year+5):
            paid_dues[year] = 0
        dues = MembershipDues.all().ancestor(self).fetch(YEAR_MAX)
        for due in dues:
            if due.paid:
                paid_dues[due.year] = 1

        for index_due in range(current_year-5, current_year+5):
            fieldlist.append(search.NumberField(name='kontingent' + str(index_due), value=paid_dues[index_due]))

        # TODO: Add cars to index?
        return search.Document(
            doc_id=str(self.key()),
            fields=fieldlist)

    def update_index(self):
        index = search.Index(name='members')
        index.put(self.create_document())

    def generate_access_code(self):
        import os
        """Create easy readable access code for profile editing"""

        # This is the alphabet we can use; l, I, 1 and 0, O are obvious,
        # S, 5 not so much,  8 and B a little less.
        alphabet = 'CDEFHKNPRSTUVWXY46379'

        maxlen = len(alphabet)
        code = ''
        for byte in os.urandom(8):
            pos = ord(byte) % maxlen
            code += alphabet[pos:pos+1]
        self.edit_access_code = code


class MembershipDues(db.Model):
    """Payments for membership fees. One for each year. A new set of
    payment entries will be created for each year. The structures parent
    will be the member class."""
    year = db.IntegerProperty(required=True)
    paid = db.BooleanProperty(default=False, required=True)


class ModelRange(db.Model):
    """A model range. In almost all cases there are more than one model in
    each range; this is the generic (like 'Spider', 'GTV', 'GT' and so on.)"""

    name = db.StringProperty()
    year_start = db.IntegerProperty()
    year_end = db.IntegerProperty()
    notes = db.TextProperty(required=False)

    def model_count(self):
        count = memcache.get(str(self.key()) + '_count')
        if count is not None:
            return count
        return 0


class CarModel(db.Model):
    """A concrete model, like 'GTV 2.0i Twin Spark' or 'GTV 3.2i V6'"""

    model_range = db.ReferenceProperty(ModelRange, collection_name='models')
    name = db.StringProperty()
    engine_code = db.StringProperty()
    typeno = db.StringProperty()
    image_url = db.LinkProperty()
    year_from = db.IntegerProperty()
    year_to = db.IntegerProperty()
    notes = db.TextProperty(required=False)

    def prettyprint(self):
        if self.year_to == 0:
            year_to = ''
        else:
            year_to = str(self.year_to)
        return '%s - (%d - %s)' % (self.name, self.year_from, year_to)

class Car(db.Model):
    """A member's car. The parent structure will be the member owning the
    car. """

    member = db.ReferenceProperty(Member, collection_name='cars')
    model = db.ReferenceProperty(CarModel, collection_name='cars')
    registration = db.StringProperty()
    bought_year = db.IntegerProperty(required=False)
    sold_year = db.IntegerProperty(required=False)
    year = db.IntegerProperty()
    notes = db.TextProperty()
    serial_no = db.StringProperty()
    delete_on_save = db.BooleanProperty(required=False, default=False)

class User(db.Model):
    """User of the system"""

    email = db.EmailProperty()


class ConfigTuple(db.Model):
    """Tuple for configuration parameters. The key names will be used to
    name the configuration option."""

    value = db.TextProperty()

