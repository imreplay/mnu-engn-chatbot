from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import ListView, TemplateView
from django.contrib.auth import logout
from .models import *

# Create your views here.
def logout_view(request):
  logout(request)

class MainTV(TemplateView):
  template_name = 'web_s/main.html'
  def get(self, request, *args, **kwargs):
    ctx = {"message":'<h4>우측 상단의 메뉴를 클릭해주세요.</h4>'}
    return self.render_to_response(ctx)

class UserLV(ListView):
  template_name = 'web_s/user.html'
  context_object_name = 'users'
  model = User

class ReserveLV(ListView):
  template_name = 'web_s/reserve.html'
  context_object_name = 'reserves'
  model = Reserve
  


