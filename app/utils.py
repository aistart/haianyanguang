# utils.py
import bcrypt
import streamlit as st
import sqlite3
import datetime
from datetime import datetime, timedelta  # 修改此处
import smtplib
from email.mime.text import MIMEText
import smtplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

'''~~~smtp认证使用的邮箱账号密码~~~'''
username='daoootop@aliyun.com'
password = 'BJB!gWPm2NwVuj3'
'''~~~定义发件地址~~~'''
From = formataddr(['daoootop@aliyun.com','daoootop@aliyun.com'])  #昵称(邮箱没有设置外发指定自定义昵称时有效)+发信地址(或代发)
replyto = 'daoootop@aliyun.com'  #回信地址

def send_booking_email(photoSet, name, phone, date, time_slot, remarks):
    '''定义收件对象'''
    to =  ','.join(['aistart@aliyun.com', ''])  #收件人 = 'aistart@aliyun.com'
    cc = ','.join(['', ''])  #抄送
    bcc = ','.join(['', ''])  #密送
    rcptto = [to,cc,bcc]  #完整的收件对象

    '''定义主题'''
    Subject = name+':预约拍照时间'
    
    '''~~~开始构建message~~~'''
    msg = MIMEMultipart('alternative')
    '''1.1 收发件地址、回信地址、Message-id、发信时间、邮件主题'''
    msg['From'] = From
    msg['Reply-to'] = replyto
    msg['TO'] = to
    msg['Cc'] = cc
    # msg['Bcc'] = bcc  #建议密送地址在邮件头中隐藏
    msg['Message-id'] = email.utils.make_msgid()
    msg['Date'] = email.utils.formatdate()
    msg['Subject'] = Subject
    # ''''1.2 正文text/plain部分'''
    # Content = f"\n预约套系： {photoSet}\n\n预约人: {name}\n\n电话/微信: {phone}\n\n日期: {date}\n\n时间段: {time_slot}\n\n\n 登录预约管理系统 https://yuyue.daooo.top/"
    # textplain = MIMEText(Content, _subtype='plain', _charset='UTF-8')
    # msg.attach(textplain)

    '''1.3 正文text/html部分'''
    Content_HTML = f"""<p>预约套系： {photoSet}</p>
                       <p>预约人: {name}</p>
                       <p>电话/微信: {phone}</p>
                       <p>日期: {date}</p>
                       <p>时间段: {time_slot}</p>
                       <p>备注：{remarks}</p>
                       <p><a href="https://yuyue.daooo.top/">登录预约管理系统</a></p>"""
    texthtml = MIMEText(Content_HTML, _subtype='html', _charset='UTF-8')
    msg.attach(texthtml)

    # '''1.3 封装附件'''
    # file = r'C:\Users\yourname\Desktop\某文件夹\123.pdf'   #指定本地文件，请换成自己实际需要的文件全路径。
    # att = MIMEText(open(file, 'rb').read(), 'base64', 'utf-8')
    # att["Content-Type"] = 'application/octet-stream'
    # att.add_header("Content-Disposition", "attachment", filename='123.pdf')
    # msg.attach(att)'

    '''~~~开始连接验证服务~~~'''
    try:
        client = smtplib.SMTP_SSL('smtp.aliyun.com', 465)
        print('smtp_ssl----连接服务器成功，现在开始检查账号密码')
    except Exception as e1:
        client = smtplib.SMTP('smtp.aliyun.com', 25, timeout=5) 
        print('smtp----连接服务器成功，现在开始检查账号密码')
    except Exception as e2:
        print('抱歉，连接服务超时')
        exit(1)
    try:
        client.login(username, password)
        print('账密验证成功')
    except:
        print('抱歉，账密验证失败')
        exit(1)

    '''~~~发送邮件并结束任务~~~'''
    client.sendmail(username, (','.join(rcptto)).split(','), msg.as_string())
    client.quit()
    print('邮件发送成功')


