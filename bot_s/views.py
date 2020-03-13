from django.shortcuts import render
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from web_s.models import *
import json
import datetime

# Create your views here.
class MainTV(TemplateView):
  template_name = 'web_s/main.html'
  def get(self, request, *args, **kwargs):
    ctx = {"message":'Don\'t Use....'}
    return self.render_to_response(ctx)

class AdduserTV(TemplateView):
  template_name = 'bot_s/simple_text.html'
  @method_decorator(csrf_exempt)
  def dispatch(self, request, *args, **kwargs):
    return super(AdduserTV, self).dispatch(request, *args, **kwargs)
  def post(self, request, **kwargs):
    data = json.loads(request.body)
    if data['userRequest']['block']['id']=="5da47aaa92690d0001a47c4d":
      context = {'message':''}
      if User.objects.filter(kakao_id=data['userRequest']['user']['id']):
        context['message'] = "이미 가입되어있습니다."
      else:
        context['message'] ="안녕하세요. \\n공과대학 풋살장의 원활한 예약시스템을 위해 사용자의 정보를 저장 후 예약 서비스를 제공하고 있습니다. \\n본 서비스를 통해 수집되는 개인정보는\\n[이름, 학번, 연락처, 학과]이며, \\n서비스 사용기간동안 저장 됩니다.\\n사용자 등록을 원하실 경우\\n[진행] 버튼을 눌러주세요."
        context['quickReplies'] = {'label':'진행','message':'진행','action':'block','b_id':'5da47985b617ea00012b3829'}
      return self.render_to_response(context)

    else:
      data = data['action']['params']
      ck_user = User.objects.filter(s_id=data['s_id'])
      if(ck_user):
        msg = "이미 존재하는 사용자입니다."
      else:
        user, flag = User.objects.get_or_create(
          name=data['name'],
          department=data['department'],
          s_id=data['s_id'],
          phone=data['phone'],
          kakao_id= json.loads(request.body)['userRequest']['user']['id']
        )
        msg = "사용자 생성을 완료하였습니다.\\n관리자 승인후 정상적인 서비스 이용이 가능합니다."

    context = {'message':f'{msg}'}
    return self.render_to_response(context)

class ReserveTV(TemplateView):
  template_name = 'bot_s/simple_text_multi.html'
  @method_decorator(csrf_exempt)
  def dispatch(self, request, *args, **kwargs):
    return super(ReserveTV, self).dispatch(request, *args, **kwargs)
  def check_day(self):
    possible_day = [0,1,2,3,4,5,6] #mon:0 - sun:6
    return datetime.datetime.today().weekday() in possible_day
  def get_next_week(self):
    today = datetime.date.today()
    start_day = today - datetime.timedelta(days=today.weekday())+ datetime.timedelta(days=7)
    end_day = start_day + datetime.timedelta(days=7)
    return [start_day, end_day]
  def get_reserve(self):
    datas = Reserve.objects.filter(start_time__range=self.get_next_week(), end_time__range=self.get_next_week())
    msg = ''
    weekday_list = ['월', '화','수','목','금','토','일']
    for data in datas:
      msg += f"[{weekday_list[data.start_time.weekday()]}]"
      msg += f"{data.start_time.strftime('%m-%d (%H:%M')}~{data.end_time.strftime('%H:%M) ')}/{data.user.department}\\n"
    if not msg:
      msg="[예약 내역이 없습니다.]\\n"
    return msg
  def post(self, request, **kwargs):
    data = json.loads(request.body)
    context = {'message':''}
    if not self.check_day(): 
      context['message'] = "오늘은 예약이 불가능 합니다. \\n[토,일] 요일에 다시 시도해주세요."
      return self.render_to_response(context)
    user = User.objects.filter(kakao_id=data['userRequest']['user']['id'])
    if user:
      #승인기능 
      # if user[0].verify == 'unverified':
      #   context['message'] = "승인 대기중인 사용자입니다."
      #   return self.render_to_response(context)

      resv = self.get_reserve().replace("학과",'')
      context['message'] = f'[{user[0].name}]님 안녕하세요.\\n현재 예약 현황입니다.\\n\\n{resv}\\n'
      context['message'] += f'\\n예약하실 요일을 선택해주세요.'
      context['quickReplies'] = []
      weekday_list = ['월', '화','수','목','금','토','일']
      for i,weekday in  enumerate(weekday_list):
        s_day = self.get_next_week()[0]
        context['quickReplies'].append({'label':weekday,'message':f'{weekday}요일({str(s_day+datetime.timedelta(days=i))[5:]})','action':'block','b_id':'5e68b8e0fa22f5000120e939'})
    else:
      context['message'] = f'사용자 등록이 되어있지 않습니다.\\n'
      context['quickReplies'] = [{'label':'사용자등록','message':'사용자등록','action':'block','b_id':'5da47aaa92690d0001a47c4d'}]
    return self.render_to_response(context)

