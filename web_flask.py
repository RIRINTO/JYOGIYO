import os
import random
import smtplib
import requests
import configparser
import re
import ssl


from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template, redirect, request, session, escape
from flask.json import jsonify
from flask.helpers import send_file, url_for
from werkzeug.utils import secure_filename
from email.mime.text import MIMEText
from dao.buy import DaoBuy
from dao.category import DaoCategory
from dao.event import DaoEvent
from dao.menu import DaoMenu
from dao.owner import DaoOwner
from dao.notice import DaoNotice
from dao.sys_ques import DaoSysQues
from dao.sys_ans import DaoSysAns
from dao.voc import DaoVoc

daoVoc = DaoVoc()
daoBuy = DaoBuy()
daoCategory = DaoCategory()
daoEvent = DaoEvent()
daoMenu = DaoMenu()
daoNotice = DaoNotice()
daoOwner = DaoOwner()
daoSysQues = DaoSysQues()
daoSysAns = DaoSysAns()

config = configparser.ConfigParser()
config.read("config.ini")

DIR_UPLOAD, KakaoAK, HOST, PORT = config['DIR_UPLOAD']['DIR_UPLOAD'], config['Kakao']['KakaoAK'], config['network']['HOST'], config['network']['PORT']

app = Flask(__name__, static_url_path="", static_folder="static/")
app.secret_key = os.urandom(24)


@app.route('/login')
def main():
    return redirect('login.html')


##################   register ######################

@app.route('/register', methods=['POST'])
def register():
    owner_name = request.form["owner_name"]
    owner_id = request.form["owner_id"]
    owner_pwd = request.form["owner_pwd"]
    owner_str_name = request.form["owner_str_name"]
    owner_str_num = request.form["owner_str_num"].replace("-", "")
    owner_str_tel = request.form["owner_str_tel"]

    owner_add1 = request.form["owner_add1"]
    owner_add2 = request.form["owner_add2"]

    owner_seq = daoOwner.owner_seq_gen()

    logo = request.files["logo"]
    attach_path, attach_file = saveFile(logo, owner_seq)

    try:
        if daoOwner.insert(owner_seq, owner_name, owner_id, owner_pwd, owner_str_name, owner_str_num, owner_str_tel, owner_add1, owner_add2, attach_path, attach_file):
            return redirect("login.html")
    except:
        pass
    return '<script>alert("회원가입에 실패하였습니다.");history.back()</script>'


@app.route('/id_check.ajax', methods=['POST'])
def id_check_ajax():
    owner_id = request.form['owner_id']
    return jsonify({'cnt': daoOwner.id_check(owner_id)})


@app.route('/owner_str_num_check.ajax', methods=['POST'])
def owner_str_num_check_ajax():
    owner_str_num = request.form['owner_str_num'].replace('-', '')
    return jsonify({'cnt': daoOwner.owner_str_num_check(owner_str_num)})


@app.route('/login_form', methods=['POST'])
def login():
    owner_id = request.form["owner_id"]
    owner_pwd = request.form["owner_pwd"]
    obj = daoOwner.select_login(owner_id, owner_pwd)
    
    
    if obj:
        session["owner_seq"] = obj["owner_seq"]
        session["owner_id"] = obj["owner_id"]
        session["admin_yn"] = obj["admin_yn"]
        session["owner_name"] = obj["owner_name"]
        session["logo_path"] = obj["logo_path"]
        session["logo_file"] = obj["logo_file"]
        return redirect('dashboard')
    return "<script>alert('아이디 또는 비밀번호가 일치하지 않습니다.');history.back()</script>"


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login.html')


