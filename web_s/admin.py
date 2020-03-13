from django.contrib import admin
from .models import *
# Register your models here.

class User_admin(admin.ModelAdmin):
  actions = ['verify_users','unverify_users']
  list_display = ['name','department','s_id','phone','verify']
  search_fields =['name','department','s_id','phone','verify']
  list_filter = ('department','verify')

  def verify_users(self, request, queryset):
    updated_user = queryset.update(verify='verified')
    self.message_user(request, f'{updated_user}명의 사용자를 승인하였습니다.')

  def unverify_users(self, request, queryset):
    updated_user = queryset.update(verify='unverified')
    self.message_user(request, f'{updated_user}명의 사용자를 승인대기상태로 전환하였습니다.')

  verify_users.short_description = '선택한 사용자를 모두 승인'
  unverify_users.short_description = '선택한 사용자를 모두 승인대기상태 전환'

class Reserve_admin(admin.ModelAdmin):
  search_fields = ['user']

admin.site.register(User, User_admin)
admin.site.register(Reserve)