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
from constants import *
from google.appengine.api import mail
from model import Country
from model import Member
from model import MemberType
from model import Status
import datetime
import dbutils
import jinja2
import webapp2
import cStringIO
from utils.giro import PdfGenerator
from config import Configuration
from jinja2 import Template
import constants

class Signup(webapp2.RequestHandler):
    """Member signup form"""

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('templates/selfservice/signup.html')
        countries = Country.all().order('order').fetch(100)
        self.response.write(template.render({
            'countries': countries,
            'incomplete': [],
            'complete': [],
            'values': { } }))

    def get_check_field(self, name, incomplete_list, required=True):
        value = self.request.get(name)
        if required and (not value or value.strip() == ''):
            print 'Missing',name
            incomplete_list.append(name)
        return (value, incomplete_list)

    def post(self):
        complete = []
        incomplete = []
        values = {}

        # Holy crap this is ugly. There has to be a better way.

        name = self.request.get('name')
        if not name or name.strip() == '':
            incomplete.append('name')
        else:
            values['name'] = name
            complete.append('name')


        address = self.request.get('address')
        if not address or address.strip() == '':
            incomplete.append('address')
        else:
            values['address'] = address
            complete.append('address')


        zipcode = self.request.get('zip')
        if (not zipcode or zipcode.strip() == '') or len(zipcode.strip()) < 4:
            incomplete.append('zip')
        else:
            values['zip'] = zipcode
            complete.append('zip')


        city = self.request.get('city')
        if not city or city.strip() == '':
            incomplete.append('city')
        else:
            values['city'] = city
            complete.append('city')

        if 'zip' in incomplete or 'city' in incomplete:
            incomplete.append('zipcity')


        country_key = self.request.get('country').strip()
        country = Country.get(country_key)

        countries = Country.all().order('order').fetch(100)

        if not country or not country_key or country_key.strip() == '':
            incomplete.append('country')
            # retrieve countries since we're going to need them
        else:
            values['country'] = country.name
            complete.append('country')

        email = self.request.get('email')
        if not email or email.strip() == '' or not mail.is_email_valid(email):
            incomplete.append('email')
        else:
            values['email'] = email
            complete.append('email')

        mobile = self.request.get('mobile')
        if mobile and mobile.strip() == '':
            mobile = None
        values['mobile'] = mobile

        home = self.request.get('home')
        if home and home.strip() == '':
            home = None
        values['home'] = home

        work = self.request.get('work')
        if work and work.strip() == '':
            work = None
        values['work'] = work

        member_type = self.request.get('type')
        if not member_type or member_type.strip() == '':
            member_type = '1'

        types = MemberType.all().fetch(100)

        mtype = None

        # TODO: Custom settings? Constants at least.
        if member_type == '1':
            mtype = next(t for t in types if t.name == DEFAULT_MEMBER_NAME)
        else:
            mtype = next(t for t in types if t.name == DEFAULT_SUPPORT_MEMBER_NAME)

        values['type'] = mtype.name
        comment = self.request.get('comment')
        complete.append('comment')
        values['comment'] = comment

        error_message = ''

        # Check if member exists;
        existing = Member.all().filter('email', email).fetch(1)

        if len(existing) > 0:
            incomplete.append('email')
            error_message = 'Det er allerede registrert noen i medlemsregisteret med denne epostadressen!'
            # TODO: Error message

        if len(incomplete) > 0:
            # missing field, redirect to signup page again
            template = JINJA_ENVIRONMENT.get_template('templates/selfservice/signup.html')
            return self.response.write(template.render({
                'countries': countries,
                'incomplete': incomplete,
                'complete': complete,
                'error_message': error_message,
                'values': values }))

        # invariant: fields are OK, create new member, send mail,
        # create payment history on member.
        template = JINJA_ENVIRONMENT.get_template('templates/selfservice/signup_receipt.html')
        data = {
            'values': values,
            'profile_url': PROFILE_URL
        }

        statuses = Status.all().fetch(100)

        # TODO: Handle existing members signing up again

        new_member = Member()

        new_member.name = name
        new_member.address = address
        new_member.zipcode = zipcode
        new_member.city = city
        new_member.notes = comment
        new_member.country = country
        new_member.membertype = mtype

        status = next(s for s in statuses if s.name == SIGNUP_STATUS_NAME)
        new_member.status = status

        new_member.number = dbutils.create_new_member_no()

        new_member.email = email
        new_member.member_since = datetime.date.today()
        if mobile:
            new_member.phone = mobile
        if work:
            new_member.phone_work = work
        if home:
            new_member.phone_home = home
        new_member.generate_access_code()
        new_member.member_since = datetime.date.today()
        new_member.member_type = mtype
        new_member.put()

        self.send_welcome_mail(new_member)
        self.send_notification_mails(new_member)

        # TODO: Invalidate counts for categories
        # Handle mutations on members gracefully

        return self.response.write(template.render(data))

    def send_welcome_mail(self, member):
        """Send welcom email with attachments"""
        config = Configuration()
        sender_address = config.get('WELCOME_MAIL_SENDER')
        subject = config.get('WELCOME_MAIL_SUBJECT')
        account_no = config.get('GIRO_ACCOUNT_NO')

        mail_template = Template(config.get('WELCOME_MAIL_TEXT'))

        data = {
            'member': member,
            'year': datetime.date.today().year,
            'accountno': account_no,
            'profile_url': constants.PROFILE_URL
        }
        body = mail_template.render(data)


        print 'sending mail with member no',member.number,'and access code',member.edit_access_code

        buf = cStringIO.StringIO()
        address = member.name + '\n' + member.address + '\n' + member.zipcode + ' ' + member.city
        if member.country.name != 'Norge':
            address = address + '\n' + member.country.name

        body_template = Template(config.get('GIRO_TEXT'))
        message_template = Template(config.get('GIRO_MESSAGE'))

        data = { 'member_no': member.number, 'account_no': account_no, 'access_code': member.edit_access_code, 'profile_url': constants.PROFILE_URL }

        pdf = PdfGenerator(member_address=address, club_address=config.get('GIRO_ADDRESS'), account_no=account_no,
            member_no=member.number, access_code=member.edit_access_code, profile_url=constants.PROFILE_URL,
            heading=config.get('GIRO_SUBJECT'), body=body_template.render(data), fee=member.member_type.fee, due_date='12.12.2012', payment_message=message_template.render(data))

        pdf.generate_pdf(buf)

        mail.send_mail(sender_address, member.email, subject, body, attachments=[('kontingent.pdf', buf.getvalue())])

    def send_notification_mails(self, member):
        """Send the notification mail"""
        config = Configuration()
        sender_address = config.get('WELCOME_MAIL_SENDER')
        subject = config.get('NOTIFICATION_MAIL_SUBJECT')
        recipients = config.get('NOTIFICATION_MAIL_RECIPIENTS')

        mail_template = JINJA_ENVIRONMENT.get_template('templates/emails/notification_signup.txt')
        data = {
            'member': member,
            'server_url': SERVER_URL
        }
        body = mail_template.render(data)

        mail.send_mail(sender_address, recipients, subject, body)
