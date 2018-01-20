# -*- coding: utf-8 -*-
import json

from braces.views import LoginRequiredMixin, _access
from django.conf import settings
from django.http import HttpResponse, Http404
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, DetailView
from django.core.exceptions import PermissionDenied

from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.viewsets import ModelViewSet

from core.models import Course, CourseStudent, Class, CertificateTemplate, CourseCertification
from core import views as core_views
from core.permissions import IsProfessorCoordinatorOrAdminPermissionOrReadOnly
from core.serializers import CertificateTemplateImageSerializer, CourseCertificationSerializer

from accounts.models import TimtecUser, Group
from accounts.views import GroupViewSet, GroupAdminViewSet

from paralapraca.serializers import (AnswerNotificationSerializer,
    UnreadNotificationSerializer, UserInDetailSerializer,
    UsersByClassSerializer, ContractSerializer, ContractGroupSerializer)
from paralapraca.models import (AnswerNotification, UnreadNotification,
                                Contract, CertificateData)
from paralapraca.serializers import ContractGroupAdminSerializer, ContractClassSerializer, \
    CertificateDataSerializer, CertificateImageDataSerializer, SimpleContractSerializer

from discussion.models import Comment, CommentLike, Topic, TopicLike
from rest_pandas import PandasViewSet
from rest_pandas.renderers import PandasCSVRenderer, PandasJSONRenderer
import pandas as pd

from administration.views import AdminMixin
from serializers import ClassSerializer, CourseGroupSerializer

ROCKET_CHAT = {
    'address': 'http://chat.paralapraca.org.br',
    'service': 'paralapraca'
}



class ChatScreenView(TemplateView):
    template_name = 'chat.html'

    def get_context_data(self, **kwargs):
        context = super(ChatScreenView, self).get_context_data(**kwargs)
        context['rocketchat'] = getattr(settings, 'ROCKET_CHAT', ROCKET_CHAT)
        return context