@app.route('/temp_pwd_send.ajax', methods=['POST'])
def temp_pwd_send_ajax():
    owner_str_num = request.form["owner_str_num"].replace("-", "")
    owner_id = request.form["owner_id"]

    try:
        list = daoOwner.id_check_list(owner_id, owner_str_num)
    except:
        return '0'

    smtpName = "smtp.naver.com"  # smtp 서버 주소
    smtpPort = 587  # smtp 포트 번호

    sendEmail = "hihidaeho@naver.com"
    password = "shingoha2848"
    recvEmail = owner_id

    pwd_list = ['!', '@', '#', '$', '%', '^', '&', '+', '=', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q',
                'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
                'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
    temp = ""
    regPwd = '.*(?=^.{8,15}$)(?=.*\d)(?=.*[a-zA-Z])(?=.*[!@#$%^&+=]).*'
    match = None

    while 1:
        temp = ""
        for _ in range(15):
            match = re.match(regPwd, temp)
            if match:
                break
            temp += pwd_list[random.randint(0, 70)]
        if match:
            break
    print(temp)

    title = "죠기요 임시 비밀번호 발급"  # 메일 제목
    content = list["owner_name"] + "님의 임시 비밀번호는 " + temp + " 입니다. \n로그인 후에 비밀번호를 변경하여 사용하시기 바랍니다."  # 메일 내용

    msg = MIMEText(content)  # MIMEText(text , _charset = "utf8")
    msg['From'] = sendEmail
    msg['To'] = recvEmail
    msg['Subject'] = title

    try:
        s = smtplib.SMTP(smtpName, smtpPort)  # 메일 서버 연결
        s.starttls()  # TLS 보안 처리
        s.login(sendEmail, password)  # 로그인
        s.sendmail(sendEmail, recvEmail, msg.as_string())  # 메일 전송, 문자열로 변환하여 보냅니다.
        s.close()  # smtp 서버 연결을 종료합니다.
    except:
        return '0'

    owner_pwd = temp
    cnt = daoOwner.update_pwd(owner_pwd, owner_id)
    return str(cnt)


##################   dashboard   ######################

@app.route('/')
@app.route('/dashboard')
def dashboard():
    if 'owner_seq' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner_seq'])

    if session['admin_yn'] == 'Y' or session['admin_yn'] == 'y':
        dayschart = daoOwner.dayschart(30)
        monthschart = daoOwner.monthschart(6)
        yearchart = daoOwner.monthschart(12)
        return render_template('web/dashboard/admin_dashboard.html', dayschart=dayschart , monthschart=monthschart, yearschart=yearchart)

    thismonth = datetime.now().strftime("%Y-%m")
    lastmonth = (datetime.now()-relativedelta(months=1)).strftime("%Y-%m")

    menuCntChart_this = daoMenu.menuCntChart(owner_seq, thismonth)
    menuCntChart_last = daoMenu.menuCntChart(owner_seq, lastmonth)
    print(owner_seq)
    print(lastmonth)

    menuSalesChart_this = daoMenu.menuSalesChart(owner_seq, thismonth)
    print(menuSalesChart_this)
    menuSalesChart_last = daoMenu.menuSalesChart(owner_seq, lastmonth)

    salesChart = daoMenu.salesChart(owner_seq,12)
    return render_template('web/dashboard/owner_dashboard.html',
                           menuCntChart_this=menuCntChart_this,
                           menuCntChart_last=menuCntChart_this,
                           menuSalesChart_this=menuSalesChart_this,
                           menuSalesChart_last=menuSalesChart_this,
                           salesChart=salesChart
                           )


@app.route('/account_manage')
def account_manage():
    if 'owner_seq' not in session:
        return redirect('login.html')
    owner_seq = session["owner_seq"]
    obj = daoOwner.select(owner_seq)
    if obj and obj['owner_str_num']:
        owner_str_num = list(obj['owner_str_num'])
        owner_str_num.insert(3, '-')
        owner_str_num.insert(6, '-')
        obj['owner_str_num'] = ''.join(owner_str_num)
    return render_template('web/account/account_manage.html', owner=obj)


@app.route('/account_show')
def account_show():
    if 'owner_seq' not in session:
        return redirect('login.html')
    owner_seq = session["owner_seq"]
    obj = daoOwner.select(owner_seq)
    if obj and obj['owner_str_num']:
        owner_str_num = list(obj['owner_str_num'])
        owner_str_num.insert(3, '-')
        owner_str_num.insert(6, '-')
        obj['owner_str_num'] = ''.join(owner_str_num)
    return render_template('web/account/account_show.html', owner=obj)


@app.route('/account_mod_form', methods=["POST"])
def account_mod_form():
    if 'owner_seq' not in session:
        return redirect('login.html')
    owner_seq = session["owner_seq"]
    owner_name = request.form["owner_name"]
    owner_pwd = request.form["owner_pwd"]
    owner_str_name = request.form["owner_str_name"]
    owner_str_tel = request.form["owner_str_tel"]
    owner_add1 = request.form["owner_add1"]
    owner_add2 = request.form["owner_add2"]
    logo_path = request.form["logo_path"]
    logo_file = request.form["logo_file"]

    logo = request.files["logo"]
    if logo:
        logo_path, logo_file = saveFile(logo)

    try:
        if daoOwner.update(owner_name, owner_pwd, owner_str_name, owner_str_tel, owner_add1, owner_add2, logo_path, logo_file, owner_seq):
            session["owner_seq"] = owner_seq
            session["owner_name"] = owner_name
            session["logo_path"] = logo_path
            session["logo_file"] = logo_file
            return "<script>alert('정보가 수정되었습니다.');location.href='account_show'</script>"
    except:
        pass
    return "<script>alert('정보가 수정되었습니다.');history.back()</script>"


##################   notice   ######################

@app.route('/noti_list')
def noti_list():
    if 'owner_seq' not in session:
        return redirect('login.html')
    admin_yn = escape(session["admin_yn"])
    list = DaoNotice().selectlist()
    return render_template('web/notice/noti_list.html', list=list)


@app.route('/noti_detail')
def noti_detail():
    if 'owner_seq' not in session:
        return redirect('login.html')

    noti_seq = request.args.get('noti_seq')
    obj = DaoNotice().select(noti_seq)
    return render_template('web/notice/noti_detail.html', noti=obj)


@app.route('/noti_add', methods=['POST'])
def noti_add():
    if 'owner_seq' not in session:
        return redirect('login.html')
    
    owner_id = escape(session['owner_id'])
    noti_title = request.form['noti_title']
    noti_content = request.form['noti_content']

    attach_path = ""
    attach_file = ""

    noti_file = request.files['noti_file']
    if noti_file:
        attach_path, attach_file = saveFile(noti_file)

    try:
        cnt = daoNotice.insert(noti_title, noti_content, attach_path, attach_file, owner_id)
        if cnt:
            return redirect('noti_list')
    except:
        pass
    
    return '<script>alert("글 작성에 실패하였습니다.");history.back()</script>'


@app.route('/noti_mod', methods=['POST'])
def noti_mod():
    noti_seq = request.form['noti_seq']
    noti_title = request.form['noti_title']
    noti_content = request.form['noti_content']
    owner_id = escape(session["owner_id"])

    noti_file = request.files['noti_file']
    attach_path = request.form['attach_path']
    attach_file = request.form['attach_file']


    if noti_file:
        attach_path, attach_file = saveFile(noti_file)

    cnt = daoNotice.update(noti_seq, noti_title, noti_content, attach_path, attach_file, owner_id)

    if cnt:
        return redirect("noti_detail?noti_seq=" + noti_seq)
    return '<script>alert("공지사항 수정에 실패하였습니다.");history.back()</script>'


@app.route('/noti_del')
def noti_del():
    noti_seq = request.args.get('noti_seq')

    try:
        cnt = daoNotice.delete(noti_seq)
        if cnt:
            return redirect('noti_list')
    except:
        pass
    return '<script>alert("공지사항 삭제에 실패하였습니다.");history.back()</script>'


@app.route("/noti_del_img.ajax", methods=['POST'])
def noti_del_img():
    noti_seq = request.form['noti_seq']
    cnt = daoNotice.del_img(noti_seq)
    print('cnt', cnt)
    msg = ""
    if cnt == 1:
        msg = "ok"
    else:
        msg = "ng"
    return jsonify(msg=msg)


@app.route('/noti_download')
def noti_download():
    attach_path = request.args.get('attach_path')
    attach_file = request.args.get('attach_file')
    file_name = attach_path + "/" + attach_file

    return send_file(file_name,
                     as_attachment=True)


##################   category   ######################

@app.route('/cate_list')
def cate_list():
    if 'owner_seq' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner_seq'])
    list = daoCategory.selectAll(owner_seq)

    return render_template('web/category/cate_list.html', list=list)


@app.route('/cate_detail')
def cate_detail():
    if 'owner_seq' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner_seq'])
    cate_seq = request.args.get('cate_seq')
    obj = daoCategory.select(owner_seq, cate_seq)
    return render_template('web/category/cate_detail.html', cate=obj)


@app.route('/cate_add', methods=['POST'])
def cate_add():
    if 'owner_seq' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner_seq'])
    cate_name = request.form['cate_name']
    cate_content = request.form['cate_content']
    cate_display_yn = request.form['cate_display_yn']
    attach_path, attach_file = '', ''

    cate_file = request.files['cate_file']
    if cate_file:
        attach_path, attach_file = saveFile(cate_file)

    try:
        cnt = daoCategory.myinsert(owner_seq, cate_name, cate_content, cate_display_yn, attach_path, attach_file)
        if cnt:
            return redirect('cate_list')
    except:
        pass
    return '<script>alert("카테고리 작성에 실패하였습니다.");history.back()</script>'


@app.route('/cate_mod', methods=['POST'])
def cate_mod():
    cate_seq = request.form['cate_seq']
    owner_seq = session['owner_seq']
    cate_name = request.form['cate_name']
    cate_content = request.form['cate_content']
    cate_display_yn = request.form['cate_display_yn']

    cate_file = request.files['cate_file']
    attach_path = request.form['attach_path']
    attach_file = request.form['attach_file']
    print(cate_seq)

    if attach_file == 'None':
        attach_file = ""
        attach_path = ""

    if cate_file:
        attach_path, attach_file = saveFile(cate_file)

    cnt = daoCategory.myupdate(cate_seq, owner_seq, cate_name, cate_content, cate_display_yn, attach_path, attach_file, None, owner_seq, None, owner_seq)

    if cnt:
        return redirect("cate_detail?cate_seq=" + cate_seq)
    return '<script>alert("수정에 실패하였습니다.");history.back()</script>'


@app.route("/cate_del_img.ajax", methods=['POST'])
def cate_del_img():
    cate_seq = request.form['cate_seq']
    cnt = daoCategory.del_img(cate_seq)
    msg = ""
    if cnt == 1:
        msg = "ok"
    else:
        msg = "ng"

    return jsonify(msg=msg)


##################     menu     ######################
@app.route('/menu_list')
def menu_list():
    if 'owner_seq' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner_seq'])
    menu_list = daoMenu.selectAll(owner_seq)
    categoryList = daoCategory.selectYList(owner_seq)
    return render_template('web/menu/menu_list.html', menu_list=menu_list, categoryList=categoryList)


@app.route('/menu_detail')
def menu_detail():
    if 'owner_seq' not in session:
        return redirect('login.html')
    menu_seq = request.args.get('menu_seq')
    owner_seq = escape(session['owner_seq'])
    menu = daoMenu.select(menu_seq, owner_seq)
    if menu.get('owner_seq', '') == session['owner_seq']:
        categoryList = daoCategory.selectYList(owner_seq)
        return render_template('web/menu/menu_detail.html', menu=menu, categoryList=categoryList)
    return '<script>alert("권한이 없습니다.");history.back()</script>'


@app.route('/menu_add_form', methods=['POST'])
def menu_add_form():
    if 'owner_seq' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner_seq'])
    cate_seq = request.form['cate_seq']
    menu_name = request.form['menu_name']
    menu_price = request.form['menu_price']
    menu_content = request.form['menu_content']
    menu_display_yn = request.form['menu_display_yn']
    attach_path = ''
    attach_file = ''

    file = request.files['file']
    if file:
        attach_path, attach_file = saveFile(file)

    try:
        if daoMenu.insert(owner_seq, cate_seq, menu_name, menu_price, menu_content, menu_display_yn, attach_path, attach_file):
            return "<script>alert('성공적으로 추가되었습니다.');location.href='menu_list'</script>"
    except:
        pass

    return "<script>alert('추가에 실패하였습니다.');history.back()</script>"


@app.route('/menu_mod_form', methods=['POST'])
def menu_mod_form():
    if 'owner_seq' not in session:
        return redirect('login.html')
    menu_seq = request.form['menu_seq']
    owner_seq = escape(session['owner_seq'])
    cate_seq = request.form['cate_seq']
    menu_name = request.form['menu_name']
    menu_price = request.form['menu_price']
    menu_content = request.form['menu_content']
    menu_display_yn = request.form['menu_display_yn']
    attach_path = request.form['attach_path']
    attach_file = request.form['attach_file']

    file = request.files['file']
    if file:
        attach_path, attach_file = saveFile(file)

    try:
        if daoMenu.update(cate_seq, menu_name, menu_price, menu_content, menu_display_yn, attach_path, attach_file, owner_seq, menu_seq):
            return f"<script>alert('성공적으로 수정되었습니다.');location.href='menu_detail?menu_seq={menu_seq}'</script>"
    except:
        pass

    return "<script>alert('수정에 실패하였습니다.');history.back()</script>"


##################    event     ######################  
@app.route('/event_list')
def event_list():
    if 'owner_seq' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner_seq'])
    admin_yn = escape(session["admin_yn"])
    list = daoEvent.selectAll(owner_seq)
    return render_template('web/event/event_list.html', list=list)


@app.route('/event_detail')
def event_detail():
    if 'owner_seq' not in session:
        return redirect('login.html')
    owner_seq = escape(session['owner_seq'])
    event_seq = request.args.get('event_seq')
    obj = daoEvent.select(owner_seq, event_seq)
    return render_template('web/event/event_detail.html', event=obj)


@app.route('/event_addact', methods=['POST'])
def event_addact():
    owner_id = escape(session['owner_id'])
    owner_seq = escape(session['owner_seq'])
    event_seq = request.form["event_seq"]
    event_title = request.form["event_title"]
    event_content = request.form["event_content"]
    event_start = request.form["event_start"]
    event_end = request.form["event_end"]
    attach_path = ""
    attach_file = ""
    
    
    event_file = request.files['event_file']
    if event_file:
        attach_path, attach_file = saveFile(event_file)
    try:
        cnt = daoEvent.insert(owner_seq, event_seq, event_title, event_content, event_start, event_end, attach_path, attach_file, None, owner_id, None, owner_id)
        if cnt:
            return redirect('event_list')
    except:
        pass
    return '<script>alert("글 작성에 실패하였습니다.");history.back()</script>'


@app.route('/event_modact', methods=['POST'])
def event_modact():
    owner_id = escape(session['owner_id'])
    owner_seq = escape(session['owner_seq'])
    event_seq = request.form["event_seq"]
    event_title = request.form["event_title"]
    event_content = request.form["event_content"]
    event_start = request.form["event_start"]
    event_end = request.form["event_end"]
    attach_path = request.form['attach_path']
    attach_file = request.form['attach_file']
    event_file = request.files['event_file']

    if attach_file == 'None':
        attach_path = ""
        attach_file = ""

    if event_file:
        attach_path, attach_file = saveFile(event_file)

    try:
        cnt = daoEvent.update(owner_seq, event_seq, event_title, event_content, event_start, event_end, attach_path, attach_file, None, owner_id, None, owner_id)
        if cnt:
            return f'<script>location.href="event_detail?owner_seq={owner_seq}&event_seq={event_seq}"</script>'
    except:
        pass
    return '<script>alert("글 작성에 실패하였습니다.");history.back()</script>'


@app.route("/event_delact")
def event_delact():
    owner_seq = request.args.get("owner_seq")
    event_seq = request.args.get("event_seq")
    try:
        cnt = daoEvent.delete(owner_seq, event_seq)
        if cnt:
            return redirect('event_list')
    except:
        pass
    return '<script>alert("진행중인 이벤트입니다.");history.back()</script>'


@app.route("/event_del.ajax", methods=['POST'])
def event_del_img():
    owner_seq = request.form['owner_seq']
    event_seq = request.form['event_seq']
    cnt = daoEvent.del_img(owner_seq, event_seq)
    msg = ""
    if cnt == 1:
        msg = "ok"
    else:
        msg = "ng"

    return jsonify(msg=msg)


##################    sys_qna     ######################

@app.route('/sys_ques_list')
def sys_ques_list():
    if 'owner_id' not in session:
        return redirect('login.html')
    owner_id = escape(session['owner_id'])
    list = daoSysQues.selectAll(owner_id)
    return render_template('web/sys_ques/sys_ques_list.html', list=list, enumerate=enumerate)


@app.route('/sys_ques_detail')
def sys_ques_detail():
    if 'owner_id' not in session:
        return redirect('login.html')

    sys_ques_seq = request.args.get('sys_ques_seq')
    ques = DaoSysQues().select(sys_ques_seq)
    reply = DaoSysAns().select(sys_ques_seq)
    return render_template('web/sys_ques/sys_ques_detail.html', ques=ques, reply=reply)


@app.route('/sys_ques_add', methods=['POST'])
def sys_ques_add():
    if 'owner_id' not in session:
        return redirect('login.html')
    owner_id = escape(session['owner_id'])
    owner_seq = escape(session['owner_seq'])

    sys_ques_title = request.form["title"]
    sys_ques_content = request.form["content"]
    sys_ques_display_yn = request.form["display_yn"]
    file = request.files['file']

    attach_path = ""
    attach_file = ""

    if file:
        attach_path, attach_file = saveFile(file)
        print("file O")
    else:
        print("file X")

    print(attach_path)
    print(attach_file)
    try:
        if DaoSysQues().insert(owner_seq, sys_ques_title, sys_ques_content, sys_ques_display_yn, attach_path, attach_file, "", owner_id, "", owner_id):
            return "<script>alert('성공적으로 추가되었습니다.');location.href='sys_ques_list'</script>"
    except:
        pass

    return "<script>alert('추가에 실패하였습니다.');history.back()</script>"


@app.route('/sys_ques_mod', methods=['POST'])
def sys_ques_mod():
    if 'owner_id' not in session:
        return redirect('login.html')
    owner_id = escape(session['owner_id'])
    owner_seq = escape(session['owner_seq'])

    sys_ques_seq = request.form["sys_ques_seq"]
    sys_ques_title = request.form["title"]
    sys_ques_content = request.form["content"]
    sys_ques_display_yn = request.form["display_yn"]
    file = request.files["file"]
    attach_path = request.form["attach_path"]
    attach_file = request.form["attach_file"]

    if file:
        attach_path, attach_file = saveFile(file)

    try:
        if DaoSysQues().update(sys_ques_seq, sys_ques_title, sys_ques_content, sys_ques_display_yn, attach_path, attach_file, "", owner_id, "", owner_id):
            return f"<script>alert('성공적으로 수정되었습니다.');location.href='sys_ques_detail?sys_ques_seq={sys_ques_seq}'</script>"
    except:
        pass


#     return redirect(url_for('sys_ques_detail', sys_ques_seq=sys_ques_seq))

@app.route('/sys_ques_del.ajax', methods=['POST'])
def sys_ques_del():
    if 'owner_id' not in session:
        return redirect('login.html')
    sys_ques_seq = request.form['sys_ques_seq']

    DaoSysAns().delete(sys_ques_seq)
    cnt = DaoSysQues().delete(sys_ques_seq)

    msg = ""
    if cnt == 1:
        msg = "ok"
    else:
        msg = "ng"
    return jsonify(msg=msg)


@app.route('/reply_add.ajax', methods=['POST'])
def sys_ans_add():
    if 'owner_id' not in session:
        return redirect('login.html')
    owner_id = escape(session['owner_id'])

    sys_ques_seq = request.form['sys_ques_seq']
    sys_ans_reply = request.form['sys_ans_reply']

    print(sys_ques_seq)
    print(sys_ans_reply)

    try:
        cnt = DaoSysAns().insert(sys_ques_seq, sys_ans_reply, "", owner_id, "", owner_id)
        print(cnt)
    except:
        cnt = 0

    msg = ""
    if cnt == 1:
        msg = "ok"
    else:
        msg = "ng"

    return jsonify(msg=msg)


@app.route('/sys_reply_del.ajax', methods=['POST'])
def sys_reply_del():
    if 'owner_id' not in session:
        return redirect('login.html')
    owner_id = escape(session['owner_id'])
    sys_ques_seq = request.form['sys_ques_seq']
    cnt = DaoSysAns().delete(sys_ques_seq)
    print(cnt)

    msg = ""
    if cnt == 1:
        msg = "ok"
    else:
        msg = "ng"
    return jsonify(msg=msg)


#########################################################

@app.route('/password_change_successful')
def password_change_successful():
    return render_template('web/account/password_change_successful.html')


@app.route('/password_change_failed')
def password_change_failed():
    return render_template('web/account/password_change_failed.html')


@app.route('/kiosk_main')
def k_main():
    return render_template('kiosk/main.html')


@app.route('/kiosk_login', methods=['POST'])
def kiosk_login():
    owner_id = request.form["owner_id"]
    owner_pwd = request.form["owner_pwd"]

    obj = daoOwner.select_login(owner_id, owner_pwd)

    if obj:
        session["owner_seq"] = obj["owner_seq"]
        session["owner_id"] = obj["owner_id"]
        session["admin_yn"] = obj["admin_yn"]
        session["owner_name"] = obj["owner_name"]
        session["owner_str_name"] = obj["owner_str_name"]
        session["logo_path"] = obj["logo_path"]
        session["logo_file"] = obj["logo_file"]
        return redirect('kiosk_home')

    return "<script>alert('아이디 또는 비밀번호가 일치하지 않습니다.');history.back()</script>"


@app.route('/kiosk_home')
def k_home():
    if 'owner_id' not in session:
        return redirect('kiosk_main')
    logo_path = escape(session["logo_path"])
    logo_file = escape(session["logo_file"])
    owner_seq = escape(session["owner_seq"])
    list = daoEvent.selectAll(owner_seq)
    return render_template('kiosk/home.html', logo_path=logo_path, logo_file=logo_file, list=list)


@app.route('/kiosk_menu')
def k_menu():
    if 'owner_id' not in session:
        return redirect('kiosk_main')
    owner_seq = escape(session["owner_seq"])
    logo_path = escape(session["logo_path"])
    logo_file = escape(session["logo_file"])
    cate_list = daoCategory.selectKiosk(owner_seq)
    return render_template('kiosk/menu.html', cate_list=cate_list, logo_path=logo_path, logo_file=logo_file)


@app.route('/select_menu.ajax', methods=["POST"])
def select_menu():
    cate_seq = request.form["cate_seq"]
    try:
        owner_seq = escape(session["owner_seq"])

        menu_list = daoMenu.selectKiosk(owner_seq, cate_seq)
        return jsonify(menu_list=menu_list)
    except:
        pass
    return None


@app.route('/select_menu_by_name.ajax', methods=['POST'])
def owner_seq():
    try:
        owner_seq = escape(session["owner_seq"])
        menu_name = request.form["menu_name"]
        menu_list = daoMenu.selectByName(owner_seq, menu_name)
        return jsonify(menu_list=menu_list)
    except:
        pass
    return None


@app.route('/kiosk_pay_form', methods=["POST"])
def kiosk_pay_form():
    if 'owner_id' not in session:
        return redirect('kiosk_main')
    owner_seq = escape(session['owner_seq'])
    goods = dict(request.form)
    print(goods)

    buyList = {'menu': [], 'buy_seq': daoBuy.genBuySeq(), 'total_price': 0}

    menuList = daoMenu.selectKakao(owner_seq)
    count = 0
    for key, value in goods.items():
        buyList['menu'].append({'menu_seq': int(key.split("_")[1]),
                                'menu_name': menuList[int(key.split("_")[-1])]['menu_name'],
                                'count': int(value),
                                'menu_price': menuList[int(key.split("_")[1])]['menu_price']})
        buyList['total_price'] += menuList[int(key.split("_")[1])]['menu_price'] * int(value)
        count += int(value)
    buy_name = buyList['menu'][0]['menu_name']
    if count - 1:
        buy_name += ' 외 ' + str(count - 1) + '개'

    URL = 'https://kapi.kakao.com/v1/payment/ready'
    headers = {
        'Authorization': "KakaoAK " + KakaoAK,
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    params = {
        "cid": "TC0ONETIME",
        "partner_order_id": buyList['buy_seq'],
        "partner_user_id": "Kiosk",
        "item_name": buy_name,
        "quantity": 1,
        "total_amount": buyList['total_price'],
        "tax_free_amount": 0,
        "approval_url": f"http://127.0.0.1:5004/pay_success",
        "cancel_url": f"http://127.0.0.1:5004/kiosk_home",
        "fail_url": f"http://127.0.0.1:5004/pay_fail",
    }

    res = requests.post(URL, headers=headers, params=params)
    buyList['tid'] = res.json()['tid']  # 결제 승인시 사용할 tid를 세션에 저장
    session['buy'] = buyList
    return redirect(res.json()['next_redirect_pc_url'])


@app.route('/pay_success')
def pay_success():
    buyList = session['buy']
    print(buyList)
    owner_seq = escape(session['owner_seq'])

    URL = 'https://kapi.kakao.com/v1/payment/approve'
    headers = {
        "Authorization": "KakaoAK " + KakaoAK,
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    params = {
        "cid": "TC0ONETIME",  # 테스트용 코드
        "tid": buyList['tid'],  # 결제 요청시 세션에 저장한 tid
        "partner_order_id": buyList['buy_seq'],  # 주문번호
        "partner_user_id": "Kiosk",  # 유저 아이디
        "pg_token": request.args.get("pg_token"),  # 쿼리 스트링으로 받은 pg토큰
    }
    res = requests.post(URL, headers=headers, params=params).json()

    owner = daoOwner.select(escape(session['owner_seq']))

    if owner and owner['owner_str_num']:
        owner_str_num = list(owner['owner_str_num'])
        owner_str_num.insert(3, '-')
        owner_str_num.insert(6, '-')
        owner['owner_str_num'] = ''.join(owner_str_num)

    cnt = daoBuy.insert(buyList['buy_seq'], buyList['menu'], owner_seq)

    return render_template('kiosk/success.html', owner=owner, res=res, buyList=buyList)


@app.route("/kakaopay/cancel", methods=['POST', 'GET'])
def cancel():
    URL = "https://kapi.kakao.com/v1/payment/order"
    headers = {
        "Authorization": "KakaoAK " + KakaoAK,
        "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
    }
    params = {
        "cid": "TC0ONETIME",  # 가맹점 코드
        "tid": session['tid'],  # 결제 고유 코드
    }
    res = requests.post(URL, headers=headers, params=params)
    print(res.text)
    amount = res.json()['cancel_available_amount']['total']

    context = {
        'res': res,
        'cancel_available_amount': amount,
    }

    if res.json()['status'] == "QUIT_PAYMENT":
        res = res.json()
        return render_template('kiosk/cancel.html', params=params, res=res, context=context)


@app.route("/kakaopay/fail", methods=['POST', 'GET'])
def fail():
    return render_template('kiosk/fail.html')


@app.route('/downloads')
def downloads():
    path = request.args.get('path')
    file = request.args.get('file')
    return send_file(path + '/' + file)


def saveFile(file, owner_seq=None):
    if owner_seq:
        attach_path = DIR_UPLOAD + '/' + str(owner_seq)
    else:
        attach_path = DIR_UPLOAD + '/' + escape(session['owner_seq'])
    attach_file = str(datetime.today().strftime("%Y%m%d%H%M%S")) + str(random.random()) + '.' + secure_filename(file.filename).split('.')[-1]
    os.makedirs(attach_path, exist_ok=True)
    file.save(os.path.join(attach_path, attach_file))
    return attach_path, attach_file

###############################voc##############################################
@app.route('/voc_list')
def voc_list():
    if 'owner_seq' not in session:
        return redirect('login.html')
    
    owner_seq = escape(session['owner_seq'])
    list = daoVoc.select(owner_seq)
    return render_template('web/voc/voc_list.html', list=list)

@app.route('/voc_addact', methods=['POST'])
def voc_addact():
    owner_seq = escape(session['owner_seq'])
    content = request.form['content']
    try:
        cnt = daoVoc.insert(owner_seq,content,'','')
        if cnt:
            return redirect("kiosk_menu?owner_seq=" + owner_seq)
    except:
        pass
    return '<script>alert("소리함 작성에 실패하였습니다.");history.back()</script>'



@app.route('/search_menu.ajax', methods=['POST'])
def search_menu_ajax():
    owner_seq = escape(session['owner_seq'])
    msg = request.form['msg']
    menu_list = daoMenu.selectByName(owner_seq,msg)
    return jsonify(menu_list=menu_list)






if __name__ == '__main__':
    # ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    # ssl_context.load_cert_chain(certfile='ssl/root.ca.pem', keyfile='ssl/root.ca.key', password='java')
    # app.run(host=HOST, port=PORT, debug=True, ssl_context=ssl_context)
    app.run(host=HOST, port=PORT, debug=True)
