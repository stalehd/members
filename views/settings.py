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
import jinja2
from config import JINJA_ENVIRONMENT
import utils.auth
from config import Configuration
from model import Country
from model import Member
from model import MemberType
from jinja2 import Template
import constants
from utils.giro import PdfGenerator

class Detail(utils.auth.AuthHandler):
    """Handle configuration settings"""

    def get(self):
        """get; show page with config values"""

        template = JINJA_ENVIRONMENT.get_template('templates/settings/detail.html')

        data = { 'config': Configuration() }
        self.response.write(template.render(data))

    def post(self):
        """post; Save the config and show the page again"""

        config = Configuration()
        config.set('WELCOME_MAIL_SENDER', self.request.get('welcome_sender'))
        config.set('WELCOME_MAIL_SUBJECT', self.request.get('welcome_subject'))
        config.set('NOTIFICATION_MAIL_RECIPIENTS', self.request.get('notification_recipients'))
        config.set('NOTIFICATION_MAIL_SUBJECT', self.request.get('notification_subject'))
        config.set('GIRO_ACCOUNT_NO', self.request.get('account_no'))
        config.set('GIRO_SUBJECT', self.request.get('heading'))
        config.set('GIRO_TEXT', self.request.get('body'))
        config.set('GIRO_ADDRESS', self.request.get('address'))
        config.set('WELCOME_MAIL_TEXT', self.request.get('welcome_body'))
        config.set('GIRO_MESSAGE', self.request.get('giro_message'))
        template = JINJA_ENVIRONMENT.get_template('templates/settings/detail.html')

        data = { 'config': config }
        self.response.write(template.render(data))

class WelcomePreview(utils.auth.AuthHandler):
    """Show preview of email"""
    def get(self):
        config = Configuration()
        ruler = """
--------------------------------------------------------------------------------
0________1_________2_________3_________4_________5_________6_________7_________8
1        0         0         0         0         0         0         0         0
--------------------------------------------------------------------------------
"""
        template = Template(config.get('WELCOME_MAIL_TEXT'))

        member = Member()
        member.name = 'Ola Normann'
        member.address = 'Norskeveien 1'
        member.zipcode = '9876'
        member.city = 'Olabyen'
        member.country = Country().all().order('order').fetch(1)[0]
        member.email = 'ola.nordmann@example.com'
        member.phone = '916 75 105'
        member.phone_home = '939 90 115'
        member.phone_work = '101 33 116'
        member.number = '9669'
        member.access_code = 'BBQWTF'
        member.member_type = MemberType.all().order('order').fetch(1)[0]
        sample_data =  {
            'year': 2014,
            'fee': 400,
            'account_no': config.get('GIRO_ACCOUNT_NO'),
            'member': member,
            'profile_url': constants.PROFILE_URL
            }
        sample_text = template.render(sample_data)
        # Merge template before submitting text
        data = {'text': ruler + sample_text + ruler }

        template = JINJA_ENVIRONMENT.get_template('templates/settings/email_preview.html')
        self.response.write(template.render(data))

class PdfPreview(utils.auth.AuthHandler):
    """Show PDF preview"""
    def get(self):
        self.response.headers['Content-Type'] = 'application/pdf'

        config = Configuration()

        address = 'Ola Nordmann\nNorskeveien 1\n9876 Olabyen'
        member_no = '9876'
        access_code = 'BBQLOL'
        fee = 400
        profile_url = constants.PROFILE_URL
        account_no = config.get('GIRO_ACCOUNT_NO')


        body_template = Template(config.get('GIRO_TEXT'))
        message_template = Template(config.get('GIRO_MESSAGE'))

        data = { 'member_no': member_no, 'account_no': account_no, 'access_code': access_code, 'profile_url': profile_url }

        pdf = PdfGenerator(member_address=address, club_address=config.get('GIRO_ADDRESS'), account_no=account_no,
            member_no=member_no, access_code=access_code, profile_url=profile_url,
            heading=config.get('GIRO_SUBJECT'), body=body_template.render(data), fee=fee, due_date='12.12.2012', payment_message=message_template.render(data))

        pdf.generate_pdf(self.response.out)

