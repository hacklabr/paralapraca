# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from paralapraca.models import Contract
from accounts.models import Group
from core.models import Class
from django.db.models import Q

TimtecUser = get_user_model()

CONTRACT_ARCHIVE_CLASS_PREFIX = "ARQUIVO_"

class Command(BaseCommand):
    args = 'file'
    help = 'Remove users from a given contract'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('contract_id', nargs='+', type=int)

        # Named (optional) arguments
        parser.add_argument(
            '--dry-run',
            action='store_const',
            dest='dry_run',
            const=True,
            help='Do not execute any alterations, just send stats back',
        )


    def handle(self, *args, **options):
        if options['dry_run']:
            result = self._contract_remove_users_view(options['contract_id'][0], True)
        else:
            result = self._contract_remove_users_view(options['contract_id'][0])

        print(result)

    def _contract_remove_users_view(self, contract_id, dry_run = False):
        contract = Contract.objects.get(id=contract_id)
        contract_archive_group = u'Espaço Aberto %s' % (contract.name,)

        if not Group.objects.filter(name=contract_archive_group).exists():
            contract_archive_group = Group(name=contract_archive_group)
            contract_archive_group.save()
        else:
            contract_archive_group = Group.objects.get(name=contract_archive_group)

        groups_add = [Group.objects.get(name="Espaço Aberto"),
                      Group.objects.get(name="students"), contract_archive_group]

        errors = {
            'num_errors' : 0,
            'email_with_error' : [],
        }
        stats = {
            "users_to_add" : 0,
        }
        users_to_remove = TimtecUser.objects\
            .exclude(is_superuser=True, is_staff=True)\
            .exclude(groups=Group.objects.get(name="Espaço Aberto"))

        stats["users_to_add"] = len(users_to_remove)

        if errors['num_errors'] == 0:
            groups_remove = contract.groups \
                .exclude(Q(name="Avante") | Q(name="Entremeios")) \
                .values_list('id', flat=True)
            contract_classes = contract.classes.exclude(name__contains="ARQUIVO_")
            archive_classes = {}
            for c in contract_classes:
                archive_class_name = "%s%s@%s" % \
                                     (
                                         CONTRACT_ARCHIVE_CLASS_PREFIX,
                                         c.course.name,
                                         contract.name
                                     )
                if not Class.objects \
                    .filter(name=archive_class_name,
                            course=c.course,
                            contract__id=contract_id).exists():
                    archive_class = Class(name=archive_class_name,
                                          course=c.course,)
                    archive_class.save()
                    archive_class.contract.add(contract_id,)
                else:
                    archive_class = Class.objects.get(name=archive_class_name,
                                                         course=c.course,
                                                         contract__id=contract_id)
                archive_classes[c.name + c.course.name] = archive_class

            from django.db import transaction
            with transaction.atomic():
                for u in users_to_remove:
                    for g in groups_remove:
                        if not dry_run:
                            u.groups.remove(g)

                    for g in groups_add:
                        if not dry_run:
                            u.groups.add(g)

                    for c in u.classes.all().exclude(name__contains="ARQUIVO_"):
                        if c.contract.first().id == contract.id:
                            if not dry_run:
                                c.remove_students(u)
                                archive_classes[c.name + c.course.name].add_students(u)

            return (stats, errors)
        else:
            return errors

