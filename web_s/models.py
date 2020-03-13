from django.db import models


# Create your models here.
class User(models.Model):
  class Meta:
    verbose_name = '사용자'
    verbose_name_plural = '사용자 목록'
  def __str__(self):
    return f"{self.department.replace('학과','')} {self.name}"
  check_verify = (
    ('verified', '승인됨'), 
    ('unverified','승인대기'),
  )
  name = models.CharField(max_length=20)
  department = models.TextField()
  s_id = models.CharField(max_length=10, unique=True)
  phone = models.CharField(max_length=20)
  kakao_id = models.TextField(unique=True,default='0')
  verify = models.CharField(max_length=10, default='unverified', choices=check_verify)
  is_admin = models.BooleanField(default=False)

class Reserve(models.Model):
  class Meta:
    ordering = ['start_time']
    verbose_name = '예약'
    verbose_name_plural = '예약 목록'
  def __str__(self):
    return f"{self.start_time.strftime('%m-%d (%H:%M')}~{self.end_time.strftime('%H:%M) ')}/ {self.user}  \
      [{self.reserve_time.strftime('%d일(%a) %H:%M:%S 예약')}]"
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  start_time = models.DateTimeField()
  end_time   = models.DateTimeField()
  reserve_time = models.DateTimeField(auto_now_add=True)