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

import cloudstorage
import datetime
from config import REPORT_BUCKET
from model import MembershipDues

YEAR_MAX = 25

class ReportGenerator(object):
    """ Abstract report class - implement to make new methods """
    from abc import ABCMeta
    from abc import abstractmethod
    __metaclass__ = ABCMeta
    """ Base class for reports """

    @abstractmethod
    def id(self):
        pass

    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def description(self):
        pass

    @abstractmethod
    def report_task(self):
        pass

    def get_filename(self, report_id):
        ts = datetime.datetime.now().strftime('%Y-%m-%dT%H%M%S')
        return '/%s/%s_%s.csv' % (REPORT_BUCKET, report_id, ts)

    def write_report(self, filename, lines, encoding='utf-8'):
        write_retry_params = cloudstorage.RetryParams(backoff_factor=1.1)
        gcs_file = cloudstorage.open(filename,
            'w',
            content_type='text/plain',
            retry_params=write_retry_params)

        for line in lines:
            gcs_file.write(line.encode(encoding))

        gcs_file.close()
