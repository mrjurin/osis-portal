##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from admission import models as mdl
from django.shortcuts import render, get_object_or_404
from reference import models as mdl_reference

from datetime import datetime
from admission.views.common import home
from functools import cmp_to_key
import locale
from django.utils.translation import ugettext_lazy as _
import string


def save(request):
    next_step = False
    previous_step = False
    save_step = False
    validation_messages = {}
    if request.POST:
        if 'bt_next_step_up' in request.POST or 'bt_next_step_down' in request.POST:
            next_step = True
        else:
            if 'bt_previous_step_up' in request.POST or 'bt_previous_step_down' in request.POST:
                previous_step = True
            else:
                if 'bt_save_up' in request.POST or 'bt_save_down' in request.POST:
                    save_step = True

    if previous_step:
        return home(request)

    message_success = None
    # Get the data in bd for dropdown list
    local_universities_french = mdl_reference.education_institution\
        .find_by_institution_type_national_community('UNIVERSITY', 'FRENCH', False)

    local_universities_dutch = mdl_reference.education_institution\
        .find_by_institution_type_national_community('UNIVERSITY', 'DUTCH', False)
    universities_cities = []
    universities = []
    national_high_non_university_institutions = mdl_reference.education_institution.find_by_institution_type_iso_code('HIGHER_NON_UNIVERSITY', 'BE', False)
    cities_national_high_non_university_institutions = mdl_reference.education_institution.find_by_isocode_type('BE', 'HIGHER_NON_UNIVERSITY', False)

    foreign_high_institution_countries = mdl_reference.education_institution.find_countries_by_type_excluding_country('HIGHER_NON_UNIVERSITY', False, "BE")
    foreign_high_institution_cities = mdl_reference.education_institution\
        .find_by_not_isocode_type('BE', 'HIGHER_NON_UNIVERSITY', False)
    foreign_high_institutions = mdl_reference.education_institution.find_by_institution_type_not_isocode('HIGHER_NON_UNIVERSITY', 'BE', False)

    if save_step or next_step:
        is_valid, validation_messages, curricula, universities_cities, universities, foreign_high_institution_cities, foreign_high_institutions = validate_fields_form(request)
        if is_valid:
            message_success = _('msg_info_saved')
            for curriculum in curricula:
                curriculum.save()
        else:
            return render(request, "curriculum.html", {"curricula":                 curricula,
                                           "local_universities_french": local_universities_french,
                                           "local_universities_dutch":  local_universities_dutch,
                                           "domains":                   mdl.domain.find_all_domains(),
                                           "subdomains":                mdl.domain.find_all_subdomains(),
                                           "grade_types":               mdl.grade_type.find_all(),
                                           "validation_messages":       validation_messages,
                                           "message_success":           message_success,
                                           "universities_cities":       universities_cities,
                                           "universities":              universities,
                                           "cities_national_high_non_university_institutions":cities_national_high_non_university_institutions,
                                           "national_high_non_university_institutions": national_high_non_university_institutions,
                                           "languages":                 mdl_reference.language.find_languages(),
                                           "foreign_high_institution_countries": foreign_high_institution_countries,
                                           "foreign_high_institution_cities": foreign_high_institution_cities,
                                           "foreign_high_institutions":foreign_high_institutions})

    #Get the data in bd
    a_person = mdl.person.find_by_user(request.user)
    first_academic_year_for_cv = None
    curricula = []
    message = None
    # find existing cv
    secondary_education = mdl.secondary_education.find_by_person(a_person)
    if secondary_education:
        if secondary_education.academic_year is None:
            message ="Vous ne pouvez pas encoder d'études supérieures sans avoir réussit vos études secondaires"
        else:
            first_academic_year_for_cv = secondary_education.academic_year.year + 1
    current_academic_year = mdl.academic_year.current_academic_year().year
    year = first_academic_year_for_cv

    while year < current_academic_year:
        academic_year = mdl.academic_year.find_by_year(year)
        curriculum = mdl.curriculum.find_by_academic_year(academic_year)
        if curriculum is None:
            # add cv empty cv's for the year if it's needed
            curriculum = mdl.curriculum.Curriculum()
            curriculum.person = a_person
            curriculum.academic_year = academic_year
        curricula.append(curriculum)
        year = year + 1

    return render(request, "curriculum.html", {"curricula":                 curricula,
                                               "local_universities_french": local_universities_french,
                                               "local_universities_dutch":  local_universities_dutch,
                                               "domains":                   mdl.domain.find_all_domains(),
                                               "subdomains":                mdl.domain.find_all_subdomains(),
                                               "grade_types":               mdl.grade_type.find_all(),
                                               "universities_countries":    mdl_reference.education_institution.find_countries(),
                                               "validation_messages":       validation_messages,
                                               "message_success":           message_success,
                                               "universities_cities":       universities_cities,
                                               "universities":              universities,
                                               "cities_national_high_non_university_institutions":cities_national_high_non_university_institutions,
                                               "national_high_non_university_institutions": national_high_non_university_institutions,
                                               "languages":                 mdl_reference.language.find_languages(),
                                               "foreign_high_institution_countries": foreign_high_institution_countries,
                                               "foreign_high_institution_cities": foreign_high_institution_cities,
                                               "foreign_high_institutions": foreign_high_institutions})