class RocketchatIframeAuthView(TemplateView):
    template_name = 'rocketchat.html'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(RocketchatIframeAuthView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(RocketchatIframeAuthView, self).get_context_data(**kwargs)
        context['rocketchat'] = getattr(settings, 'ROCKET_CHAT', ROCKET_CHAT)
        return context

    def get(self, request, *argz, **kwargz):
        response = super(RocketchatIframeAuthView, self).get(request, *argz, **kwargz)
        return response

    def post(self, request, *argz, **kwargz):
        origin = request.META.get('HTTP_ORIGIN', '')
        token = request.COOKIES.get('rc_token', '')

        response = HttpResponse(json.dumps({
            'token': token
        }))

        response['Content-Type'] = 'application/json'
        response['Access-Control-Allow-Origin'] = origin
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE'
        response["Access-Control-Allow-Headers"] = "Origin, X-Requested-With, Content-Type, Accept"

        return response


class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.query_params.get('simple', None):
            self.serializer_class = SimpleContractSerializer

        return super(ContractViewSet, self).get_serializer_class()

    def _get_groups_data(self, instance, request):
        curr_group_set = instance.groups.values_list('id', flat=True)
        new_group_set = request.data.get('groups', [])
        new_group_set = [g['id'] for g in new_group_set]
        return curr_group_set, new_group_set

    def _get_classes_data(self, instance, request):
        curr_class_set = instance.classes.values_list('id', flat=True)
        new_class_set = request.data.get('classes', [])
        new_class_set = [c['id'] for c in new_class_set]
        return curr_class_set, new_class_set

    def _get_set_diff(self, curr, new):
        remove = set(curr) - set(new)
        add = set(new) - set(curr)
        return add,remove

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        curr_group_set, new_group_set = self._get_groups_data(instance, request)
        g_add, g_remove = self._get_set_diff(curr_group_set, new_group_set)
        for g in g_add:
            instance.groups.add(g)
        for g in g_remove:
            instance.groups.remove(g)

        curr_class_set, new_class_set = self._get_classes_data(instance, request)
        c_add, c_remove = self._get_set_diff(curr_class_set, new_class_set)
        for c in c_add:
            instance.classes.add(c)
        for c in c_remove:
            instance.classes.remove(c)

        return super(ContractViewSet, self).update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        MContractSerializer = self.get_serializer_class()
        serializer = MContractSerializer(data=request.data)
        if serializer.is_valid():
            contract = serializer.save()
        else:
            return Response({"error" : "Error creating new Contract"}, status.HTTP_400_BAD_REQUEST)

        curr_group_set, new_group_set = self._get_groups_data(contract, request)
        g_add, g_remove = self._get_set_diff(curr_group_set, new_group_set)
        for g in g_add:
            contract.groups.add(g)
        for g in g_remove:
            contract.groups.remove(g)

        curr_class_set, new_class_set = self._get_classes_data(contract, request)
        c_add, c_remove = self._get_set_diff(curr_class_set, new_class_set)
        for c in c_add:
            contract.classes.add(c)
        for c in c_remove:
            contract.classes.remove(c)

        return Response(serializer.data, status.HTTP_201_CREATED)


class ClassViewSet(viewsets.ModelViewSet):
    queryset = Class.objects.all()
    serializer_class = ClassSerializer
    filter_fields = ('course',)

class AnswerNotificationViewSet(viewsets.ModelViewSet):
    """
    """

    queryset = AnswerNotification.objects.all()
    serializer_class = AnswerNotificationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'topic'

    def get_queryset(self):
        queryset = super(AnswerNotificationViewSet, self).get_queryset()
        queryset = queryset.filter(user=self.request.user)

        limit_to = self.request.query_params.get('limit_to', None)
        if limit_to:
            queryset = queryset[:int(limit_to)]
        return queryset

    def update(self, request, **kwargs):
        # Find the corresponding AnswerNotification for this call and mark it as read
        try:
            notification = AnswerNotification.objects.get(topic=kwargs.get('topic'), user=request.user)
            notification.is_read = True
            notification.save(skip_date=True)
            return Response(self.get_serializer(notification).data, status=status.HTTP_200_OK)
        except AnswerNotification.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
            pass


class UnreadNotificationViewSet(viewsets.ModelViewSet):

    queryset = UnreadNotification.objects.all()
    serializer_class = UnreadNotificationSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, pk=None):
        # Since the frontend is sending a PUT request to this view, the counter must be reset
        unread = UnreadNotification.objects.get(user=self.request.user)
        unread.counter = 0
        unread.save()
        return Response(self.get_serializer(unread).data)

    def get_queryset(self):
        # If the user is new, a new UnreadNotification must be created
        queryset = UnreadNotification.objects.filter(user=self.request.user)
        if queryset.count() == 0:
            UnreadNotification.objects.create(user=self.request.user)
            queryset = UnreadNotification.objects.filter(user=self.request.user)
        return queryset

