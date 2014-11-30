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
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm, inch
from reportlab.lib.colors import yellow, white
from google.appengine.api import images
import os.path

class PdfGenerator:
    """PDF Generator class.

        Shamelessly picked parts of this from https://code.google.com/p/finfaktura
        but modified to fit our needs. The invoices are a veritable minefield of
        standards, specs and rules so it is no wonder that most implementations
        just dump something that looks like a fair imitation.

        I'm no different. This won't pass mustard with the proper authorities and
        bank-approved OCR machines but I'm satisfied with this. A very small minority
        (if any) will print this and perform transactions. Most will enter the information
        through their online bank and be happy with it.
    """

    FONT = 'Times-Roman'
    BOLDFONT = 'Times-Bold'

    def __init__(self, member_address, club_address, account_no, member_no, access_code, profile_url, heading, body, fee, due_date, payment_message):
        self.member_address = member_address
        self.club_address = club_address
        self.account_no = account_no
        self.member_no = member_no
        self.access_code = access_code
        self.profile_url = profile_url
        self.heading = heading
        self.body = body
        self.due_date = due_date
        self.fee = fee
        self.payment_message = payment_message

    def draw_address_heading(self, canvas, address):
        """Draw member's address at the top of the page."""

        textobject = canvas.beginText()
        textobject.setTextOrigin(2.0*cm, 24.5*cm)
        textobject.setFont(self.FONT, 12)
        for line in address.split('\n'):
            textobject.textLine(line)
        canvas.drawText(textobject)

    def draw_page_text(self, canvas, heading, body):
        """Draw main text on page"""

        textobject = canvas.beginText()
        textobject.setTextOrigin(2.0*cm, 21.0*cm)

        textobject.setFont(self.BOLDFONT, 14)
        heading = heading.replace('\r', '')
        for line in heading.split('\n'):
            textobject.textLine(line)

        textobject.textLine('')

        textobject.setFont(self.FONT, 12)
        body = body.replace('\r','')
        for line in body.split('\n'):
            textobject.textLine(line)

        canvas.drawText(textobject)

    def draw_payers_address(self, canvas, address):
        """Draw member's address at the bottom"""

        textobject = canvas.beginText()
        textobject.setTextOrigin(1.5*cm, 5.8*cm)
        textobject.setFont(self.FONT, 10)
        address = address.replace('\r','')
        for line in address.split('\n'):
            textobject.textLine(line)
        canvas.drawText(textobject)

    def draw_recipient_address(self, canvas, address):
        """Draw the club's address"""

        textobject = canvas.beginText()
        textobject.setTextOrigin(11.5*cm, 5.8*cm)
        textobject.setFont(self.FONT, 10)
        address=address.replace('\r', '')
        for line in address.split('\n'):
            textobject.textLine(line)
        canvas.drawText(textobject)

    def draw_payment_info(self, canvas, info):
        """Add payment information. This will probably be copied and pasted by the member"""

        textobject = canvas.beginText()
        textobject.setTextOrigin(1.5*cm, 9.0*cm)
        textobject.setFont(self.BOLDFONT, 10)
        textobject.textLine(info)
        canvas.drawText(textobject)

    def draw_account_no(self, canvas, account):
        """Draw the account no"""

        textobject = canvas.beginText()
        textobject.setTextOrigin(133*mm, 2.13*cm)
        textobject.setFont(self.BOLDFONT, 10)
        textobject.textLine(account)
        canvas.drawText(textobject)

    def draw_amount(self, canvas, amount):
        """Draw the amount to be paid"""

        textobject = canvas.beginText()
        textobject.setTextOrigin(92*mm, 2.13*cm)
        textobject.setFont(self.BOLDFONT, 10)
        textobject.textLine(amount)
        textobject.setTextOrigin(107*mm, 2.13*cm)
        textobject.textLine('00')
        canvas.drawText(textobject)

    def draw_due_date(self, canvas, due_date):
        """Draw due date. This will probably be ignored by quite a few but..."""

        textobject = canvas.beginText()
        textobject.setTextOrigin(170*mm, 95*mm)
        textobject.setFont(self.FONT, 10)
        textobject.textLine(due_date)
        canvas.drawText(textobject)

    def draw_club_logo(self, canvas):
        """Draw the club logo. Not a lot of code but nice to do everything in separate methods"""

        canvas.drawInlineImage(os.path.abspath('./club-logo.jpg'), 9.5*cm, 25.5*cm, 3*cm, 3*cm)

    def generate_pdf(self, destination):
        c = canvas.Canvas(destination, pagesize=A4)
        self.drawBackground(c)
        self.draw_address_heading(c, self.member_address)


        self.draw_page_text(c, self.heading, self.body)
        self.draw_payers_address(c, self.member_address)
        self.draw_recipient_address(c, self.club_address)

        self.draw_payment_info(c, self.payment_message)
        self.draw_account_no(c, self.account_no)
        self.draw_amount(c, str(self.fee))
        self.draw_due_date(c, self.due_date)
        self.draw_club_logo(c)
        c.showPage()
        c.save()



    def markField(self, canvas, punktX, punktY, deltaX, deltaY, tekst=None):
        """En fullstendig giro har hjørneklammer rundt hvert tekstfelt.
           PunktX og punktY setter øverste venstre hjørne i "boksen".
           deltaX og deltaY angir relativ avstand til nederste høyre hjørne."""

        # Oppe i venstre  hjørne P(12,65)
        canvas.setLineWidth(0.2*mm)
        canvas.lines([(punktX, punktY, punktX+2*mm, punktY), (punktX, punktY-2*mm, punktX, punktY)])
        # oppe i høyre hjørne P(98,65)
        canvas.lines([(punktX+deltaX-2*mm, punktY, punktX+deltaX, punktY), (punktX+deltaX, punktY-2*mm, punktX+deltaX, punktY)])

        # Nede i venstre hjørne P(12,43)
        canvas.lines([(punktX, punktY+deltaY, punktX+2*mm, punktY+deltaY), (punktX, punktY+deltaY, punktX, punktY+deltaY+2*mm)])
        # Nede i høyre hjørne P(98,43) # deltaX = 86, deltaY = -22
        canvas.lines([(punktX+deltaX-2*mm, punktY+deltaY, punktX+deltaX, punktY+deltaY), (punktX+deltaX, punktY+deltaY, punktX+deltaX, punktY+deltaY+2*mm)])

        if isinstance(tekst, basestring):
            # skriv hjelpetekst til boksen
            canvas.setFont("Helvetica-Bold", 6)
            canvas.drawString(punktX+3*mm,punktY+1*mm, tekst)

    def drawBackground(self, canvas):
        underkant = 5.0/6.0 * inch
        # a4 format spec:
        # http://www.cl.cam.ac.uk/~mgk25/iso-paper.html
        # 210 x 297
        # faktura spek:
        # Norsk Standard Skjema F60-1
        # url: http://code.google.com/p/finfaktura/issues/detail?id=38
        canvas.saveState()
        canvas.setFillColor(yellow)

        # Yellow bits; skipping the receipt area.
        # Lag de gule feltene
        #canvas.rect(0*mm, 101*mm, 210*mm, 21*mm, stroke=0, fill=1)
        canvas.rect(0*mm, 33*mm, 210*mm, 9*mm, stroke=0, fill=1)
        canvas.rect(0*mm, 14*mm, 210*mm, 2*mm, stroke=0, fill=1)

        canvas.setFillColor(white)
        # Legg de hvite feltene oppå for "gjennomsiktighet"
        canvas.rect(80*mm, 103*mm, 36*mm, 9*mm, stroke=0, fill=1) # beløp
        canvas.rect(126*mm, 103*mm, 40*mm, 9*mm, stroke=0, fill=1) # betalerens kontonummer
        canvas.rect(170*mm, 103*mm, 31*mm, 9*mm, stroke=0, fill=1) # blankettnummer
        canvas.restoreState()

        # skillelinjer for KID
        canvas.lines([(9*mm, 16*mm, 9*mm, 30*mm), (80*mm, 16*mm, 80*mm, 30*mm)])
        # blankettnummer
        #canvas.setFont("Courier", 10)
        #blankettnr = "xxxxxxx"
        #canvas.drawString(173*mm, 105*mm, blankettnr)
        #canvas.drawString(173*mm, underkant, blankettnr)

        # Lag klammer for kontrollsiffer til sum.
        canvas.drawString(115*mm, underkant, "<")
        canvas.drawString(125*mm, underkant, ">")
        # Lag tekst som beskriver feltene.
        canvas.setFont("Helvetica-Bold", 6)
        canvas.drawString(15*mm, 98*mm, "Betalingsinformasjon")
        canvas.drawString(10*mm,30*mm,"Kundeidentifikasjon (KID)")
        canvas.drawString(82*mm,30*mm,"Kroner")
        canvas.drawString(107*mm,30*mm,"Øre")
        canvas.drawString(133*mm,30*mm,"Til konto")
        canvas.drawString(172*mm,30*mm,"Blankettnummer")
        canvas.drawString(150*mm,98*mm,"Betalings-")
        canvas.drawString(150*mm,95*mm,"frist")

        # Lag hjørneklammer rundt alle tekstfelt
        self.markField(canvas, 12*mm,64*mm, 86*mm, -21*mm, "Betalt av")
        self.markField(canvas, 110*mm,64*mm, 86*mm, -21*mm, "Betalt til")
        self.markField(canvas, 110*mm,89*mm, 86*mm, -19*mm, "Underskrift ved girering")
        self.markField(canvas, 166*mm,99*mm, 30*mm, -6*mm)    # Betalingsfrist.

        # Add the all-important "GIRO" text. It seems to do wonders for the recognition.
        canvas.setFont('Helvetica-Bold', 14)
        canvas.drawString(110*mm, 98*mm, "GIRO")