class ReserveOKTV(TemplateView):
  template_name = 'bot_s/simple_text.html'
  @method_decorator(csrf_exempt)
  def dispatch(self, request, *args, **kwargs):
    return super(ReserveOKTV, self).dispatch(request, *args, **kwargs)
  def time_setting(self, times):
    for i,t in enumerate(times):
      if ':' in t:
        times[i] = list(map(int,t.split(":")))
        if t.count(":")>1:
          return -1
        
      else:
        t += ":00"
        times[i] = list(map(int,t.split(":")))
    return times
  def check_time(self,times): #times -> [start_time, end_time]
    for t in times: #시간 형식 체크
      if t[0]>=24 or t[1]>60 or t[0]<8:
        return "시간이 올바르지 않습니다."
    if datetime.timedelta(hours=times[1][0],minutes=times[1][1])-datetime.timedelta(hours=times[0][0],minutes=times[0][1]) > datetime.timedelta(seconds=7200):
      #예약시간이 2시간 초과하면 예약 불가
      return "예약은 2시간까지 가능합니다."
    elif datetime.timedelta(hours=times[1][0],minutes=times[1][1])-datetime.timedelta(hours=times[0][0],minutes=times[0][1]) < datetime.timedelta(minutes=20): 
      return "예약시간이 너무 짧습니다."
    return "OK"
  def post(self, request, **kwargs):
    data = json.loads(request.body)

    context = {'message':''}
    if not ReserveTV.check_day(self): 
      context['message'] = "오늘은 예약이 불가능 합니다. \\n[토,일] 요일에 다시 시도해주세요."
      return self.render_to_response(context)
    req_m,req_d = data['userRequest']['utterance'].split("(")[1][:-1].split("-")
    try:
      req_st = data['action']['params']['start_time'] #11 or 11:30
      req_et = data['action']['params']['end_time']   #11 or 11:30
      req_st,req_et = self.time_setting([req_st,req_et]) #['11','00'] or ['11','30']
    except Exception as e:
      context['message'] = "숫자 또는 : 문자(1개)만 입력할 수 있습니다."
      return self.render_to_response(context)
    if self.check_time([req_st,req_et]) != "OK":
      context['message'] = f"[Error] - {self.check_time([req_st,req_et])}\\n예약을 다시 진행해주세요."
      return self.render_to_response(context)

    st = datetime.datetime(year=datetime.datetime.today().year, month=int(req_m),day=int(req_d),hour=req_st[0],minute=req_st[1])
    et = datetime.datetime(year=datetime.datetime.today().year, month=int(req_m),day=int(req_d),hour=req_et[0],minute=req_et[1])
    one_sec = datetime.timedelta(seconds=1)
    resv = Reserve.objects.filter(Q(start_time__range=[st,et-one_sec])|Q(end_time__range=[st+one_sec,et]))
    if resv.exists():
      msg = resv[0].start_time.strftime('%m-%d (%H:%M ~')
      msg += resv[0].end_time.strftime('%H:%M) ')
      msg += resv[0].user.department.replace("학과","")
      context['message']=f'이미 예약이 되어있는 시간입니다.\\n{msg}\\n예약을 다시 진행해주세요.'
    else:
      user = User.objects.get(kakao_id=data['userRequest']['user']['id'])
      Reserve.objects.create(user=user,start_time=st,end_time=et)
      context['message']=f'{req_st[0]:02d}:{req_st[1]:02d}~{req_et[0]:02d}:{req_et[1]:02d} / {user.department[:-2]}\\n\\n예약이 완료되었습니다.\\n감사합니다.'

    return self.render_to_response(context)

