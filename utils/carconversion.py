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
import re
import datetime
from model import CarModel

class Model(CarModel):
    common_name = None

    def __init__(self, common_name, name, typeno, engine_code, year_from, year_to, notes):
        self.common_name = common_name
        super(name=name, typeno=typeno, engine_code=engine_code, year_from=year_from, year_to=year_to, notes=notes)

class MemberCar:
    """ A member's car """
    description = None
    registration = None
    year = None
    memberno = None

    def __init__(self, description=None, registration=None, year=None, memberno=None):
        self.description = description
        self.registration = registration
        self.year = year
        self.memberno = memberno

    def __repr__(self):
        return 'MemberCar(' + self.description + '/' + self.registration + '/' + str(self.year) + ')'

    def isvalid(self):
        if self.description:
            return True

#
# Conversion utilities and methods for car member import and matching.
# This is big and messy but so is the source data.

def read_models(file_name):
    # read the car models
    models = []
    with open(file_name, 'r') as fh:
        first = True
        for line in fh:
            # Skip first line
            if first:
                first = False
                continue

            fields = line.split(';')
            try:
                notes = ''
                if len(fields) > 6:
                    notes = fields[6]
                if len(fields) > 7:
                    print '**Whups:', line

                model = Model(
                    common_name=fields[0].strip(),
                    name=fields[1].strip(),
                    typeno=fields[2].strip(),
                    engine_code=fields[3].strip(),
                    year_from=int(fields[4]),
                    year_to=int(fields[5]),
                    notes=notes.strip())
                models.append(model)
            except Exception as ex:
                print ex, 'processing',line
    return models

def retrieve_cars_from_import(fields, cars):
    memberno = fields[0]
    car1 = MemberCar(memberno=memberno)
    car1.description = fields[1].strip()
    car1.registration = fields[2].strip()

    car2 = MemberCar(memberno=memberno)
    car2.description = fields[3].strip()
    car2.registration = fields[4].strip()

    car3 = MemberCar(memberno=memberno)
    car3.description = fields[5].strip()
    car3.registration = fields[6].strip()

    car4 = MemberCar(memberno=memberno)
    car4.description = fields[7].strip()
    car4.registration = fields[8].strip()

    car5 = MemberCar(memberno=memberno)
    car5.description = fields[9].strip()
    car5.registration = fields[10].strip()

    try:
        car1.year = int(fields[11])
    except ValueError:
        car1.year = 0
    try:
        car2.year = int(fields[12])
    except ValueError:
        car2.year = 0

    try:
        car3.year = int(fields[13])
    except ValueError:
        car3.year = 0

    try:
        car4.year = int(fields[14])
    except ValueError:
        car4.year = 0

    try:
        car5.year = int(fields[15])
    except ValueError:
        car5.year = 0

    if car1.isvalid() and car1.description != 'Bil1':
        cars.append(car1)
    if car2.isvalid() and car2.description != 'Bil2':
        cars.append(car2)
    if car3.isvalid()  and car3.description != 'Bil3':
        cars.append(car3)
    if car4.isvalid() and car4.description != 'Bil4':
        cars.append(car4)
    if car5.isvalid() and car5.description != 'Bil5':
        cars.append(car5)

def read_cars(file_name):
    cars = []
    # Read the member's models
    with open(file_name, 'r') as fh:
        first = True
        for line in fh:
            if first:
                first = False
                continue

            fields = line.strip().split(';')
            retrieve_cars_from_import(fields, cars)

    return cars