def update(request):
    curricula = []
    message = None
    a_person = mdl.person.find_by_user(request.user)
    secondary_education = mdl.secondary_education.find_by_person(a_person)
    current_academic_year = mdl.academic_year.current_academic_year().year
    admission = is_admission(a_person, secondary_education)
    year_secondary = None
    year = current_academic_year - 5
    if secondary_education and secondary_education.secondary_education_diploma is True:
        year_secondary= secondary_education.academic_year.year

    if admission:
        if secondary_education and secondary_education.secondary_education_diploma is True:
            year = secondary_education.academic_year.year + 1

    if year_secondary and year < year_secondary:
        year = year_secondary + 1

    while year < current_academic_year:
        academic_year = mdl.academic_year.find_by_year(year)
        if academic_year:
            # find existing cv
            curriculum = mdl.curriculum.find_by_academic_year(academic_year)
            if curriculum is None:
                # add cv empty cv's for the year if it's needed
                curriculum = mdl.curriculum.Curriculum()
                curriculum.person = a_person
                curriculum.academic_year = academic_year
            curricula.append(curriculum)
        year = year + 1
    local_universities_french = mdl_reference.education_institution\
        .find_by_institution_type_national_community('UNIVERSITY', 'FRENCH', False)

    local_universities_dutch = mdl_reference.education_institution\
        .find_by_institution_type_national_community('UNIVERSITY', 'DUTCH', False)
    foreign_high_institution_countries = mdl_reference.education_institution.find_countries_by_type_excluding_country('HIGHER_NON_UNIVERSITY', False, "BE")
    foreign_high_institution_cities = mdl_reference.education_institution.find_by_not_isocode_type("BE", "HIGHER_NON_UNIVERSITY", False)
    foreign_high_institutions = mdl_reference.education_institution.find_by_institution_type_not_isocode('HIGHER_NON_UNIVERSITY', 'BE', False )

    if message:
        return home(request)
    else:
        universities_cities, universities = populate_dropdown_list(curricula)
        foreign_high_institution_countries, foreign_high_institution_cities, foreign_high_institutions = populate_dropdown_foreign_high_list(curricula)
        national_high_non_university_institutions = mdl_reference.education_institution.find_by_institution_type_iso_code('HIGHER_NON_UNIVERSITY', 'BE', False )
        cities_national_high_non_university_institutions = mdl_reference.education_institution.find_by_isocode_type('BE', 'HIGHER_NON_UNIVERSITY', False )
        return render(request, "curriculum.html", {"curricula":                 curricula,
                                                   "local_universities_french": local_universities_french,
                                                   "local_universities_dutch":  local_universities_dutch,
                                                   "domains":                   mdl.domain.find_all_domains(),
                                                   "subdomains":                mdl.domain.find_all_subdomains(),
                                                   "grade_types":               mdl.grade_type.find_all(),
                                                   "universities_countries":    mdl_reference.education_institution.find_countries(),
                                                   "universities_cities":       universities_cities,
                                                   "universities":              universities,
                                                   "cities_national_high_non_university_institutions": cities_national_high_non_university_institutions,
                                                   "national_high_non_university_institutions": national_high_non_university_institutions,
                                                   "languages":                 mdl_reference.language.find_languages(),
                                                   "foreign_high_institution_countries": foreign_high_institution_countries,
                                                   "foreign_high_institution_cities": foreign_high_institution_cities,
                                                   "foreign_high_institutions": foreign_high_institutions})


