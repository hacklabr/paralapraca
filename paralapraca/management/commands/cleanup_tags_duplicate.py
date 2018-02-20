# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from discussion.models import Tag, Topic


class Command(BaseCommand):
    help = 'Remove tag duplicates.'

    def handle(self, **options):
        tags = Tag.objects.all()
        new_tags = dict()
        for tag in tags:
            tag.name = tag.name.replace("#", '').lower()
            tag.save()

        for tag in tags:
            try:
                new_tags[tag.name]+=[tag]
            except :
                new_tags[tag.name]=[tag]

        tag_groups = [x for x in new_tags.values() if len(x) > 1]
        topics_changed = []
        for tg in tag_groups:
            the_one = tg[0]
            the_others = tg[1:]
            for t in the_others:
                for topic in t.topic_set.all():
                     topic.tags.remove(t)
                     topic.tags.add(the_one)
                     topics_changed.append(topic.id)
                t.delete()
        topics_changed_set = set(topics_changed)
        for changed in topics_changed_set:
                print "http://localhost:8000/discussion/topic/#!/topic/%s/" % str(changed)


