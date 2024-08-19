from django.contrib import admin
from .models import Balance


@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount')
    readonly_fields = ('user',)