def validate_fields_form(request):
    is_valid = True
    curricula = []
    universities_cities = []
    universities = []
    high_non_universities_cities = []
    high_non_universities_names = []
    validation_messages = {}
    a_person = mdl.person.find_by_user(request.user)
    names = [v for k, v in request.POST.items() if k.startswith('curriculum_year_')]
    names = sorted(names, key=cmp_to_key(locale.strcoll)) #to keep the order of the cv from the oldest to the more recent

    for curriculum_form in names:
        curriculum_year = curriculum_form.replace('curriculum_year_', '')
        academic_year = mdl.academic_year.find_by_year(curriculum_year)
        curriculum = mdl.curriculum.find_by_person_year(a_person, int(curriculum_year))

        if curriculum is None:
            curriculum = mdl.curriculum.Curriculum()
            curriculum.person = a_person
            curriculum.academic_year = academic_year
        #default
        curriculum.path_type = None
        curriculum.national_education = None
        curriculum.language = None
        curriculum.national_institution = None
        curriculum.domain = None
        curriculum.sub_domain = None
        curriculum.grade_type = None
        curriculum.result = None
        curriculum.credits_enrolled = None
        curriculum.credits_obtained = None
        curriculum.diploma = False
        curriculum.diploma_title = None
        curriculum.activity_type = None
        curriculum.activity = None
        curriculum.activity_place = None
        #
        if request.POST.get('path_type_%s' % curriculum_year) is None:
            validation_messages['path_type_%s' % curriculum_year] = _('mandatory_field')
            is_valid = False
        else:
            curriculum.path_type = request.POST.get('path_type_%s' % curriculum_year)
            if curriculum.path_type == 'LOCAL_UNIVERSITY' or curriculum.path_type == 'LOCAL_HIGH_EDUCATION':
                is_valid, validation_messages, curriculum = validate_belgian_fields_form(request,
                                                                                         curriculum,
                                                                                         curriculum_year,
                                                                                         validation_messages,
                                                                                         is_valid)
            else:
                if curriculum.path_type == 'FOREIGN_UNIVERSITY' or 'FOREIGN_HIGH_EDUCATION':
                    is_valid, validation_messages, curriculum, universities_cities, universities, \
                    high_non_universities_cities,high_non_universities_names = validate_foreign_university_fields_form(request,
                                                                                                        curriculum,
                                                                                                        curriculum_year,
                                                                                                        validation_messages,
                                                                                                        is_valid,
                                                                                                        universities_cities,
                                                                                                        universities,
                                                                                                        high_non_universities_cities,
                                                                                                        high_non_universities_names)

        curricula.append(curriculum)
    return is_valid, validation_messages, curricula, universities_cities, universities, high_non_universities_cities, high_non_universities_names


def is_admission(a_person, secondary_education):
    if a_person.nationality.european_union:
        if secondary_education and secondary_education.national is True:
            return False
    return True