class ReserveCKTV(TemplateView):
  template_name = 'bot_s/simple_text_multi.html'
  @method_decorator(csrf_exempt)
  def dispatch(self, request, *args, **kwargs):
    return super(ReserveCKTV, self).dispatch(request, *args, **kwargs)
  def get_next_week(self,flag):
    today = datetime.date.today()
    start_day = today - datetime.timedelta(days=today.weekday())
    if flag =="Next":
      start_day += datetime.timedelta(days=7)
    end_day = start_day + datetime.timedelta(days=7)
    return [start_day, end_day]
  def get_reserve(self,flag):
    datas = Reserve.objects.filter(start_time__range=self.get_next_week(flag), end_time__range=self.get_next_week(flag))
    msg = ''
    weekday_list = ['월', '화','수','목','금','토','일']
    for data in datas:
      msg += f"[{weekday_list[data.start_time.weekday()]}]"
      msg += f"{data.start_time.strftime('%m-%d (%H:%M')}~{data.end_time.strftime('%H:%M) ')}/{data.user.department}\\n"
    if not msg:
      msg="[예약 내역이 없습니다.]\\n"
    return msg  
  def post(self, request, **kwargs):
    data = json.loads(request.body)
    context = {'message':''}
    if "주" not in data['userRequest']['utterance']:
      context['message'] = "예약현황을 조회합니다.\\n어느 주의 예약 현황을 확인할까요?"
      context['quickReplies'] = [
        {'label':'이번주','message':'이번주','action':'block','b_id':'5da47cc48192ac00011589bf'},
        {'label':'다음주','message':'다음주','action':'block','b_id':'5da47cc48192ac00011589bf'}
      ]
      return self.render_to_response(context)
    flag = ""
    if data['userRequest']['utterance']=="다음주":
      flag = "Next"
    resv = self.get_reserve(flag=flag).replace("학과",'')
    context = {'message':''}
    context['message'] = f"{data['userRequest']['utterance']} 예약 현황입니다.\\n\\n{resv}"
    return self.render_to_response(context)

class ReserveCancleTV(TemplateView):
  template_name = 'bot_s/simple_text_multi.html'
  @method_decorator(csrf_exempt)
  def dispatch(self, request, *args, **kwargs):
    return super(ReserveCancleTV, self).dispatch(request, *args, **kwargs)

  def post(self, request, **kwargs):
    data = json.loads(request.body)
    context = {'message':''}  
    user = User.objects.filter(kakao_id=data['userRequest']['user']['id'])
    if not user.exists():
      context['message'] = "등록되지 않은 사용자입니다."
      return self.render_to_response(context)
    resv = Reserve.objects.filter(user=user[0])
    if "번"in data['userRequest']['utterance']:
      n = int(data['userRequest']['utterance'][:1])
      resv[n-1].delete()
      context['message'] = "정상적으로 취소되었습니다."
      return self.render_to_response(context)
    msg = ''
    weekday_list = ['월', '화','수','목','금','토','일']
    for i,data in enumerate(resv):
      msg += f"{i+1})[{weekday_list[data.start_time.weekday()]}]"
      msg += f"{data.start_time.strftime('%m-%d (%H:%M')}~{data.end_time.strftime('%H:%M) ')}/{data.user.department}\\n"
    if not msg:
      msg="[예약 내역이 없습니다.]\\n"
    context['message'] = f"[{user[0].name}]님의 예약 내역입니다.\\n{msg}어느것을 취소하시겠습니까?"
    context['quickReplies'] = []
    for i in range(resv.count()):
      context['quickReplies'].append({'label':f'{i+1}번','message':f'{i+1}번','action':'block','b_id':'5e68eaa87bf6580001b0e850'})
    return self.render_to_response(context)

class Admin_verify(TemplateView):
  template_name = 'bot_s/simple_text_multi.html'
  @method_decorator(csrf_exempt)
  def dispatch(self, request, *args, **kwargs):
    return super(Admin_verify, self).dispatch(request, *args, **kwargs)
  def post(self, request, **kwargs):
    data = json.loads(request.body)
    context = {'message':''}  
    user = User.objects.filter(kakao_id=data['userRequest']['user']['id'])
    if not user[0].is_admin:
      context['message'] = "잘못된 접근입니다."
      return self.render_to_response(context)

    users = User.objects.filter(verify='unverified')
    if data['userRequest']['block']['id']=="5e68fcbfa47f190001b18ff6":
      no_list = data['action']['params']['id'].strip().split(" ")
      for i,u in enumerate(users):
        if str(i+1) in no_list:
          pass
        else:
          u.verify='verified'
          u.save()
      context['message'] = f"{users.count()-len(no_list)}명의 사용자를 승인하였습니다."
      return self.render_to_response(context) 
    if "모두" in data['userRequest']['utterance']:
      users.update(verify='verified')
      context['message'] = f"모든 사용자를 승인하였습니다."
      return self.render_to_response(context)
    for i,u in enumerate(users):
      context['message'] += f"{i+1}) {u.name}({u.s_id})/{u.department}/{u.phone}\\n"
    context['quickReplies'] = [
      {'label':'모두 승인하기','message':'모두 승인하기','action':'block','b_id':'5e67cfa15555e4000156b5cd'},
      {'label':'일부 사용자 제외하기','message':'일부 사용자 제외하기','action':'block','b_id':'5e68fcbfa47f190001b18ff6'}
    ]
    if context['message'] == "":
      context['message'] = "승인되지 않은 사용자가 없습니다."
      context['quickReplies']=""
    return self.render_to_response(context)