class SummaryViewSet(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    def list(self, request):
        courses = Course.objects.all()
        stats = []
        for course in courses:
            course_stats = {
                'name': course.name,
                'user_count': course.coursestudent_set.count(),
                'user_finished_course_count': 0
            }
            classes = Class.objects.filter(course=course)
            classes_stats = []
            for cclass in classes:
                cclass_stats = {
                    'name': cclass.name,
                    'user_count': cclass.get_students.count(),
                    'certificate_count': 0,
                    'user_finished': 0
                }

                course_students = cclass.get_students.all()
                certified = course_students.filter(certificate__type='certificate')
                cclass_stats['certificate_count'] += certified.count()

                for cs in course_students:
                    # if cs.course_finished:
                    #    cclass_stats['user_finished'] += 1
                    if cs.can_emmit_receipt():
                        course_stats['user_finished_course_count'] += 1
                        cclass_stats['user_finished'] += 1

                classes_stats.append(cclass_stats)

            course_stats['classes'] = classes_stats
            stats.append(course_stats)

        response = Response({
            'user_count': TimtecUser.objects.count(),
            'total_number_of_topics': Topic.objects.count(),
            'total_number_of_comments': Comment.objects.count(),
            'total_number_of_likes': TopicLike.objects.count() + CommentLike.objects.count(),
            'statistics_per_course': stats})
        return response


class UsersByGroupViewSet(PandasViewSet):

    permission_classes = [IsAuthenticated]
    renderer_classes = [PandasCSVRenderer, PandasJSONRenderer]
    queryset = TimtecUser.objects.all()

    def list(self, request, format=None):
        groups = request.query_params.get('group', None)
        if groups is not None:
            serializer = UserInDetailSerializer(self.queryset.filter(groups__name__in=groups.split(',')), many=True)
        else:
            serializer = UserInDetailSerializer(self.queryset, many=True)
        # in order to get the data in the wanted column form, I'll need to make some transformations
        return Response(self.transform_data(serializer.data))

    def transform_data(self, data):
        response = []
        for user in data:
            for course in user.get('courses'):
                user.update({
                    u'{} - progresso'.format(course['course_name']): course['percent_progress'],
                    u'{} - nome da turma'.format(course['course_name']): course['class_name'],
                    u'{} - concluiu'.format(course['course_name']): course['course_finished'],
                    u'{} - possui certificado'.format(course['course_name']): course['has_certificate']
                })
            user.pop('courses', None)
            response.append(user)
        return pd.DataFrame.from_dict(response)


class UsersByClassViewSet(PandasViewSet):

    permission_classes = [IsAuthenticated]
    queryset = CourseStudent.objects.all()

    def list(self, request, format=None):
        try:
            ids = request.query_params.get('id', None).split(',')
            ids = [int(i) for i in ids]
        except AttributeError:
            ids = []

        classes = Class.objects.all().filter(pk__in=ids)
        students = [cls.students.all() for cls in classes]
        students = [s for cls in students for s in cls]
        courses = [cls['course_id'] for cls in classes.values()]

        queryset = self.queryset
        if len(ids) > 0:
            queryset = self.queryset \
                .filter(user__in=students, course__id__in=courses)

        serializer = UsersByClassSerializer(queryset, many=True)

        return Response(pd.DataFrame
                        .from_dict(self.transform_data(serializer.data))
                        .set_index('cpf'))

    def transform_data(self, data):
        for coursestudent in data:
            for lesson in coursestudent.get(u'percent_progress_by_lesson', None):
                coursestudent.update({
                    u'Lição {} - Progresso'.format(lesson['name']): lesson['progress']
                })
                for activity in lesson.get(u'activities', None):
                    coursestudent.update({
                        u'Lição {} - Atividade {} realizada'.format(lesson['name'], activity['name']): activity['done']
                    })
            coursestudent.pop('percent_progress_by_lesson', None)
        return data


class ContractGroupViewSet(GroupViewSet):
    """
    Override group viewset add contracts.
    """
    def get_serializer_class(self):
        return ContractGroupSerializer


class ContractGroupAdminViewSet(GroupAdminViewSet):
    """
    Override group viewset add contracts.
    """
    def get_serializer_class(self):
        return ContractGroupAdminSerializer


class ContractClassViewSet(core_views.ClassViewSet):
    """
    Override group viewset add contracts.
    """

    def get_queryset(self):
        queryset = super(ContractClassViewSet, self).get_queryset()

        contract_id = self.request.query_params.get('contract')
        if contract_id:
            try:
                contracts = [Contract.objects.get(pk=contract_id), ]
            except Contract.DoesNotExist:
                return  Class.objects.none()

            queryset.filter(contract__in=contracts)

        return queryset

    def get_serializer_class(self):
        return ContractClassSerializer


class CertificateDataAdminView(AdminMixin, TemplateView, _access.AccessMixin):
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):

        response = super(CertificateDataAdminView, self)\
            .dispatch(request, *args, **kwargs)

        if not (request.user.is_superuser or self.object.get_professor_role(request.user) == 'coordinator'):
            if self.raise_exception:  # *and* if an exception was desired
                raise PermissionDenied  # return a forbidden response.

        return response


class CertificateDataMixin(viewsets.ModelViewSet):
     def get_queryset(self):
        queryset = CertificateData.objects.all()
        course = self.request.query_params.get('course', None)
        if course:
            queryset = queryset.filter(certificate_template__course=course)

        contract = self.request.query_params.get('contract', None)
        if contract:
            queryset = queryset.filter(contract=contract)

        return queryset


