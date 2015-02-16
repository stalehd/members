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
from config import REPORT_BUCKET
from google.appengine.ext import deferred
import datetime
import utils.auth
import webapp2
import cloudstorage
import lists.unpaid
import lists.magazine
import lists.newmembers
import lists.newsletter
import lists.tuttimondo

# This is the array of available reports
report_generators = [
    lists.unpaid.UnpaidMembershipDues(),
    lists.magazine.MagazineRecipients(),
    lists.newmembers.NewMemberList(),
    lists.newsletter.NewsletterRecipients(),
    lists.tuttimondo.TuttiMondo(),
]


class ReportList(utils.auth.AuthHandler):
    """ Display list of available reports and a list of report generators """

    def get(self):
        # List the files in the cloudstore reports dir.
        files = list()
        bucket_name = '/' + REPORT_BUCKET

        for stat in cloudstorage.listbucket(bucket_name, max_keys=100):
            date_str = datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%d.%m.%Y kl %H:%M')
            report = self.get_report_from_file(stat.filename)
            files.append({ 'filename': stat.filename[len('/' + REPORT_BUCKET + '/'):], 'date': date_str, 'report': report, 'source': stat })

        # get reports in progress

        template = JINJA_ENVIRONMENT.get_template('templates/reports/list.html')
        data = { 'files': files, 'generators': report_generators }
        self.response.write(template.render(data))

    def get_report_from_file(self, filename):
        # strip bucket name
        for report in report_generators:
            # report starts with
            if filename.startswith('/%s/%s_' % (REPORT_BUCKET, report.id())):
                return report
        return None


class ReportGenerator(utils.auth.AuthHandler):
    """ POST class that enqueues reports and redirects back to the report list """
    def post(self):
        report_id = self.request.get('report_id')
        for report in report_generators:
            if report_id == report.id():
                ts = datetime.datetime.now().strftime('%Y-%m-%dT%H%M%S')
                task_name = 'Report_%s_%s' % (report_id, ts)
                deferred.defer(report.report_task, _name=task_name)
                break
        self.redirect('/reports')


class ReportDownloader(utils.auth.AuthHandler):
    """ Download class for files stored in GCS """
    def get(self, filename):
        bucket_file = '/%s/%s' % (REPORT_BUCKET, filename)
        write_retry_params = cloudstorage.RetryParams(backoff_factor=1.1)
        file_contents = ''

        with cloudstorage.open(bucket_file, 'r', retry_params=write_retry_params) as fh:
            for line in fh:
                file_contents += line

        self.response.headers.add('content-disposition', 'attachment; filename=portello_' + filename)
        self.response.headers.add('content-type', 'text/csv; charset=utf-8')
        self.response.write(file_contents)


class ReportViewer(utils.auth.AuthHandler):
    def get(self, filename):
        bucket_file = '/%s/%s' % (REPORT_BUCKET, filename)
        write_retry_params = cloudstorage.RetryParams(backoff_factor=1.1)
        file_contents = ''

        with cloudstorage.open(bucket_file, 'r', retry_params=write_retry_params) as fh:
            for line in fh:
                file_contents += line

        self.response.headers.add('content-type', 'text/csv; charset=utf-8')
        self.response.headers
        self.response.write(file_contents)