def validate_belgian_fields_form(request, curriculum, curriculum_year, validation_messages, is_valid):

    if curriculum.path_type == "LOCAL_UNIVERSITY":
        if request.POST.get('national_education_%s' % curriculum_year) is None:
            validation_messages['national_education_%s' % curriculum_year] = _('mandatory_field')
            is_valid = False
        else:
            curriculum.national_education = request.POST.get('national_education_%s' % curriculum_year)
            if curriculum.national_education == 'FRENCH':
                curriculum.language = mdl_reference.language.find_by_code('fr')
                if request.POST.get('national_institution_french_%s' % curriculum_year) is None \
                        or request.POST.get('national_institution_french_%s' % curriculum_year) == '-':
                    validation_messages['national_institution_french_%s' % curriculum_year] = _('mandatory_field')
                    is_valid = False
                else:
                    national_institution = mdl_reference.education_institution\
                        .find_by_id(int(request.POST.get('national_institution_french_%s' % curriculum_year)))
                    curriculum.national_institution = national_institution
            else:
                if curriculum.national_education == 'DUTCH':
                    curriculum.language = mdl_reference.language.find_by_code('nl')
                    if request.POST.get('national_institution_dutch_%s' % curriculum_year) is None \
                            or request.POST.get('national_institution_dutch_%s' % curriculum_year) == '-':
                        validation_messages['national_institution_dutch_%s' % curriculum_year] = _('mandatory_field')
                        is_valid = False
                    else:
                        national_institution = mdl_reference.education_institution\
                            .find_by_id(int(request.POST.get('national_institution_dutch_%s' % curriculum_year)))
                        curriculum.national_institution = national_institution
        if request.POST.get('domain_%s' % curriculum_year) is None \
                or request.POST.get('domain_%s' % curriculum_year) == '-':
            validation_messages['domain_%s' % curriculum_year] = _('mandatory_field')
            is_valid = False
        else:
            domain = mdl.domain.find_by_id(int(request.POST.get('domain_%s' % curriculum_year)))
            curriculum.domain = domain
            if domain.sub_domains:
                if request.POST.get('subdomain_%s' % curriculum_year) is None \
                            or request.POST.get('subdomain_%s' % curriculum_year) == '-':
                    validation_messages['subdomain_%s' % curriculum_year] = _('mandatory_field')
                    is_valid = False
                else:
                    sub_domain = mdl.domain.find_by_id(int(request.POST.get('subdomain_%s' % curriculum_year)))
                    curriculum.sub_domain = sub_domain
        print(request.POST.get('corresponds_to_domain_%s' % curriculum_year))
        if request.POST.get('corresponds_to_domain_%s' % curriculum_year) == "false":
            print(request.POST.get('diploma_title_%s' % curriculum_year))
            if request.POST.get('diploma_title_%s' % curriculum_year) is None \
                    or len(request.POST.get('diploma_title_%s' % curriculum_year).strip()) == 0:
                validation_messages['diploma_title_%s' % curriculum_year] = _('mandatory_field')
                is_valid = False

        if request.POST.get('result_national_%s' % curriculum_year) is None \
                and ((curriculum.academic_year.year < 2014) or (curriculum.academic_year.year >= 2014 and curriculum.diploma)):
            validation_messages['result_national_%s' % curriculum_year] = _('mandatory_field')
            is_valid = False
        else:
            curriculum.result = request.POST.get('result_national_%s' % curriculum_year)

    if curriculum.path_type == "LOCAL_HIGH_EDUCATION":
        if request.POST.get('national_education_%s' % curriculum_year):
            curriculum.national_education = request.POST.get('national_education_%s' % curriculum_year)
        if request.POST.get('other_school_high_non_university_%s' % curriculum_year) \
                and request.POST.get('other_school_high_non_university_%s' % curriculum_year) == "on":
            if request.POST.get('other_high_non_university_name_%s' % curriculum_year) is None:
                validation_messages['high_non_university_name_%s' % curriculum_year] = _('msg_school_name')
                is_valid = False
            else:
                national_institution = mdl_reference.education_institution.EducationInstitution()
                national_institution.adhoc = True
                national_institution.name = request.POST.get('other_high_non_university_name_%s' % curriculum_year)
                national_institution.save()
                curriculum.national_institution = national_institution
        else:
            if request.POST.get('national_high_non_university_institution_%s' % curriculum_year) is None or request.POST.get('national_high_non_university_institution_%s' % curriculum_year) == "-":
                validation_messages['high_non_university_name_%s' % curriculum_year] = _('msg_school_name')
                is_valid = False
            else:
                national_institution = mdl_reference.education_institution\
                            .find_by_id(int(request.POST.get('national_high_non_university_institution_%s' % curriculum_year)))
                curriculum.national_institution = national_institution
        if request.POST.get('domain_non_university_%s' % curriculum_year) is None \
                or request.POST.get('domain_non_university_%s' % curriculum_year) == '-':
            validation_messages['domain_non_university_%s' % curriculum_year] = _('mandatory_field')
            is_valid = False
        else:
            domain = mdl.domain.find_by_id(int(request.POST.get('domain_non_university_%s' % curriculum_year)))
            curriculum.domain = domain
        if request.POST.get('grade_type_no_university_%s' % curriculum_year) is None \
                or request.POST.get('grade_type_no_university_%s' % curriculum_year) == '-':
            validation_messages['grade_type_no_university_%s' % curriculum_year] = _('mandatory_field')
            is_valid = False
        else:
            curriculum.grade_type_no_university = request.POST.get('grade_type_no_university_%s' % curriculum_year)

        if request.POST.get('study_systems_%s' % curriculum_year):
            curriculum.study_system = request.POST.get('study_systems_%s' % curriculum_year)
        else:
            curriculum.study_system = None

        if request.POST.get('result_national_%s' % curriculum_year) \
                and request.POST.get('result_national_%s' % curriculum_year) != "-":
            curriculum.result = request.POST.get('result_national_%s' % curriculum_year)
        else:
            curriculum.result = None
    # common fields for belgian university and no-university curriculum
    if request.POST.get('grade_type_%s' % curriculum_year) is None \
            or request.POST.get('grade_type_%s' % curriculum_year) == '-':
        validation_messages['grade_type_%s' % curriculum_year] = _('mandatory_field')
        is_valid = False
    else:
        grade_type = mdl.grade_type.find_by_id(int(request.POST.get('grade_type_%s' % curriculum_year)))
        curriculum.grade_type = grade_type

    if request.POST.get('diploma_title_%s' % curriculum_year):
        curriculum.diploma_title = request.POST.get('diploma_title_%s' % curriculum_year)

    if request.POST.get('diploma_%s' % curriculum_year) is None:
        validation_messages['diploma_%s' % curriculum_year] = _('mandatory_field')
        is_valid = False
    else:
        if request.POST.get('diploma_%s' % curriculum_year) == "true":
            curriculum.diploma = True

    if curriculum.academic_year.year >= 2014:
        if request.POST.get('credits_enrolled_%s' % curriculum_year) is None \
                or len(request.POST.get('credits_enrolled_%s' % curriculum_year)) == 0:
            validation_messages['credits_enrolled_%s' % curriculum_year] = _('mandatory_field')
            is_valid = False
            curriculum.credits_enrolled = None
    if request.POST.get('credits_enrolled_%s' % curriculum_year) \
            and len(request.POST.get('credits_enrolled_%s' % curriculum_year)) > 0:
            try:
                credits = float(request.POST.get('credits_enrolled_%s' % curriculum_year)\
                            .strip().replace(',', '.'))
                curriculum.credits_enrolled = credits
                if credits > 75:
                    validation_messages['credits_enrolled_%s' % curriculum_year] = _('credits_too_high')
                    is_valid = False
                else:
                    if credits < 0:
                        validation_messages['credits_enrolled_%s' % curriculum_year] = _('credits_negative')
                        is_valid = False
            except ValueError:
                validation_messages['credits_enrolled_%s' % curriculum_year] = _('numeric_field')
                is_valid = False

    if curriculum.academic_year.year >= 2014:
        if request.POST.get('credits_obtained_%s' % curriculum_year) is None \
                or len(request.POST.get('credits_obtained_%s' % curriculum_year)) == 0:
            validation_messages['credits_obtained_%s' % curriculum_year] = _('mandatory_field')
            is_valid = False
            curriculum.credits_obtained = None
    if request.POST.get('credits_obtained_%s' % curriculum_year) \
            and len(request.POST.get('credits_obtained_%s' % curriculum_year)) > 0:
            try:
                credits = float(request.POST.get('credits_obtained_%s' % curriculum_year)
                            .strip().replace(',', '.'))
                curriculum.credits_obtained = credits
                if credits > 75:
                    validation_messages['credits_obtained_%s' % curriculum_year] = _('credits_too_high')
                    is_valid = False
                else:
                    if credits < 0:
                        validation_messages['credits_obtained_%s' % curriculum_year] = _('credits_negative')
                        is_valid = False
            except ValueError:
                validation_messages['credits_obtained_%s' % curriculum_year] = _('numeric_field')
                is_valid = False
    return is_valid, validation_messages, curriculum