class CertificateDataViewSet(LoginRequiredMixin, CertificateDataMixin, viewsets.ModelViewSet):
    model = CertificateData
    serializer_class = CertificateDataSerializer

    def create(self, request, *args, **kwargs):
        generate =  request.data.get('generate', False)
        if generate:
            data = request.data
            current = CertificateData.objects.filter(certificate_template__course__id=data.get('course', None),
                                                     contract__id=data.get('contract', None))

            if len(current) >= 2:
                return Response({'error' : 'Os templates já existem'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                course = Course.objects.get(pk=data.get('course', None))
                contract = Contract.objects.get(pk=data.get('contract', None))
                if len(current) > 0:
                    ct = CertificateTemplate(course=course)
                    ct.save()
                    t = CertificateData.TYPES[0]
                    if 'receipt' == current[0].type:
                        t = CertificateData.TYPES[1]
                    cd = CertificateData(type=t[0], contract=contract, certificate_template=ct)
                    cd.save()
                    return Response({'message' : 'Os templates foram criados com sucesso'})
                else:
                    for t in CertificateData.TYPES:
                        ct = CertificateTemplate(course=course)
                        ct.save()
                        cd = CertificateData(type=t[0], contract=contract, certificate_template=ct)
                        cd.save()

                    return Response({'message' : 'Os templates foram criados com sucesso'})
        else:
            super(CertificateDataViewSet, self).create(request, *args, **kwargs)


class CertificateImageDataViewSet(CertificateDataMixin, viewsets.ModelViewSet):
    queryset = CertificateData.objects.all()
    model = CertificateData
    permission_classes = (IsProfessorCoordinatorOrAdminPermissionOrReadOnly, )

    def post(self, request, **kwargs):
        obj = self.get_object()
        errors = []

        clear_logos = (
            ('base_logo', request.data.get('base_logo_clear', None)),
            ('signature', request.data.get('signature_clear', None)),
            ('cert_logo', request.data.get('cert_logo_clear', None)),
        )
        for cl in clear_logos:
            if(cl[1]):
                setattr(obj.certificate_template, cl[0], None)

        ct_serializer = CertificateTemplateImageSerializer(
            obj.certificate_template, request.FILES)
        if ct_serializer.is_valid():
            ct_serializer.save()
        else:
            errors += ct_serializer.errors

        cl = ('site_logo', request.data.get('site_logo_clear', None))
        if(cl[1]):
            setattr(obj, cl[0], None)
        serializer = CertificateImageDataSerializer(obj, request.FILES)
        if serializer.is_valid():
            serializer.save()
        else:
            errors += serializer.errors

        if len(errors) > 0:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            s = CertificateDataSerializer(obj)
            return Response(s.data, status=status.HTTP_200_OK)


class CourseCertificationDetailView(DetailView):
    model = CourseCertification
    template_name = 'certificate.html'
    slug_field = "link_hash"
    serializer_class = CourseCertificationSerializer

    def render_to_response(self, context, **response_kwargs):
        from django.core.urlresolvers import resolve

        certificate = context.get('object')
        contract = certificate.course_student\
            .get_current_class().contract.first()

        if not certificate.course_student.can_emmit_receipt():
            raise Http404

        if certificate:
            context['cert_template'] = CertificateData.objects\
                .get(certificate_template__course=certificate.course_student.course,
                     type=certificate.type, contract=contract)
            # Interpolate data into text string
            # {Nome} : certificate.student (name)
            # {CPF} : certificate.student.cpf)
            # {MODULO} : certificate.course.name)
            # {CONTRATO} : context['cert_template'].contract.name)
            # {NUM_UNIDADES} : str(certificate.course_total_units))
            # {TURMA} : certificate.course_student.get_current_class().name)

            context['cert_template'].text = context['cert_template'].text\
                .replace('{NOME}', certificate.student.get_full_name())\
                .replace('{CPF}', certificate.student.cpf)\
                .replace('{MODULO}', certificate.course.name)\
                .replace('{CONTRATO}', context['cert_template'].contract.name) \
                .replace('{NUM_UNIDADES}', str(certificate.course_total_units))\
                .replace('{TURMA}', certificate.course_student.get_current_class().name)\

        url_name = resolve(self.request.path_info).url_name

        if url_name == 'certificate-download':
            from selenium import webdriver
            from signal import SIGTERM
            from time import gmtime, strftime
            from timtec.settings import MEDIA_ROOT, CERTIFICATE_SIZE, PHANTOMJS_PATH
            from PIL import Image
            import os

            today = strftime("%d%b%Y", gmtime())

            width, height = CERTIFICATE_SIZE
            url = self.request.build_absolute_uri().split('download')[0] + 'print/'
            png_path = os.path.join(MEDIA_ROOT, certificate.link_hash + '.png')
            pdf_filename = certificate.link_hash + today + '.pdf'
            pdf_path = os.path.join(MEDIA_ROOT, pdf_filename)

            driver = webdriver.PhantomJS(executable_path=PHANTOMJS_PATH)
            driver.set_window_size(width, height)
            driver.get(url)
            driver.save_screenshot(filename=png_path)

            driver.service.process.send_signal(SIGTERM)
            driver.quit()
            Image.open(png_path).convert("RGB").save(pdf_path, format='PDF', quality=100, dpi=(300, 300))

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename=%s' % pdf_filename

            certi = open(pdf_path)
            response.write(certi.read())
            certi.close()

            return response
        else:
            return super(CourseCertificationDetailView, self)\
                .render_to_response(context, **response_kwargs)


@api_view(['POST'])
@permission_classes((IsAdminUser,))
def contract_uploader_view(request):
    csv_file = request.FILES.get('file', None)
    contract_id = request.data.get('contract_id', None)
    data = {
        'errors' : {
            'user_exists' : [],
            'class_not_found' : [],
        },
        'stats'  : {
            'inserted' : 0,
            'num_errors': 0,
            'new_groups':0,
        }
    }
    if not contract_id:
        data['errors']['form'] = "Contract must be specified"
        return Response(data, status.HTTP_400_BAD_REQUEST)

    contract = Contract.objects.get(pk=contract_id)
    if csv_file:
        import unicodecsv as csv
        transactions = {
            'create' : [],
            'group_users' : {},
            'class_users' : {},
            'contract' : {
                'group' : [],
                'class' : [],
                'unities' : []
            }
        }
        try:
            cf = csv_file.read().splitlines()
            csv_reader = csv.DictReader(cf)
            csv_reader = [c for c in csv_reader]

            groups = set([c for u in csv_reader for c in u['Grupos']
                         .split(';')])
            for group in groups:
                if not Group.objects.filter(name=group).exists():
                    g = Group(name=group)
                    transactions['create'].append(g)
                    data['stats']['new_groups']+=1

            for user in csv_reader:
                transactions['contract']['unities'] += user[u'Município']\
                    .split(';')
                if not TimtecUser.objects.filter(email=user['Email']).exists():
                    username = slugify((user['Nome'] + user['Sobrenome'])[0:30])
                    tries = 0
                    while TimtecUser.objects.filter(username=username)\
                        .exists() and tries < 10:
                        tries+=1
                        username = username[0:-1] + str(tries)

                    u = TimtecUser(email=user['Email'], cpf=user['CPF'],
                                   username=username,
                                   first_name=user['Nome'][0:30],
                                   last_name=user['Sobrenome'][0:30])
                    transactions['create'].append(u)
                    data['stats']['inserted']+=1
                else:
                    data['errors']['user_exists'].append(user['Nome'] +
                                                         user['Sobrenome'])
                    data['stats']['num_errors']+=1
                    u = None

                groups = user['Grupos'].split(';')
                for group in groups:
                    if not transactions['group_users'].has_key(group):
                        transactions['group_users'][group] = []

                    transactions['contract']['group'].append(group)
                    if u:
                        transactions['group_users'][group].append(u)

                classes = user['Turmas'].split(';')
                for class_course in classes:
                    (cclass, course) = class_course.split(' @ ')
                    if Class.objects.filter(name=cclass, course__slug=course)\
                        .exists():
                        if not transactions['class_users']\
                            .has_key(class_course):
                            transactions['class_users'][class_course] = []
                        if u:
                            transactions['class_users'][class_course].append(u)
                        transactions['contract']['class']\
                            .append(Class.objects
                                    .get(name=cclass, course__slug=course))
                    else:
                        data['errors']['class_not_found'].append(class_course)
                        data['stats']['num_errors']+=1

            if data['stats']['num_errors'] == 0:
                from django.db import transaction
                with transaction.atomic():
                    # create entities
                    for transaction in transactions['create']:
                        transaction.save()

                    # add to groups
                    for group_transaction in transactions['group_users']:
                        group = Group.objects.get(name=group_transaction)
                        for u in transactions['group_users'][group_transaction]:
                            group.user_set.add(u)
                        group.save()

                    # add to classes
                    for class_transaction in transactions['class_users']:
                        (cclass, course) = class_transaction.split(' @ ')
                        cclass = Class.objects\
                            .get(name=cclass, course__slug=course)
                        for u in transactions['class_users'][class_transaction]:
                            cclass.students.add(u)
                            cclass.save()
                            if not CourseStudent.objects\
                                .filter(user=u, course=cclass.course).exists():
                                cs = CourseStudent(user=u, course=cclass.course)
                                cs.save()

                    # add groups and classes to contract
                    groups = Group.objects\
                        .filter(name__in=transactions['contract']['group'])
                    for group in groups:
                        contract.groups.add(group)

                    # add classes to contract
                    classes = transactions['contract']['class']
                    for cclass in classes:
                        contract.classes.add(cclass)

                    unities = contract.unities + \
                              list(set(transactions['contract']['unities']))
                    contract.unities = unities
                    contract.save()
                    serializer = ContractSerializer(instance=contract)
                    data['instance'] = serializer.data
            else:
                serializer = ContractSerializer(instance=contract)
                data['instance'] = serializer.data
                return Response(data, status.HTTP_400_BAD_REQUEST)
        except KeyError:
            data['errors']['form'] = "Not valid CSV file"
            return Response(data, status.HTTP_400_BAD_REQUEST)
    else:
        data['errors']['form'] = "Not valid CSV file"
        return Response(data, status.HTTP_400_BAD_REQUEST)

    return Response(data, status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((IsAdminUser,))
def contract_remove_users_view(request):
    CONTRACT_ARCHIVE_CLASS_PREFIX = "ARQUIVO_"
    contract_id = request.data.get('contract', None)
    if not contract_id:
        return Response({"error" : "Contrato não informado"},
                        status=status.HTTP_400_BAD_REQUEST)

    users = request.data.get('users', None)
    if users:
        users = users.split('\n')
    else:
        return Response({"error" : "Erro ao receber lista de usuários"},
                        status=status.HTTP_400_BAD_REQUEST)

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
    users_to_remove = []
    for u in users:
        if TimtecUser.objects.filter(email=u).exists():
            user = TimtecUser.objects.get(email=u)
            users_to_remove.append(user)
        else:
            errors['num_errors']+=1
            errors['email_with_error'].append(u)

    if errors['num_errors'] == 0:
        groups_remove = contract.groups.values_list('id', flat=True)
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
            archive_classes[c.name] = archive_class

        from django.db import transaction
        with transaction.atomic():
            for u in users_to_remove:
                for g in groups_remove:
                    u.groups.remove(g)

                for g in groups_add:
                    u.groups.add(g)

                for c in u.classes.all().exclude(name__contains="ARQUIVO_"):
                    if c.contract.first().id == contract.id:
                        c.remove_students(u)
                        archive_classes[c.name].add_students(u)

        return Response({}, status=status.HTTP_200_OK)
    else:
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)


class CourseGroupViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseGroupSerializer
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        groups = request.data.get('groups', None)
        course_slug = request.data.get('slug', None)
        instance = Course.objects.get(slug=course_slug)
        if groups:
            for g in groups:
                instance.groups.add(g)
            instance.save()
            serializer = CourseGroupSerializer(instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'error' : 'no group set'},
                            status=status.HTTP_400_BAD_REQUEST)
