# -*- coding: utf-8 -*-
from __future__ import print_function

from django.core.management.base import BaseCommand
from core.models import CourseStudent, Class
from django.contrib.auth import get_user_model
from django.db import transaction


User = get_user_model()


class Command(BaseCommand):
    help = "All enrolled students should be members of a class. This script finds any incosistent profiles that don't match that condition and may fix the problem, if requested"

    def add_arguments(self, parser):
        parser.add_argument(
            '--recover',
            action='store_true',
            dest='recover',
            default=False,
            help='Put students with no classes in a class',
        )

    @transaction.atomic
    def handle(self, *files, **options):
        users = []
        for cs in CourseStudent.objects.all():
            try:
                Class.objects.get(course=cs.course, students__in=[cs.user])
            except Class.DoesNotExist as e:
                users.append([cs.user, cs.course])
                # cs.user has a student with no class
                # if 'recover' was set, the student must be put in a class now
                if options['recover']:
                    # Find or create the appropriate class
                    cs.course.default_class.students.add(cs.user)

        print(*users, sep='\n')

        if options['recover']:
            print("All enrolled users have a Class")