class CarRank:
    """ Ranking class """
    car = None
    model = None
    score = 0
    normalized_desc = None
    normalized_name = None
    normalized_desc_words = []
    normalized_name_words = []
    normalized_common_words = []

    def __init__(self, car, model, score):
        self.car = car
        self.model = model
        self.score = score
        self.normalized_desc = self.normalize_description(self.car.description)
        self.normalized_name = self.normalize_name(self.model.name)
        self.normalized_desc_words = self.normalized_desc.split(' ')
        self.normalized_name_words = re.split(r'[ /]', self.normalized_name)
        if 'common_name' in dir(self.model):
            self.normalized_common_words = re.split(r'[ /]', self.model.common_name.upper())
        else:
            self.normalized_common_words = re.split(r'[ /]', self.model.model_range.name.upper())

    def normalize_description(self, description):
        """
        Make a reasonable unified naming scheme from the
        provided description. This list contains a lot of
        data know-how if you are wondering :)
        """
        final_words = []
        name = description.upper();
        # Do string replacements first
        name = name.replace('156 CROSSWAGON', 'CROSSWAGON')
        name = name.replace('GTV 6', 'GTV6')
        name = name.replace('159', ' 159 ')
        name = name.replace('147,', '147 ')
        # Some write displacement as 'n,n'
        name = name.replace(',', '.')
        name = re.sub(r'(\d\.\d)([TSBI]*)',r'\1 \2', name)

        # ..then build a word list
        check_words = name.split(' ')
        for name in check_words:
            if name == '':
                continue

            if name == 'GUILETTA' or name == 'GUILIETTA' \
                    or name == 'GIULIETTE' or name == 'GULIETTA' \
                    or name == 'GUILIETTA':
                final_words.append('GIULIETTA')
            elif name == 'CROSSWAGEN':
                final_words.append('CROSSWAGON')
            elif name == 'JDTM':
                final_words.append('JTDM')
            elif name == 'QV':
                final_words.append('QV')
                final_words.append('QUADRIFOGLIO VERDE')
            elif name == 'QO':
                final_words.append('QO')
                final_words.append('QUADRIFOGLIO ORO')
            elif name == 'SPORTSWAGON' or name == 'SPORTWAGEN':
                final_words.append('SPORTWAGON')
            elif name == '5M':
                final_words.append('5 MARCHE')
            elif name == 'SW':
                final_words.append('SPORTWAGON')
            elif name == 'TS':
                final_words.append('TWIN SPARK')
            elif name == 'GTJ':
                # GTJ is commonly known as GT Junior
                final_words.append('GT')
                final_words.append('JUNIOR')
            elif name == 'JR' or name == 'JR.':
                final_words.append('JUNIOR')
            elif name == 'G.T.':
                final_words.append('GT')
            elif name == '150HK':
                final_words.append('16V')
            elif name == 'EVO':
                final_words.append('EVOLUZIONE')
            elif name == 'TB':
                final_words.append('TURBO')
            else:
                final_words.append(name)
        return ' '.join(final_words)

    def normalize_name(self, full_name):
        name = full_name.upper()
        # Models have sometimes added an 'i' to the engine size. Remove it (like 2.0i)
        name = re.sub(r'(\d\.\d)[I]*',r'\1', name)
        return name

    def common_name_in_description(self):
        if 'common_name' in dir(self.model):
            return (self.normalized_desc.find(self.model.common_name.upper()) >= 0)
        return (self.normalized_desc.find(self.model.model_range.name.upper()) >= 0)

    def matching_words_in_name(self):
        count = 0
        for word in self.normalized_name_words:
            if word.strip() == '':
                continue
            if word in self.normalized_desc_words:
                count += 1
        return count

    def matching_words_in_common_name(self):
        count = 0
        for word in self.normalized_common_words:
            if word.strip() == '':
                continue
            if word in self.normalized_desc_words:
                count += 1
        return count

    def is_important_word(self, word):
        # Litre specification is important
        if re.match('\d[\.,]\d', word):
            return True
        if re.match('\d\d\d\d', word):
            return True
        return False

    def add_score_for_important_words(self):
        for word in self.normalized_desc_words:
            if word.strip() == '':
                continue
            if self.is_important_word(word):
                if word in self.normalized_name_words:
                    self.score += 1
                if word in self.normalized_common_words:
                    self.score += 1

    def add_score_for_year_match(self):
        if self.car.year > 0:
            # Since we are being lenient on the production years above, assign
            # additional score to the precise yeear
            if self.model.year_from <= self.car.year and self.model.year_to >= self.car.year:
                 self.score += 1

    def add_score_for_model_age(self):
        # only do this for cars without a year specified
        if self.car.year == 0:
            self.score += self.model.year_to - 1910

    def add_score_for_partial_word_match_name(self):
        for word in self.normalized_desc_words:
            if word.strip() == '':
                continue
            if self.normalized_name.find(word) >= 0:
                self.score += 1

    def add_score_for_percent_name_match(self):
        count = self.matching_words_in_name()
        total = len(self.normalized_name_words)
        self.score += 100.0 * count / total

    def is_questionable_match(self):
        return (self.matching_words_in_common_name() == 0)

    @classmethod
    def match_car(self, models, car):
        description = car.description
        year = car.year
        selection = models
        if year != 0:
            # Limit to models matching the year +/- 2 years
            selection = []
            for model in models:
                if (model.year_from - 2) <= year and (model.year_to + 2) >= year:
                    selection.append(model)

        scoring = []
        for model in selection:
            rank = CarRank(car, model, 0)

            # If the common name contains
            if rank.common_name_in_description():
                rank.score += 2

            matching_name_count = rank.matching_words_in_name()
            rank.score += matching_name_count

            matching_common_count = rank.matching_words_in_common_name()
            rank.score += matching_common_count * 2

            rank.add_score_for_year_match()
            rank.add_score_for_important_words()

            if rank.score > 2:
                scoring.append(rank)

        # Sort scores and find the winner(s)
        result = CarRank.make_top_list(scoring)

        # if there are one or more tied cars; score on partial match and age of model
        if len(result) > 1:
            for rank in result:
                rank.add_score_for_model_age()
                rank.add_score_for_partial_word_match_name()
            result = CarRank.make_top_list(result)

        # This is the last straw -- third pass uses percentage of
        # words matched
        if len(result) > 1:
            for rank in result:
                rank.add_score_for_percent_name_match()
            result = CarRank.make_top_list(result)

        return result

    @classmethod
    def make_top_list(self, scoring):
        """ return top scorers """
        top_list = sorted(scoring, key=lambda x: -x.score)
        result = []
        if len(top_list) > 0:
            toprank = top_list[0]
            for rank in top_list:
                if rank.score == toprank.score:
                    result.append(rank)
        return result

    @classmethod
    def do_matching(self, models, cars, create_method):
        one = 0
        multiple = 0
        none = 0
        for car in cars:
            results = CarRank.match_car(models, car)
            undecided = True
            note = ''
            model_name = 'Annet'
            model_generic = 'Ukjent'

            if len(results) == 0:
                # Couldn't decide what model this is
                note = u'Kunne ikke finne en passende modell for denne bilen. '
                note += u'Bilen er beskrevet som "' + car.description + u'" og årstallet '
                if car.year == 0:
                    note += u'er ikke oppgitt'
                else:
                    note += u'er satt til ' + str(car.year) + '.'

                none += 1

            if len(results) == 1:
                # Found something that (might) fit
                undecided = False
                one += 1
                note = u'Modellen er satt automatisk ved hjelp av beskrivelsen som er gitt. Beskrivelsen var '
                note += u'"' + car.description + u'" men det kan forekomme feil, spesielt på motorstørrelse og versjon.'
                if 'common_name' in dir(results[0].model):
                    model_generic = results[0].model.common_name
                else:
                    model_generic = results[0].model.model_range.name
                model_name = results[0].model.name

            if len(results) > 1:
                # found more than one match
                undecided = True
                multiple += 1
                model_name = 'Annen Alfa Romeo'
                model_generic = 'Alfa Romeo'
                note = u'Den eksakte modellen for denne bilen kan ikke bestemmes automatisk. Følgende alternativer kan stemme med '
                note += u'beskrivelsen "' + car.description + '":\n'
                for rank in results:
                    note +=  ' * ' + rank.model.prettyprint() + '\n'

            bad_match = 0
            for rank in results:
                if rank.is_questionable_match():
                    bad_match += 1

            if bad_match > 0 and bad_match == len(results):
                # Flag as unmatched
                note = u'Beskrivelsen for denne bilen var "' + car.description + u'" men det var umulig å bestemme modellen '
                note += u'ut i fra beskrivelsen. Dette kan skyldes at årsmodellen er feil eller at beskrivelsen '
                note += u'ikke var detaljert nok. Følgende modell(er) kan være denne bilen:\n'
                for rank in results:
                    note += ' * ' + rank.model.prettyprint() + '\n'
                model_name = 'Annen Alfa Romeo'
                model_generic = 'Alfa Romeo'

            create_method(car, model_generic, model_name, note)

        return 'Results: %d matched, %d multiple matches, %d with no match' % (one, multiple, none)
