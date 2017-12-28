# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.core.files import File

from core.models import CertificateTemplate
from timtec.settings import STATIC_ROOT
from paralapraca.models import CertificateData, Contract

import os

class Command(BaseCommand):
    help = 'Create certificate and receipt templates data for CertificateTemplate existent'

    receipt_text = '<p>inscrita no cadastro de pessoa f&iacute;sica sob o n&uacute;mero {CPF}&nbsp;</p>\
<p>participou do <em>{MODULO}</em></p>\
<p>no Ambiente Virtual de Aprendizagem do Programa Paralaprac&aacute;.</p>'

    certificate_text = '<p style="text-align: center;">inscrita no cadastro de pessoa f&iacute;sica sob o n&uacute;mero&nbsp;{CPF}</p>\
<p style="text-align: center;">concluiu o&nbsp;<strong>{MODULO}</strong>,</p>\
<p style="text-align: center;">com carga hor&aacute;ria total de 40 horas, no&nbsp;</p>\
<p style="text-align: center;">Ambiente Virtual de Aprendizagem&nbsp;do Programa Paralaprac&aacute;.</p>'


    def handle(self, *files, **options):
        types = CertificateData.TYPES

        cts = CertificateTemplate.objects.all()
        plpc = Contract.objects.first()

        plpc_path = os.path.join(STATIC_ROOT, 'img/site-logo-orange.svg')
        avante_path = os.path.join(STATIC_ROOT, 'img/logo-avante.png')
        plpc_logo = File(open(plpc_path, 'r'))
        avante_logo = File(open(avante_path, 'r'))

        for ct in cts:
            ct.base_logo = avante_logo
            ct.save()
            cdr = CertificateData(contract=plpc, type=types[0][0],
                                  certificate_template=ct,
                                  site_logo=plpc_logo,
                                  text=self.receipt_text)
            cdr.save()

            ct.pk = None
            ct.save()

            cdc = CertificateData(contract=plpc, type=types[1][0],
                                  certificate_template=ct,
                                  site_logo=plpc_logo,
                                  text=self.certificate_text)
            cdc.save()
