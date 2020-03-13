from django.urls import path
from .views import *

urlpatterns = [
  path("",MainTV.as_view()),
  path("adduser/", AdduserTV.as_view()),
  path("reserve/", ReserveTV.as_view()),
  path("reserveok/", ReserveOKTV.as_view()),
  path("reserveck/", ReserveCKTV.as_view()),
  path("reservecc/",ReserveCancleTV.as_view()),
  path("checkuser/",Admin_verify.as_view()),
]
