# -*- coding: utf-8 -*-
"""Backup databas to a JSON file"""
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
import cloudstorage as gcs

from admin.dump import DataDump
from config import JINJA_ENVIRONMENT
from config import BACKUP_BUCKET


class Backup(webapp2.RequestHandler):
    """ Do a data dump of *everything*. Big data = big break. Small data =
    not so slow. """

    def get_files(self):
        """Get files from GCS"""
        files = []
        stats = gcs.listbucket('/%s/backups' % BACKUP_BUCKET, max_keys=100)
        for stat in stats:
            files.append(stat)
        return files

    def get(self):
        """Show backup page"""
        template = JINJA_ENVIRONMENT.get_template(
            'templates/backup/backup.html')
        self.response.write(template.render(
            {'message': '', 'files': self.get_files()}))

    def post(self):
        """Run backup"""
        template = JINJA_ENVIRONMENT.get_template(
            'templates/backup/backup.html')
        dump = DataDump()
        filename = dump.do_backup()

        message = 'Backing up to %s' % (filename)
        self.response.write(template.render(
            {'message': message, 'files': self.get_files()}))
