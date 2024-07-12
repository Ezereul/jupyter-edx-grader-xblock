"""
Defines a URL to return a notebook html page to be used in an iframe
"""
from django.urls import re_path

from xblock_jupyter_graded.rest.views import (
    DownloadStudentNBView, DownloadInstructorNBView, DownloadAutogradedNBView
)
from django.contrib.auth.decorators import login_required

app_name = 'xblock_jupyter_graded'

urlpatterns = [
    re_path(
    r'^download/student_nb/(?P<course_id>.+)/(?P<unit_id>.+)/(?P<filename>.+)$',
        login_required(DownloadStudentNBView.as_view()),
        name='jupyter_student_dl'
    ),
    re_path(
    r'^download/instructor_nb/(?P<course_id>.+)/(?P<unit_id>.+)/(?P<filename>.+)$',
        login_required(DownloadInstructorNBView.as_view()),
        name='jupyter_instructor_dl'
    ),
    re_path(
    r'^download/autograded_nb/(?P<course_id>.+)/(?P<unit_id>.+)/(?P<filename>.+)$',
        login_required(DownloadAutogradedNBView.as_view()),
        name='jupyter_autograded_dl'
    ),
]



