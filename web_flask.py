import os
import random

from datetime import datetime
from flask import Flask, render_template, redirect, request, session, escape
from flask.json import jsonify
from flask.helpers import send_file, url_for
from werkzeug.utils import secure_filename

from dao.category import DaoCategory
from dao.event import DaoEvent
from dao.menu import DaoMenu
from dao.owner import DaoOwner
from dao.notice import DaoNotice
from dao.sys_ques import DaoSysQues
from dao.sys_ans import DaoSysAns

daoCategory = DaoCategory()
daoEvent = DaoEvent()
daoMenu = DaoMenu()
daoNotice = DaoNotice()
daoOwner = DaoOwner()
daoSysQues = DaoSysQues()
daoSysAns = DaoSysAns()

DIR_UPLOAD = "Z:/uploads"

app = Flask(__name__, static_url_path="", static_folder="static/")
app.secret_key = 'hello'


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
        return render_template('web/dashboard/dashboard.html', obj=obj)
    return "<script>alert('아이디 또는 비밀번호가 일치하지 않습니다.');history.back()</script>"


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login.html')


@app.route('/')
@app.route('/dashboard')
def dashboard():
    if 'owner_seq' not in session:
        return redirect('login.html')
    return render_template('web/dashboard/dashboard.html')


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

    noti_file = request.files['noti_file']
    if noti_file:
        attach_path, attach_file = saveFile(noti_file)
        print('noti_add', attach_path)
        print('noti_add', attach_file)

    try:
        cnt = daoNotice.insert(noti_title, noti_content, attach_path, attach_file, None, owner_id, None, owner_id)
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

    if noti_file == "None":
        attach_path = ""
        attach_file = ""

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
    owner_seq = escape(session['owner_seq'])
    event_seq = request.form["event_seq"]
    event_title = request.form["event_title"]
    event_content = request.form["event_content"]
    event_start = request.form["event_start"]
    event_end = request.form["event_end"]

    event_file = request.files['event_file']
    if event_file:
        attach_path, attach_file = saveFile(event_file)
    try:
        cnt = daoEvent.insert(owner_seq, event_seq, event_title, event_content, event_start, event_end, attach_path, attach_file, None, 'in_user_id', None, 'up_user_id')
        if cnt:
            return redirect('event_list')
    except:
        pass
    return '<script>alert("글 작성에 실패하였습니다.");history.back()</script>'


@app.route('/event_modact', methods=['POST'])
def event_modact():
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
        cnt = daoEvent.update(owner_seq, event_seq, event_title, event_content, event_start, event_end, attach_path, attach_file, None, 'in_user_id', None, 'up_user_id')
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
    return '<script>alert("이벤트 삭제에 실패하였습니다.");history.back()</script>'


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

    list = DaoSysQues().selectAll()
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
    old_attach_path = request.form["attach_path"]
    old_attach_file = request.form["attach_file"]

    attach_path = ""
    attach_file = ""

    if file:
        attach_path, attach_file = saveFile(file)
        print("file O")
    else:
        print("file X")

    cnt = DaoSysQues().update(sys_ques_seq, sys_ques_title, sys_ques_content, sys_ques_display_yn, attach_path, attach_file, "", owner_id, "", owner_id)
    return redirect(url_for('sys_ques_detail', sys_ques_seq=sys_ques_seq))


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


@app.route('/k_main')
def k_main():
    return render_template('kiosk/k_main.html')



@app.route('/kiosk_login', methods=['POST'])
def kiosk_login():
    owner_id = request.form["owner_id"]
    owner_pwd = request.form["owner_pwd"]

    obj = daoOwner.select_login(owner_id,owner_pwd)

    owner_seq = obj["owner_seq"]

    if obj:
        session["owner_seq"] = obj["owner_seq"]
        session["owner_id"] = obj["owner_id"]
        session["admin_yn"] = obj["admin_yn"]
        session["owner_name"] = obj["owner_name"]
        session["logo_path"] = obj["logo_path"]
        session["logo_file"] = obj["logo_file"]
        return redirect('k_home')


    return "<script>alert('아이디 또는 비밀번호가 일치하지 않습니다.');history.back()</script>"


@app.route('/k_home')
def k_home():
    logo_path = escape(session["logo_path"])
    logo_file = escape(session["logo_file"])
    owner_seq = escape(session["owner_seq"])
    list = daoEvent.selectAll(owner_seq)
    return render_template('kiosk/k_home.html',logo_path=logo_path , logo_file=logo_file , list=list)


@app.route('/k_menu')
def k_menu():
    owner_seq = escape(session["owner_seq"])
    logo_path = escape(session["logo_path"])
    logo_file = escape(session["logo_file"])
    cate_list = daoCategory.selectFromKiosk(owner_seq)
    return render_template('kiosk/k_menu.html', cate_list=cate_list, logo_path=logo_path , logo_file=logo_file)


@app.route('/select_menu.ajax', methods=["POST"])
def select_menu():
    cate_seq = request.form["cate_seq"]
    owner_seq = escape(session["owner_seq"])

    try:
        menu_list = daoMenu.selectFromKiosk(owner_seq, cate_seq)
    except:
        pass
    return jsonify(menu_list=menu_list)



@app.route('/kiosk_pay_form', methods=["POST"])
def kiosk_pay_form():
    goods = dict(request.form)
    print(goods)
    return "<script>histoy.back();</script>"





@app.route('/downloads')
def downloads():
    path = request.args.get('path')
    file = request.args.get('file')
    print(path)
    print(file)
    return send_file(path + '/' + file,
                     as_attachment=True)


def saveFile(file, owner_seq=None):
    if owner_seq:
        attach_path = DIR_UPLOAD + '/' + str(owner_seq)
    else:
        attach_path = DIR_UPLOAD + '/' + escape(session['owner_seq'])
    attach_file = str(datetime.today().strftime("%Y%m%d%H%M%S")) + str(random.random()) + '.' + secure_filename(file.filename).split('.')[-1]
    os.makedirs(attach_path, exist_ok=True)
    file.save(os.path.join(attach_path, attach_file))
    return attach_path, attach_file


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
