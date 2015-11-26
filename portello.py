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
"""Main application. Just routes for the different views."""

import admin.dump
import admin.restore
import admin.reindex
import ajax
import cronjobs
import views.backup
import views.carmodels
import views.countries
import views.load
import views.main
import views.members
import views.reports
import views.selfservice.editprofile
import views.selfservice.profile
import views.selfservice.signup
import views.settings
import views.statuses
import views.types
import views.caredit
import webapp2

application = webapp2.WSGIApplication([
    webapp2.Route('/backup', handler=views.backup.Backup),
    webapp2.Route('/restore', handler=admin.restore.DataRestore),
    webapp2.Route('/reindex', handler=admin.reindex.Reindex),

    webapp2.Route('/', handler=views.main.StartPage),
    webapp2.Route('/start', handler=views.main.StartPage),

    webapp2.Route('/members', handler=views.members.List),
    webapp2.Route('/members/<member_id>/edit', handler=views.members.Detail),
    webapp2.Route('/members/<member_id>/car/<car_id>/edit', \
        handler=views.members.CarDetail),
    webapp2.Route('/members/<member_id>/processed', \
        handler=views.members.MemberProcess),
    webapp2.Route('/ranges', handler=views.carmodels.RangeList),
    webapp2.Route('/ranges/<range_id>/edit', \
        handler=views.carmodels.RangeDetail),

    webapp2.Route('/ranges/<range_id>/<model_id>/edit',\
        handler=views.carmodels.ModelDetail),

    webapp2.Route('/countries', handler=views.countries.List),
    webapp2.Route('/countries/<country_key>/edit', \
        handler=views.countries.Detail),

    webapp2.Route('/statuses', handler=views.statuses.List),
    webapp2.Route('/statuses/<status_id>/edit', handler=views.statuses.Detail),

    webapp2.Route('/types', handler=views.types.List),
    webapp2.Route('/types/<type_id>/edit', handler=views.types.Detail),

    webapp2.Route('/settings', handler=views.settings.Detail),
    webapp2.Route('/settings/welcome', handler=views.settings.WelcomePreview),
    webapp2.Route('/settings/pdf', handler=views.settings.PdfPreview),

    webapp2.Route('/selfservice/signup', \
        handler=views.selfservice.signup.Signup),
    webapp2.Route('/selfservice/profile', \
        handler=views.selfservice.profile.Login),
    webapp2.Route('/selfservice/logout', \
        handler=views.selfservice.profile.Logout),
    webapp2.Route('/selfservice/profile/<member_no>/edit', \
        handler=views.selfservice.editprofile.Form),

    webapp2.Route('/cron/backup', handler=cronjobs.Backup),

    webapp2.Route('/ajax/ranges.json', handler=ajax.Range),
    webapp2.Route('/ajax/ranges/<range_id>/models.json', handler=ajax.Model),


    webapp2.Route('/reports', handler=views.reports.ReportList),
    webapp2.Route('/reports/generate', handler=views.reports.ReportGenerator),
    webapp2.Route('/reports/download/<filename>', handler=views.reports.ReportDownloader),
    webapp2.Route('/reports/view/<filename>', handler=views.reports.ReportViewer),

    webapp2.Route('/load', handler=views.load.Loader),
    webapp2.Route('/caredit', handler=views.caredit.CarEdit),

], debug=True)
