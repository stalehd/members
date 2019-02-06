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
""" Common admin tasks. These aren't exposed in any way but can be invoked from
the (remote) console. Most of these things *will* break the app big time.
"""
import logging

from model import Member
from model import Status
from model import MemberType
from model import Country
from model import Car
from model import ConfigTuple
from model import ModelRange
from model import CarModel
from model import User
from model import MembershipDues
from google.appengine.api import search


class Admin(object):
    """Admin tasks and functions"""

    def __init__(self):
        pass

    def purge_data(self):
        """Purge data from store (scary shit)"""
        print 'Purging data'
        for entity in [Member, Status, MemberType, Country, Car, ConfigTuple,
                       ModelRange, CarModel, User, MembershipDues]:
            print 'Purging', entity.entity_type()
            entities = entity.all().fetch(1000)
            length = len(entities)
            while length > 0:
                print '...purging', length, 'entities'
                for ent in entities:
                    ent.delete()
                entities = entity.all().fetch(1000)
                length = len(entities)

    def purge_index(self):
        """Purge the index"""
        index = search.Index(name='members')
        # looping because get_range by default returns up to 100 documents at a time
        while True:
            # Get a list of documents populating only the doc_id field and extract the ids.
            document_ids = [
                document.doc_id for document in index.get_range(ids_only=True)]
            if not document_ids:
                break
            # Delete the documents for the given ids from the Index.
            index.delete(document_ids)

    def create_index(self):
        """Create a new index"""
        members = Member.all().fetch(20000)
        docs = []
        count = 0
        for member in members:
            try:
                docs.append(member.create_document())
                if len(docs) > 100:
                    index = search.Index(name='members')
                    index.put(docs)
                    docs = []
                count = count + 1
            except Exception as ex:
                logging.warning('Got exception ex %s', ex)
        if len(docs) > 0:
            index = search.Index(name='members')
            index.put(docs)
            docs = []
        logging.info('Reindexed %d members', count)

    def rebuild_index(self):
        """Rebuild the index by purge and create a new"""
        self.purge_index()
        self.create_index()

    def nonone(self):
        """ Mass update fields set to 'None'. Please don't ask. """
        for member in Member.all().fetch(10000):
            mod = False
            if member.email == 'None':
                member.email = None
                mod = True

            if member.phone == 'None':
                member.phone = None
                mod = True

            if member.phone_work == 'None':
                member.phone_work = None
                mod = True

            if member.phone_home == 'None':
                member.phone_home = None
                mod = True

            if member.address == 'None':
                member.address = None
                mod = True

            if mod:
                member.put()

    def help(self):
        """Show help"""
        print 'purge_data, purge_index, create_index, rebuild_index, index_verification'

    def index_verification(self):
        """Verify the index"""
        logging.info('Retrieving member list')
        member_list = Member.all().fetch(10000)
        logging.info('Found %d members', len(member_list))
        index = search.Index(name='members')
        for member in member_list:
            try:
                result = index.search(query=search.Query(
                    'number:' + member.number, options=search.QueryOptions(limit=10)))
                if not result.results:
                    logging.warning(
                        'Found no entry for member with number %s. Adding to index', member.number)
                    member.update_index()

            except Exception as ex:
                logging.warning('Got exception ex %s', ex)
        logging.info('Completed verification')
