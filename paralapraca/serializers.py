from rest_framework import serializers
from paralapraca.models import AnswerNotification, UnreadNotification, Contract
from discussion.serializers import BaseTopicSerializer, BaseCommentSerializer, TopicLikeSerializer, CommentLikeSerializer
from accounts.models import TimtecUser
from accounts.serializers import GroupSerializer, GroupAdminSerializer
from core.models import Class, Course
from core.serializers import ClassSerializer as CoreClassSerializer
from django.contrib.auth.models import Group


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = ('id', 'name')


class ClassSerializer(serializers.ModelSerializer):

    course = CourseSerializer(read_only=True)

    class Meta:
        model = Class


class ContractSerializer(serializers.ModelSerializer):

    classes = ClassSerializer(many=True, read_only=True)

    class Meta:
        model = Contract
        depth = 1


class AnswerNotificationSerializer(serializers.ModelSerializer):

    topic = BaseTopicSerializer(read_only=True)
    comment = BaseCommentSerializer(read_only=True)
    topic_like = TopicLikeSerializer(read_only=True)
    comment_like = CommentLikeSerializer(read_only=True)
    activity_url = serializers.SerializerMethodField()
    course_name = serializers.SerializerMethodField()
    course_slug = serializers.SerializerMethodField()

    class Meta:
        model = AnswerNotification
        depth = 1

    def get_activity_url(self, obj):
        course_slug = obj.activity.unit.lesson.course.slug
        lesson_slug = obj.activity.unit.lesson.slug
        unit_num = obj.activity.unit.position + 1
        activity_url = "/course/{}/lesson/{}/#/{}".format(course_slug, lesson_slug, unit_num)
        return activity_url

    def get_course_name(self, obj):
        return obj.activity.unit.lesson.course.name

    def get_course_slug(self, obj):
        return obj.activity.unit.lesson.course.slug


class UnreadNotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = UnreadNotification
        fields = ('id', 'counter', )


class UserInDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = TimtecUser
        fields = sorted(('cpf', 'cities', 'courses', 'date_joined', 'last_login',
                         'full_name', 'topics_created', 'number_of_likes',
                         'comments_created',))

    comments_created = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    topics_created = serializers.SerializerMethodField()
    number_of_likes = serializers.SerializerMethodField()
    courses = serializers.SerializerMethodField()
    cities = serializers.SerializerMethodField()

    def get_cities(self, obj):
        contracts = [contract for group in obj.groups.all() for contract in group.contract.all()]
        group_names = [group.name.lower() for group in obj.groups.all()]
        city_names = [unity for c in contracts for unity in c.unities_normalized]
        return " - ".join(set(city_names) & set(group_names)).capitalize()

    def get_comments_created(self, obj):
        return obj.comment_author.count()

    def get_courses(self, obj):
        needed_stuff = [
            {'percent_progress': x.percent_progress(),
             'course_finished':  x.can_emmit_receipt(),
             'course_name': x.course.name,
             'has_certificate': x.certificate.type == 'certificate',
             'class_name': x.get_current_class().name
            } for x in obj.coursestudent_set.all()]
        return needed_stuff

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_topics_created(self, obj):
        return obj.topic_author.count()

    def get_number_of_likes(self, obj):
        return obj.topiclike_set.count() + obj.commentlike_set.count()


class UsersByClassSerializer(serializers.Serializer):
    # class Meta:
        # model = CourseStudent

        # fields = sorted(('cpf', 'email', 'full_name', 'last_login', 'has_certificate'))

    cpf = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    last_login = serializers.SerializerMethodField()
    has_certificate = serializers.SerializerMethodField()
    percent_progress_by_lesson = serializers.SerializerMethodField()
    percent_progress = serializers.SerializerMethodField()
    course_finished = serializers.SerializerMethodField()
    class_name = serializers.SerializerMethodField()
    cities = serializers.SerializerMethodField()

    def get_cpf(self, obj):
        return obj.user.cpf

    def get_cities(self, obj):
        obj = obj.user
        contracts = [contract for group in obj.groups.all() for contract in group.contract.all()]
        group_names = [group.name.lower() for group in obj.groups.all()]
        city_names = [unity for c in contracts for unity in c.unities_normalized]
        return " - ".join(set(city_names) & set(group_names)).capitalize()

    def get_email(self, obj):
        return obj.user.email

    def get_full_name(self, obj):
        return obj.user.get_full_name()

    def get_last_login(self, obj):
        return obj.user.last_login

    def get_has_certificate(self, obj):
        return obj.certificate.type == 'certificate'

    def get_percent_progress_by_lesson(self, obj):
        return obj.percent_progress_by_lesson()

    def get_percent_progress(self, obj):
        return obj.percent_progress()

    def get_course_finished(self, obj):
        return obj.can_emmit_receipt()

    def get_class_name(self, obj):
        return obj.get_current_class().name


class SimpleContractSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contract
        fields = ('id', 'name')


class ContractBaseSerializerMixin(serializers.ModelSerializer):
    contract = serializers.SerializerMethodField(read_only=False, )

    def get_contract(self, obj):
        return SimpleContractSerializer(obj.contract.first(),).data


class ContractGroupSerializer(ContractBaseSerializerMixin, GroupSerializer):

    class Meta(GroupSerializer.Meta):
        fields = ('id', 'name', 'contract')


class ContractGroupAdminSerializer(ContractBaseSerializerMixin, GroupAdminSerializer):

    class Meta(GroupAdminSerializer.Meta):
        fields = ('id', 'name', 'users', 'contract')


class ContractClassSerializer(ContractBaseSerializerMixin, CoreClassSerializer):
    pass
