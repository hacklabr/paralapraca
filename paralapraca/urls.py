# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from django.views.generic import TemplateView
from rest_framework import routers

from views import CertificateDataViewSet, CertificateImageDataViewSet, CertificateDataAdminView
from . import views

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'answer-notification', views.AnswerNotificationViewSet)
router.register(r'unread-notification', views.UnreadNotificationViewSet)
router.register(r'contract', views.ContractViewSet)
router.register(r'summary', views.SummaryViewSet, base_name='summary')
router.register(r'users-by-group', views.UsersByGroupViewSet, base_name='users-by-group')
router.register(r'users-by-class', views.UsersByClassViewSet, base_name='users-by-class')

router.register(r'group', views.ContractGroupViewSet, base_name='group')
router.register(r'group_admin', views.ContractGroupAdminViewSet, base_name='group_admin')
router.register(r'course_classes', views.ContractClassViewSet, base_name='course_classes')
router.register(r'certificate_template', CertificateDataViewSet, base_name='certificate_template')
router.register(r'certificate_template_images', CertificateImageDataViewSet, base_name='certificate_template_images')

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="base.html")),
    url(r'^api/', include(router.urls)),
    url(r'^chat/?$', views.ChatScreenView.as_view(template_name="chat.html"), name='chat_screen'),
    url(r'^_chat/auth/$', views.RocketchatIframeAuthView.as_view(), name='rocketchat_iframe_auth'),
    url(r'^contract-edit.html$', TemplateView.as_view(template_name="contract-edit.html")),
    url(r'^contract-detail.html$', TemplateView.as_view(template_name="contract-detail.html")),
    url(r'^contracts-list.html$', TemplateView.as_view(template_name="contracts-list.html")),
    url(r'^certificates-list.html$', TemplateView.as_view(template_name="administration/certificates-list.html")),

    url(r'^admin/contracts/upload_data$', views.contract_uploader_view, name="contract_uploader"),
    url(r'^admin/contracts$', TemplateView.as_view(template_name="contracts.html"), name="contracts"),
    url(r'^admin/certificates$', CertificateDataAdminView.as_view(template_name="administration/certificate-data.html"), name='administration.certificates'),
    url(r'^admin/certificate_settings/(?P<pk>[1-9][0-9]*)/$', CertificateDataAdminView.as_view(template_name="certificate-settings.html"), name="certificate_settings"),

    url(r'^certificate/(?P<slug>[-a-zA-Z0-9_]+)/$', views.CourseCertificationDetailView.as_view(), name='certificate'),
    url(r'^certificate/(?P<slug>[-a-zA-Z0-9_]+)/print/$', views.CourseCertificationDetailView.as_view(template_name="certificate_print.html"), name='certificate-print'),

]
