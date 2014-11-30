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
from google.appengine.api import memcache

from model import Country
from model import Status
from model import MemberType
from model import CarModel
from model import Member
from model import Car
from model import ModelRange

LIMIT_MEMBERS = 10000

class DataStoreCounter():
    def __init__(self):
        pass

    def __recount_items(self, selection, name):
        everything = selection.fetch(LIMIT_MEMBERS, keys_only=True)
        ret = len(everything)
        memcache.set(name, ret)
        return ret

    def __get_count(self, entity, name):
        ret = memcache.get(name)
        if not ret:
            ret = self.__recount_items(entity.all(), name)
        return ret

    def get_status_count(self):
        return self.__get_count(Status, 'status_count')

    def get_model_count(self):
        return self.__get_count(CarModel, 'model_count')

    def get_range_count(self):
        return self.__get_count(ModelRange, 'range_count')

    def get_country_count(self):
        return self.__get_count(Country, 'country_count')

    def get_type_count(self):
        return self.__get_count(MemberType, 'type_count')

    def get_member_count(self):
        return self.__get_count(Member, 'member_count')

    def get_car_count(self):
        return self.__get_count(Car, 'car_count')

    def __get_member_count(self, prefix, entity, collection):
        keyname = prefix + '_' + str(entity.key())
        ret = memcache.get(keyname)
        if not ret:
            member_list = collection.fetch(LIMIT_MEMBERS, keys_only=True)
            ret = len(member_list)
            memcache.set(keyname, ret)
        return ret

    def get_members_with_status(self, status):
        return self.__get_member_count('status', status, status.members)

    def get_members_with_type(self, membertype):
        return self.__get_member_count('type', membertype, membertype.members)

    def get_members_with_model(self, carmodel):
        return self.__get_member_count('model_', carmodel, carmodel.cars)

    def get_models_in_range(self, range):
        return self.__get_member_count('range_', range, range.models)

    def get_members_with_country(self, country):
        return self.__get_member_count('country_', country, country.members)
