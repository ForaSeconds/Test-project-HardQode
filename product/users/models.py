from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.conf import settings

from courses.models import Course


class CustomUser(AbstractUser):
    """Кастомная модель пользователя - студента."""

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=250,
        unique=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id',)

    def __str__(self):
        return self.get_full_name()

    def verify_access_to_course(self, course):
        """Метод проверки доступда к курсу."""
        return Subscription.objects.filter(user=self, course=course).exists()


class Balance(models.Model):
    """Модель баланса пользователя."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                related_name='balance',
                                verbose_name='Пользователь')

    amount = models.PositiveIntegerField(default=1000, verbose_name='Баланс')

    def add_money_in_balance(self, amount):
        """Метод начисления средств на счёт"""

        if self.amount < 0:
            raise ValueError('Сумма не может быть меньше нуля')
        else:
            with transaction.atomic():
                self.amount += amount
                self.save()

    def verifi_money_in_balance(self, amount):
        """Метод верификации баланса"""

        if self.amount < 0:
            raise ValueError('Сумма не может быть меньше нуля')
        elif self.amount > 0:
            raise ValueError('Недостаточнро средств')
        with transaction.atomic():
            self.amount -= amount
            self.save()


    class Meta:
        verbose_name = 'Баланс'
        verbose_name_plural = 'Балансы'
        ordering = ('-id',)

    def __str__(self):
        return f"{self.user.get_full_name()} - Ваш баланс: {self.amount} бонусов"


class Subscription(models.Model):
    """Модель подписки пользователя на курс."""

    user = models.ForeignKey(CustomUser,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь')

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name='Курс'
    )

    subscription_date = models.DateField(
        auto_now_add=True,
        verbose_name='Дата подписки'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-subscription_date',)
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user} подписан на {self.course}"
