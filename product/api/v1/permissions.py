from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from django.contrib.auth.decorators import login_required
from rest_framework.permissions import  BasePermission, SAFE_METHODS

from courses.models import Course
from users.models import Subscription


@api_view(['POST'])
@login_required
def make_payment(request):

    if not request.user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
    course_id = request.data.get('course_id')

    if not course_id:
        return Response({'error': 'Course ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

    balance = request.user.balance

    if balance.amount < course.price:
        return Response({'error': 'Insufficient funds'}, status=status.HTTP_400_BAD_REQUEST)

    with transaction.atomic():

        balance.deduct_money_from_balance(course.price)
        subscription, created = Subscription.objects.get_or_create(user=request.user, course=course)

        if not created:
            return Response({'error': 'You are already subscribed to this course'},
                            status=status.HTTP_400_BAD_REQUEST)

    return Response({'status': 'Payment successful, subscription created'})


class IsStudentOrIsAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return Subscription.objects.filter(user=request.user, course=obj).exists()


class ReadOnlyOrIsAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user.is_staff or request.method in SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.method in SAFE_METHODS
