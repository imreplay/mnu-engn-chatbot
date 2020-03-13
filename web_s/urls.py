from django.urls import path
from .views import *

urlpatterns = [
  path('',MainTV.as_view()),
  path('login/',logout_view),
  path('users/',UserLV.as_view()),
  path('reserve/',ReserveLV.as_view()),
]
