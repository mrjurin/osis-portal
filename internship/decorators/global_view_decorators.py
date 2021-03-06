# -*- coding: utf-8 -*-
############################################################################
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
############################################################################
import base.models as mdl_base
from functools import wraps
from dashboard.views import main as dash_main_view
from django.core.exceptions import MultipleObjectsReturned

def redirect_if_multiple_registrations(function):
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        try:
            mdl_base.student.find_by_user(request.user)
        except MultipleObjectsReturned:
            return dash_main_view.show_multiple_registration_id_error(request)
        response = function(request, *args, **kwargs)
        return response
    return wrapper

