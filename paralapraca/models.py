# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.contrib.auth.models import Group
from django.contrib.postgres.fields import ArrayField
from autoslug import AutoSlugField
from discussion.models import TopicNotification
from activities.models import Activity
from core.models import Class, CertificateTemplate
from core.utils import hash_name

@python_2_unicode_compatible
class Contract(models.Model):
    name = models.CharField(_('Name'), max_length=255)
    slug = AutoSlugField(_('Slug'), populate_from='name', max_length=128, editable=False, unique=True)
    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_('Groups created to enforce this contract restrictions in several other models'),
        related_name='contract',
    )
    classes = models.ManyToManyField(Class, related_name='contract')
    unities = ArrayField(
        models.CharField(max_length=255, blank=True),
        help_text=_('Possibly cities. This field stores the user declared unities on contract creation. This are used to distinguish some special grupos associated to the contract')
    )

    @property
    def unities_normalized(self):
        return filter(lambda x: x !=  '', [x.strip().rstrip().lower() for x in self.unities])

    class Meta:
        verbose_name = _('Contract')
        verbose_name_plural = _('Contracts')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class AnswerNotification(TopicNotification):

    activity = models.ForeignKey(Activity)


class UnreadNotification(models.Model):

    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name='user', on_delete=models.CASCADE)
    counter = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            # This is a new unread counter
            # All AnswerNotification and TopicNotification will be used to create the first unread counter for this user
            # However, counting only the unread TopicNotification instances is enough, since every AnswerNotification also has a row in the TopicNotification table
            self.counter = TopicNotification.objects.filter(
                user=self.user,
                is_read=False).count()
        super(UnreadNotification, self).save(*args, **kwargs)


class CertificateData(models.Model):
    site_logo = models.ImageField(_('Site Logo'), null=True, blank=True,
                                  upload_to=hash_name('site_logo', 'type'))

    text = models.TextField(_('Content'), default='')
    TYPES = (
        ('receipt', _('Receipt')),
        ('certificate', _('Certificate')),
    )

    type = models.CharField(_('Certificate Type'), choices=TYPES,
                            max_length=127)

    contract = models.ForeignKey(Contract)
    certificate_template = models.ForeignKey(CertificateTemplate)

    class Meta:
        verbose_name = _('Certificate Data')
        unique_together = ('contract', 'certificate_template', 'type')

    def __unicode__(self):
        return u'Data of {0} ({1})'.format(self.contract, self.type)

    def __str__(self):
        return 'Data of {0} ({1})'.format(self.contract, self.type)

    @property
    def site_logo_url(self):
        if self.site_logo:
            return self.site_logo.url
        return ''
