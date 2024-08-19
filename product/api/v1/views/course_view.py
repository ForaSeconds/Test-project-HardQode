from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response


from api.v1.serializers.course_serializer import (CourseSerializer,
                                                          CreateCourseSerializer,
                                                          CreateGroupSerializer,
                                                          CreateLessonSerializer,
                                                          GroupSerializer,
                                                          LessonSerializer)
from api.v1.serializers.user_serializer import SubscriptionSerializer
from courses.models import Course
from users.models import Subscription

from api.v1.permissions import IsStudentOrIsAdmin, ReadOnlyOrIsAdmin


class LessonViewSet(viewsets.ModelViewSet):
    """Уроки."""

    permission_classes = (IsStudentOrIsAdmin,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return LessonSerializer
        return CreateLessonSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.lessons.all()


class GroupViewSet(viewsets.ModelViewSet):
    """Группы."""

    permission_classes = (permissions.IsAdminUser,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return GroupSerializer
        return CreateGroupSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.groups.all()


class CourseViewSet(viewsets.ModelViewSet):
    """Курсы """

    queryset = Course.objects.all()
    permission_classes = (ReadOnlyOrIsAdmin,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CourseSerializer
        return CreateCourseSerializer

    @action(
        methods=['post'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def pay(self, request, pk):
        """Покупка доступа к курсу (подписка на курс)."""

        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response({'error': 'Курс не найдён'}, status=status.HTTP_404_NOT_FOUND)

        with transaction.atomic():

            request.user.balance.deduct_money_from_balance(course.price)
            subscription, created = Subscription.objects.get_or_create(user=request.user, course=course)

            if not created:
                return Response({'error': 'Вы уже подписаны'}, status=status.HTTP_400_BAD_REQUEST)

            data = {
                'message': 'Платеж прошёл, подписка создана',
                'course_id': course.id,
                'subscription_id': subscription.id,
            }

        return Response(data, status=status.HTTP_201_CREATED)