def send_verification_email(userEmail, code):

    '''定义收件对象'''
    to =  ','.join([userEmail, ''])  #收件人 = 'aistart@aliyun.com'
    cc = ','.join(['', ''])  #抄送
    bcc = ','.join(['', ''])  #密送
    rcptto = [to,cc,bcc]  #完整的收件对象

    '''定义主题'''
    Subject = '验证码'
    
    '''~~~开始构建message~~~'''
    msg = MIMEMultipart('alternative')
    '''1.1 收发件地址、回信地址、Message-id、发信时间、邮件主题'''
    msg['From'] = From
    msg['Reply-to'] = replyto
    msg['TO'] = to
    msg['Cc'] = cc
    # msg['Bcc'] = bcc  #建议密送地址在邮件头中隐藏
    msg['Message-id'] = email.utils.make_msgid()
    msg['Date'] = email.utils.formatdate()
    msg['Subject'] = Subject
    ''''1.2 正文text/plain部分'''
    Content = f"\n\n {userEmail} ：\n\n您验证码: {code}\n\n"
    textplain = MIMEText(Content, _subtype='plain', _charset='UTF-8')
    msg.attach(textplain)
    # '''1.3 封装附件'''
    # file = r'C:\Users\yourname\Desktop\某文件夹\123.pdf'   #指定本地文件，请换成自己实际需要的文件全路径。
    # att = MIMEText(open(file, 'rb').read(), 'base64', 'utf-8')
    # att["Content-Type"] = 'application/octet-stream'
    # att.add_header("Content-Disposition", "attachment", filename='123.pdf')
    # msg.attach(att)'

    '''~~~开始连接验证服务~~~'''
    try:
        client = smtplib.SMTP_SSL('smtp.aliyun.com', 465)
        print('smtp_ssl----连接服务器成功，现在开始检查账号密码')
    except Exception as e1:
        client = smtplib.SMTP('smtp.aliyun.com', 25, timeout=5) 
        print('smtp----连接服务器成功，现在开始检查账号密码')
    except Exception as e2:
        print('抱歉，连接服务超时')
        return False
    try:
        client.login(username, password)
        print('账密验证成功')
    except:
        print('抱歉，账密验证失败')
        return False

    '''~~~发送邮件并结束任务~~~'''
    client.sendmail(username, (','.join(rcptto)).split(','), msg.as_string())
    client.quit()
    print('邮件发送成功')
    return True
    
def encrypt_password(password):
    """加密密码"""
    # 将密码转换为字节串，并加密
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password, hashed):
    """验证密码"""
    # 对比提供的密码与存储的哈希值
    return bcrypt.checkpw(password.encode(), hashed)

################# 日志

def log_action(user, action, description):
    """记录用户行为日志"""
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 正确的调用方式
    conn = sqlite3.connect('admin.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO logs (user, action, description, datetime)
        VALUES (?, ?, ?, ?)
    ''', (user, action, description, current_datetime))
    conn.commit()
    conn.close()

def view_logs():
    """从数据库获取并展示日志信息"""
    st.title("查询系统日志")
    st.write("默认从最近显示日志信息。")
    # 日期过滤器
    start_date = st.date_input("开始日期", datetime.now().date())
    end_date = st.date_input("结束日期", datetime.now().date())

    if st.button("检索"):
        if end_date < start_date:
            st.error("结束日期必须大于或等于开始日期。")
        else:
            fetch_logs(start_date, end_date)
    else:
        fetch_logs()

def fetch_logs(start_date=None, end_date=None):
    conn = sqlite3.connect('admin.db')
    cursor = conn.cursor()

    # 根据是否有日期过滤
    if start_date and end_date:
        end_date_inclusive = end_date + timedelta(days=1)
        cursor.execute('''
            SELECT * FROM logs 
            WHERE datetime BETWEEN ? AND ? 
            ORDER BY datetime DESC
        ''', (start_date.strftime("%Y-%m-%d"), end_date_inclusive.strftime("%Y-%m-%d")))
    else:
        cursor.execute('SELECT * FROM logs ORDER BY datetime DESC')

    logs = cursor.fetchall()
    conn.close()

    if logs:
        # 分页显示
        page_size = 30
        total_pages = len(logs) // page_size + (1 if len(logs) % page_size > 0 else 0)
        page_number = st.number_input('选择页码', min_value=1, max_value=total_pages, value=1)
        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size
        for log in logs[start_index:end_index]:
            st.write(log)

    else:
        st.write("No logs found for the selected date range.")