def validate_foreign_university_fields_form(request, curriculum, curriculum_year, validation_messages, is_valid, universities_cities, universities, high_non_universities_cities,
                                                                                                        high_non_universities_names):
    print('validate_foreign_university_fields_form')
    cities_list = []
    universities_list = []
    high_non_universities_cities_list = []
    high_non_universities_names_list = []
    national_institution = mdl_reference.education_institution.EducationInstitution()
    national_institution.adhoc = False

    if curriculum.path_type == 'FOREIGN_UNIVERSITY':
        if request.POST.get('foreign_institution_country_%s' % curriculum_year) is None \
                or request.POST.get('foreign_institution_country_%s' % curriculum_year) == "-":
            validation_messages['foreign_institution_country_%s' % curriculum_year] = _('mandatory_field')
            is_valid = False
        else:
            country = mdl_reference.country.find_by_id(int(request.POST.get('foreign_institution_country_%s' % curriculum_year) ))
            universities_by_country = mdl_reference.education_institution.find_by_country(country)

            for university in universities_by_country:
                cities_list.append(university.city)

            national_institution.country = country
            if (request.POST.get('foreign_institution_city_%s' % curriculum_year) is None \
                    or request.POST.get('foreign_institution_city_%s' % curriculum_year) == "-") \
                    and request.POST.get('city_specify_%s' % curriculum_year) is None:
                validation_messages['foreign_institution_city_%s' % curriculum_year] = _('mandatory_field')
                is_valid = False
            else:
                universities_by_city = mdl_reference.education_institution.find_by_city(request.POST.get('foreign_institution_city_%s' % curriculum_year))

                for university in universities_by_city:
                    universities_list.append(university)

                if request.POST.get('foreign_institution_city_%s' % curriculum_year) \
                        and request.POST.get('foreign_institution_city_%s' % curriculum_year) != "-":
                    national_institution.city = request.POST.get('foreign_institution_city_%s' % curriculum_year)
                else:
                    national_institution.city = request.POST.get('city_specify_%s' % curriculum_year)
                    national_institution.adhoc = True
                if (request.POST.get('foreign_institution_name_%s' % curriculum_year) is None \
                    or request.POST.get('foreign_institution_name_%s' % curriculum_year) == "-") \
                        and (request.POST.get('name_specify_%s' % curriculum_year) is None or len(request.POST.get('name_specify_%s' % curriculum_year)) == 0):
                    validation_messages['foreign_institution_%s' % curriculum_year] = _('mandatory_university_name')
                    is_valid = False
                else:
                    if (request.POST.get('foreign_institution_name_%s' % curriculum_year)
                            and request.POST.get('foreign_institution_name_%s' % curriculum_year) != "-"):
                        national_institution = mdl_reference.education_institution\
                            .find_by_id(int(request.POST.get('foreign_institution_name_%s' % curriculum_year)))
                        national_institution = national_institution
                    else:
                        if request.POST.get('name_specify_%s' % curriculum_year) \
                               and len(request.POST.get('name_specify_%s' % curriculum_year)) > 0:
                            national_institution.name = request.POST.get('name_specify_%s' % curriculum_year)
                            national_institution.adhoc = True

        if national_institution.adhoc is True:
            national_institution.save()
        else:
            national_institution = mdl_reference.education_institution.find_by_country_city_name(national_institution.country, national_institution.city, national_institution.name)

        curriculum.national_institution = national_institution

        universities_cities.append(cities_list)
        universities.append(universities_list)
    print('abant ici',curriculum_year)

    if curriculum.path_type == "FOREIGN_HIGH_EDUCATION":
        print('ici', request.POST.get('foreign_high_institution_country_%s' % curriculum_year))
        if request.POST.get('foreign_high_institution_name_%s' % curriculum_year) \
                and request.POST.get('foreign_high_institution_name_%s' % curriculum_year) != "-":
            print('ici1')
            if (request.POST.get('national_institution_locality_adhoc_%s' % curriculum_year) is None \
                or request.POST.get('national_institution_locality_adhoc_%s' % curriculum_year) != "on") \
                    and (request.POST.get('national_institution_name_adhoc_%s' % curriculum_year) is None \
                         or request.POST.get('national_institution_name_adhoc_%s' % curriculum_year) != "on"):

                n= mdl_reference.education_institution\
                    .find_by_id(int(request.POST.get('foreign_high_institution_name_%s' % curriculum_year)))
                print('ici2', n)
                curriculum.national_institution = n
            else:

                national_institution = mdl_reference.education_institution.EducationInstitution()
                national_institution.adhoc = True
                if request.POST.get('national_institution_locality_adhoc_%s' % curriculum_year) == "on":
                    if request.POST.get('city_specify_%s' % curriculum_year) is None:
                        validation_messages['foreign_institution_city_%s' % curriculum_year] = _('mandatory_field')
                        is_valid = False
                    else:
                        national_institution.city = request.POST.get('city_specify_%s' % curriculum_year)
                if request.POST.get('national_institution_name_adhoc_%s' % curriculum_year) == "on":
                    if request.POST.get('name_specify_%s' % curriculum_year) is None:
                        validation_messages['foreign_institution%s' % curriculum_year] = _('mandatory_field')
                        is_valid = False
                    else:
                        national_institution.name = request.POST.get('txt_name_specify_%s' % curriculum_year)

                if request.POST.get('foreign_high_institution_country_%s' % curriculum_year) \
                    and request.POST.get('foreign_high_institution_country_%s' % curriculum_year) == "-":
                    validation_messages['foreign_institution_country_%s' % curriculum_year] = _('mandatory_field')
                    is_valid = False
                else:
                    national_institution.country = mdl_reference.country.find_by_id(int(request.POST.get('foreign_high_institution_country_%s' % curriculum_year)))
                #to avoid duplication
                existing_national_institution = mdl_reference.education_institution.find_by_country_city_name(national_institution.country, national_institution.city, national_institution.name)
                if existing_national_institution:
                    curriculum.national_institution = existing_national_institution
                else:
                    curriculum.national_institution = national_institution
        if curriculum.national_institution.country:
            high_non_universities_by_country = mdl_reference.education_institution.find_by_country(curriculum.national_institution.country)

            for university in high_non_universities_by_country:
                high_non_universities_cities_list.append(university.city)
        if curriculum.national_institution.city:
            universities_by_city = mdl_reference.education_institution.find_by_city(curriculum.national_institution.city)
            for university in universities_by_city:
                universities_list.append(university)

    if request.POST.get('domain_foreign_%s' % curriculum_year) is None \
            or request.POST.get('domain_foreign_%s' % curriculum_year) == '-':
        validation_messages['domain_foreign_%s' % curriculum_year] = _('mandatory_field')
        is_valid = False
    else:
        domain = mdl.domain.find_by_id(int(request.POST.get('domain_foreign_%s' % curriculum_year)))
        curriculum.domain = domain
        if domain.sub_domains:
            if request.POST.get('subdomain_foreign_%s' % curriculum_year) is None \
                        or request.POST.get('subdomain_foreign_%s' % curriculum_year) == '-':
                validation_messages['subdomain_foreign_%s' % curriculum_year] = _('mandatory_field')
                is_valid = False
            else:
                sub_domain = mdl.domain.find_by_id(int(request.POST.get('subdomain_foreign_%s' % curriculum_year)))
                curriculum.sub_domain = sub_domain

    if request.POST.get('grade_type_%s' % curriculum_year) is None \
            or request.POST.get('grade_type_%s' % curriculum_year) == '-':
        validation_messages['grade_type_%s' % curriculum_year] = _('mandatory_field')
        is_valid = False
    else:
        grade_type = mdl.grade_type.find_by_id(int(request.POST.get('grade_type_%s' % curriculum_year)))
        curriculum.grade_type = grade_type

    if request.POST.get('diploma_title_%s' % curriculum_year):
        curriculum.diploma_title = request.POST.get('diploma_title_%s' % curriculum_year)

    if request.POST.get('diploma_foreign_%s' % curriculum_year) is None:
        validation_messages['diploma_foreign_%s' % curriculum_year] = _('mandatory_field')
        is_valid = False
    else:
        if request.POST.get('diploma_foreign_%s' % curriculum_year) == "true":
            curriculum.diploma = True

    if request.POST.get('result_%s' % curriculum_year) is None \
            and ((curriculum.academic_year.year < 2014) or (curriculum.academic_year.year >= 2014 and curriculum.diploma)):
        validation_messages['result_%s' % curriculum_year] = _('mandatory_field')
        is_valid = False
    else:
        curriculum.result = request.POST.get('result_%s' % curriculum_year)

    if request.POST.get('credits_enrolled_foreign_%s' % curriculum_year) \
            and len(request.POST.get('credits_enrolled_foreign_%s' % curriculum_year)) > 0:
            try:
                credits = float(request.POST.get('credits_enrolled_foreign_%s' % curriculum_year)\
                            .strip().replace(',', '.'))
                curriculum.credits_enrolled = credits
                if credits > 75:
                    validation_messages['credits_enrolled_foreign_%s' % curriculum_year] = _('credits_too_high')
                    is_valid = False
                else:
                    if credits < 0:
                        validation_messages['credits_enrolled_foreign_%s' % curriculum_year] = _('credits_negative')
                        is_valid = False
            except ValueError:
                validation_messages['credits_enrolled_foreign_%s' % curriculum_year] = _('numeric_field')
                is_valid = False

    if request.POST.get('credits_obtained_foreign_%s' % curriculum_year) \
            and len(request.POST.get('credits_obtained_foreign_%s' % curriculum_year)) > 0:
            try:
                credits = float(request.POST.get('credits_obtained_foreign_%s' % curriculum_year)
                            .strip().replace(',', '.'))
                curriculum.credits_obtained = credits
                if credits > 75:
                    validation_messages['credits_obtained_foreign_%s' % curriculum_year] = _('credits_too_high')
                    is_valid = False
                else:
                    if credits < 0:
                        validation_messages['credits_obtained_foreign_%s' % curriculum_year] = _('credits_negative')
                        is_valid = False
            except ValueError:
                validation_messages['credits_obtained_foreign_%s' % curriculum_year] = _('numeric_field')
                is_valid = False

    if request.POST.get('linguistic_regime_%s' % curriculum_year) \
            and request.POST.get('linguistic_regime_%s' % curriculum_year) != "-":
        l = mdl_reference.language.find_by_id(int(request.POST.get('linguistic_regime_%s' % curriculum_year)))
        curriculum.language = l
    if len(high_non_universities_cities_list) > 0:
        high_non_universities_cities.append(high_non_universities_cities_list)
    if len(high_non_universities_names_list) > 0:
        high_non_universities_names.append(high_non_universities_names_list)
    return is_valid, validation_messages, curriculum, universities_cities, universities, high_non_universities_cities, high_non_universities_names


