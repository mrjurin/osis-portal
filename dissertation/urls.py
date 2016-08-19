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

from django.conf.urls import url
from dissertation.views import common, dissertation, proposition_dissertation


urlpatterns = [
    url(r'^$', common.home, name='dissertation'),

    url(r'^dissertations/$', dissertation.dissertations,
        name='dissertations'),
    url(r'^dissertation_delete/(?P<pk>[0-9]+)$', dissertation.dissertation_delete,
        name='dissertation_delete'),
    url(r'^dissertation_detail/(?P<pk>[0-9]+)/$', dissertation.dissertation_detail,
        name='dissertation_detail'),
    url(r'^dissertation_history/(?P<pk>[0-9]+)$', dissertation.dissertation_history,
        name='dissertation_history'),
    url(r'^dissertations_search$', dissertation.dissertations_search,
        name='dissertations_search'),
    url(r'^dissertation_to_dir_submit/(?P<pk>[0-9]+)$', dissertation.dissertation_to_dir_submit,
        name='dissertation_to_dir_submit'),

    url(r'^proposition_dissertations/$', proposition_dissertation.proposition_dissertations,
        name='proposition_dissertations'),
    url(r'^proposition_dissertation_detail/(?P<pk>[0-9]+)/$', proposition_dissertation.proposition_dissertation_detail,
        name='proposition_dissertation_detail'),
    url(r'^proposition_dissertations_search$', proposition_dissertation.proposition_dissertations_search,
        name='proposition_dissertations_search'),
]
