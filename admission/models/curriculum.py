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
from django.db import models
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from .secondary_education import NATIONAL_COMMUNITY_TYPES


class CurriculumAdmin(admin.ModelAdmin):
    list_display = ('person', 'path_type')


class Curriculum(models.Model):

    PATH_TYPES = (
            ('LOCAL_UNIVERSITY', _('national_university')),
            ('FOREIGN_UNIVERSITY', _('foreign_university')),
            ('LOCAL_HIGH_EDUCATION', _('high_national_non_university')),
            ('FOREIGN_HIGH_EDUCATION', _('high_foreign_non_university')),
            ('ANOTHER_ACTIVITY', _('other')),
            )

    RESULT_TYPE = (('SUCCEED', _('succeeded')),
                   ('FAILED', _('failed')),
                   ('NO_RESULT', _('no_result')))

    ACTIVITY_TYPES = (
            ('JOB', _('Job')),
            ('INTERNSHIP', _('internship')),
            ('VOLUNTEERING', _('volunteering')),
            ('UNEMPLOYMENT', _('unemployment')),
            ('ILLNESS', _('illness')),
            ('OTHER', _('other')),
            )

    person = models.ForeignKey('Person')
    academic_year = models.ForeignKey('AcademicYear')
    path_type = models.CharField(max_length=25, choices=PATH_TYPES)
    national_education = models.CharField(max_length=20, choices=NATIONAL_COMMUNITY_TYPES, blank=True, null=True)
    language = models.ForeignKey('reference.Language', blank=True, null=True)
    national_institution = models.ForeignKey('reference.EducationInstitution', blank=True, null=True)
    domain = models.ForeignKey('Domain', blank=True, null=True,)
    grade_type = models.ForeignKey('GradeType', blank=True, null=True)
    result = models.CharField(max_length=20, choices=RESULT_TYPE, blank=True, null=True)
    credits_enrolled = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    credits_obtained = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    diploma = models.BooleanField(default=False)
    diploma_title = models.CharField(max_length=255, blank=True, null=True)
    activity_type = models.CharField(max_length=255, choices=ACTIVITY_TYPES, blank=True, null=True)
    activity = models.CharField(max_length=255, blank=True, null=True)
    activity_place = models.CharField(max_length=255, blank=True, null=True)


def find_by_id(an_id):
    return Curriculum.objects.get(pk=an_id)


def find_one_by_academic_year(an_academic_year):
    return Curriculum.objects.filter(academic_year=an_academic_year).first()


def find_user(a_person):
    return Curriculum.objects.filter(person=a_person)


def find_by_person_year(a_person, year):
    return Curriculum.objects.filter(person=a_person, academic_year__year=year).first()