def populate_dropdown_list(curricula):
    universities_cities = []
    universities = []
    for curriculum in curricula:
        cities_list = []
        universities_list = []
        if curriculum.national_institution:
            universities_by_city = mdl_reference.education_institution.find_by_city(curriculum.national_institution.city)
            universities_by_country = mdl_reference.education_institution.find_by_country(curriculum.national_institution.country)

            for university in universities_by_country:
                cities_list.append(university.city)

            universities_cities.append(cities_list)
            for university in universities_by_city:
                universities_list.append(university)
            universities.append(universities_list)
    return universities_cities, universities


def populate_dropdown_foreign_high_list(curricula):
    foreign_high_institution_countries = []
    foreign_high_institution_cities = []
    foreign_high_institutions = []
    for curriculum in curricula:
        cities_list = []
        institutions_list = []
        countries_list = []
        if curriculum.national_institution:
            institutions_by_city = mdl_reference.education_institution.find_by_city_country(curriculum.national_institution.city,curriculum.national_institution.country)
            institution_by_country = mdl_reference.education_institution.find_by_country(curriculum.national_institution.country)
            countries_list.append(curriculum.national_institution.country)
            foreign_high_institution_countries.append(countries_list)
            for institution in institution_by_country:
                cities_list.append(institution.city)

            foreign_high_institution_cities.append(cities_list)

            for institution in institutions_by_city:
                institutions_list.append(institution)
            foreign_high_institutions.append(institutions_list)

    return  foreign_high_institution_countries, foreign_high_institution_cities, foreign_high_institutions