import streamlit as st
import sqlite3
import datetime
# from datetime import datetime,date,timedelta
import random
import string
from .yuyue_database import create_connection
from .utils import view_logs,log_action
from .user import photography_packages
import uuid



admin_email  = ""
def edit_and_delete_appointment_form(appointment, selected_date, time_slot, context):
    appointment_id, customer_name, appointment_date, appointment_time, package, contact_info, remarks = appointment

    unique_id = uuid.uuid4()  # 生成唯一标识符
    delete_save_key = f"delete_save_{time_slot}_{context}_{appointment_id}"
    delete_key = f"delete_{time_slot}_{context}_{appointment_id}"
    save_key = f"save_{time_slot}_{context}_{appointment_id}"

    # 使用 appointment_id 和字段名称创建唯一的 session_state 键
    session_keys = {
        'package': f"edited_package_{time_slot}_{context}_{appointment_id}",
        'contact_info': f"edited_contact_info_{time_slot}_{context}_{appointment_id}",
        'remarks': f"edited_remarks_{time_slot}_{context}_{appointment_id}"
    }

    # 初始化 session_state
    if not st.session_state.get(session_keys['package']):
        st.session_state[session_keys['package']] = package
    if not st.session_state.get(session_keys['contact_info']):
        st.session_state[session_keys['contact_info']] = contact_info
    if not st.session_state.get(session_keys['remarks']):
        st.session_state[session_keys['remarks']] = remarks

    # 渲染输入框并更新 session_state
    edited_package = st.text_input("套系", value=st.session_state[session_keys['package']], key=f"package_{time_slot}_{context}_{appointment_id}")
    st.session_state[session_keys['package']] = edited_package

    edited_contact_info = st.text_input("联系方式", value=st.session_state[session_keys['contact_info']], key=f"contact_{time_slot}_{context}_{appointment_id}")
    st.session_state[session_keys['contact_info']] = edited_contact_info

    edited_remarks = st.text_input("备注", value=st.session_state[session_keys['remarks']], key=f"remarks_{time_slot}_{context}_{appointment_id}")
    st.session_state[session_keys['remarks']] = edited_remarks
    
    new_appointment_date = selected_date
    new_appointment_time = time_slot

    # 添加日期和时间段选择器
    time_slots = ["09:00-11:00", "11:00-13:00", "13:00-15:00", "15:00-17:00", "17:00-19:00"]


    if st.button('删除或修改此预约', key=delete_save_key):
        st.session_state[f'delete_save_clicked_{delete_save_key}'] = True

    if st.session_state.get(f'delete_save_clicked_{delete_save_key}', False):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("确认删除预约", key=delete_key):
                delete_appointment(appointment_id, edited_package, customer_name, edited_contact_info, new_appointment_date, new_appointment_time, edited_remarks)
                st.session_state[f'delete_save_clicked_{delete_save_key}'] = False
                return  # 结束函数执行

        with col2:
            new_appointment_date = st.date_input(f"如修改日期,请选择：", datetime.datetime.strptime(appointment_date, '%Y-%m-%d').date(), key=f'fix_appointment_date_{delete_save_key}')
            new_appointment_time = st.selectbox("如修改时间段，请选择", options=time_slots, index=time_slots.index(appointment_time), key=f'fix_appointment_time_{delete_save_key}')
            
            if st.button("确认保存修改", key=save_key):
                # 直接使用 session_state 中的值
                updated_package = st.session_state[session_keys['package']]
                updated_contact_info = st.session_state[session_keys['contact_info']]
                updated_remarks = st.session_state[session_keys['remarks']]

                # 调用 update_appointment 函数
                update_appointment(appointment_id, updated_package, customer_name, updated_contact_info, new_appointment_date, new_appointment_time, updated_remarks)
                st.session_state[f'delete_save_clicked_{delete_save_key}'] = False
                return  # 结束函数执行


# 登录后显示当前的预约情况：
def view_appointments():
    conn = create_connection()
    cursor = conn.cursor()

    st.subheader("选择日期查看预约")

    # 设置默认值为当天的日期
    today =datetime.date.today()
    three_months_later = today + datetime.timedelta(days=90)
    selected_date = st.date_input("选择日期", value=today)

    initialize_time_slots(today.strftime("%Y-%m-%d"), three_months_later.strftime("%Y-%m-%d"))


    # 确保 selected_date 是字符串类型
    if not isinstance(selected_date, str):
        selected_date = str(selected_date)

    # 使用元组传递参数
    cursor.execute("SELECT time_slot, is_open FROM date_time_slots WHERE date = ?", (selected_date,))
    time_slots = cursor.fetchall()

    for slot in time_slots:
        time_slot, is_open = slot

        cursor.execute("SELECT * FROM appointments WHERE appointment_date = ? AND appointment_time = ?", (selected_date, time_slot))
        appointments = cursor.fetchall()
        # has_appointments = len(appointments) > 0

        # with st.expander(f"时间段：{time_slot}，共{len(appointments)}条预约", expanded=has_appointments):
        with st.expander(f"时间段：{time_slot}，共{len(appointments)}条预约"):
            # 使用日期和时间段的组合作为唯一的 key
            is_open_checkbox = st.checkbox("此时段可预约（去掉✔后，用户无法约）", value=is_open, key=f"open_{selected_date}_{time_slot}")


            for index, appointment in enumerate(appointments, start=1):
                st.markdown(f"**{index}.  {appointment[1]} 已预约：**")

                edit_and_delete_appointment_form(appointment, selected_date, appointment[3], context='view_appointments')

                
            # 更新可预约状态
            if is_open_checkbox != is_open:
                cursor.execute("REPLACE INTO date_time_slots (date, time_slot, is_open) VALUES (?, ?, ?)", (selected_date, time_slot, is_open_checkbox))
                conn.commit()
                log_action("admin", "__更新可预约状态__", f"__日期{selected_date},时段{time_slot}状态{is_open_checkbox}__")
    conn.close()

def add_new_appointment_form():
    st.subheader("新增用户预约信息")

    # 创建套系选择列表
    package_options = [f"{package['serial']}. {package['title']}" for package in photography_packages]

    # Initialize Session State Variables
    if 'new_customer_name' not in st.session_state:
        st.session_state['new_customer_name'] = ""

    if 'new_package' not in st.session_state:
        st.session_state['new_package'] = package_options[0]  # Assuming package_options is defined earlier

    if 'new_contact_info' not in st.session_state:
        st.session_state['new_contact_info'] = ""

    if 'new_remarks' not in st.session_state:
        st.session_state['new_remarks'] = ""

    if 'new_appointment_date' not in st.session_state:
        st.session_state['new_appointment_date'] = datetime.date.today()

    if 'new_appointment_time' not in st.session_state:
        st.session_state['new_appointment_time'] = "09:00-11:00"

    if 'form_submitted' not in st.session_state:
        st.session_state['form_submitted'] = False

    # Your existing code that updates session state variables conditionally
    if st.session_state['form_submitted']:
        # Here, you can reset the values after form submission, if needed
        st.session_state['new_customer_name'] = ""
        st.session_state['new_package'] = package_options[0]
        st.session_state['new_contact_info'] = ""
        st.session_state['new_remarks'] = ""
        st.session_state['new_appointment_date'] = datetime.date.today()
        st.session_state['new_appointment_time'] = "09:00-11:00"
        st.session_state['form_submitted'] = False

    # 创建表单
    with st.form(key="new_appointment_form"):
        new_customer_name = st.text_input("用户姓名", value=st.session_state['new_customer_name'], key='new_customer_name')
        new_package = st.selectbox("选择套系", options=package_options, index=package_options.index(st.session_state['new_package']), key='new_package')
        new_contact_info = st.text_input("联系方式", value=st.session_state['new_contact_info'], key='new_contact_info')
        new_remarks = st.text_input("备注", value=st.session_state['new_remarks'], key='new_remarks')
        new_appointment_date = st.date_input("预约日期", value=st.session_state['new_appointment_date'], key='new_appointment_date')
        new_appointment_time = st.selectbox("时间段", options=["09:00-11:00", "11:00-13:00", "13:00-15:00", "15:00-17:00", "17:00-19:00"], index=["09:00-11:00", "11:00-13:00", "13:00-15:00", "15:00-17:00", "17:00-19:00"].index(st.session_state['new_appointment_time']), key='new_appointment_time')

        submit_button = st.form_submit_button(label="保存新预约")

    if submit_button:
        # 保存逻辑
        state = add_new_appointment(new_package, new_customer_name, new_contact_info, new_appointment_date, new_appointment_time, new_remarks)
        if state:
            st.success("已新增一条预约信息。刷新页面，可见最新预约信息。")
            st.session_state['form_submitted'] = True  # 设置表单提交状态为 True



def update_appointment(appointment_id, package, customer_name, contact_info, selected_date, selected_time, remarks):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE appointments SET package = ?, customer_name = ?, contact_info = ?, appointment_date = ?, appointment_time = ?, special_requirements = ? WHERE id = ?", (package, customer_name, contact_info, selected_date, selected_time, remarks, appointment_id))
    conn.commit()
    conn.close()
    log_action("admin", "__更新预约内容__", f"__套系{package},用户名称{customer_name},电话/微信{contact_info},日期{selected_date},时段{selected_time}备注{remarks}__索引号{appointment_id}__")
    st.success("预约信息已更新。")


def delete_appointment(appointment_id, package, customer_name, contact_info, selected_date, selected_time, remarks):
    conn = create_connection()
    cursor = conn.cursor()
    # 执行删除操作
    cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
        # 可以选择在此处添加一个成功删除的消息
    st.success(f" 已成功删除。")
    conn.commit()
    conn.close()
    log_action("admin", "__删除预约__",  f"__套系{package},用户名称{customer_name},电话/微信{contact_info},日期{selected_date},时段{selected_time}备注{remarks}__索引号{appointment_id}__")


def add_new_appointment( package, customer_name,  contact_info, selected_date,selected_time, remarks):

    # 获取当前日期和时间
    current_datetime = datetime.datetime.now()

    # 检查用户姓名或联系方式是否为空
    if not customer_name or not contact_info:
        st.error("需要填写用户姓名和联系方式")
        return False  # 直接返回，不执行后续的添加预约操作

    # 检查选择的日期和时间是否小于当前日期和时间
    selected_datetime = datetime.datetime.combine(selected_date, datetime.datetime.strptime(selected_time.split('-')[0], '%H:%M').time())
    if selected_datetime <= current_datetime:
        st.error("预约应在当前日期和时间之后")
        return False
    
    conn = create_connection()
    cursor = conn.cursor()

    # 检查是否已有相同联系方式的预约
    cursor.execute("SELECT * FROM appointments WHERE contact_info = ? AND appointment_date = ? AND appointment_time = ?", (contact_info, selected_date, selected_time))
    existing_appointment = cursor.fetchone()

    if not existing_appointment:
    # 添加预约到数据库
        cursor.execute("INSERT INTO appointments (customer_name, contact_info, appointment_date, appointment_time, package, special_requirements) VALUES (?, ?, ?, ?, ?, ?)", ( customer_name,  contact_info, selected_date,selected_time, package, remarks))
        conn.commit()
        log_action("admin", "__添加预约内容__", f"__套系{package},用户名称{customer_name},电话/微信{contact_info},日期{selected_date},时段{selected_time}备注{remarks}__")
        print("New appointment saved:", package, customer_name, contact_info, selected_date, selected_time)  # 调试信息
        conn.close()
        return True
    else:
        print("Appointment already exists for:", customer_name, contact_info, selected_date, selected_time)  # 调试信息
        st.error("相同联系方式的用户已有预约")
        conn.close()
        return False

    

def view_recent_appointments_summary():
    conn = create_connection()
    cursor = conn.cursor()

    # 获取当前日期和时间
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    current_time = datetime.datetime.now().strftime("%H:%M")

    # 查询数据库以获取当前时间之后的最新5个预约
    cursor.execute("""
    SELECT * FROM appointments 
    WHERE (appointment_date > ?) OR (appointment_date = ? AND appointment_time >= ?)
    ORDER BY appointment_date ASC, appointment_time ASC 
    LIMIT 10""", (current_date, current_date, current_time))

    recent_appointments = cursor.fetchall()

    st.subheader("最近10条预约信息：")
    for appointment in recent_appointments:
        with st.expander(f"{appointment[2]}, {appointment[3]} ：{appointment[1]}"):
            edit_and_delete_appointment_form(appointment, appointment[2], appointment[3], context='view_recent')

    conn.close()



def admin_dashboard():
    st.title("海岸阳光摄影●预约管理")

    # 将英文周几映射到中文
    weekday_mapping = {
        'Monday': '一',
        'Tuesday': '二',
        'Wednesday': '三',
        'Thursday': '四',
        'Friday': '五',
        'Saturday': '六',
        'Sunday': '日'
    }

    # 获取今天的日期
    current_date = datetime.date.today()
    # 获取当前的日期和时间
    current_datetime = datetime.datetime.now()
    # 获取今天是周几，然后用中文表示
    today_weekday = weekday_mapping[current_datetime.strftime('%A')]

    # 格式化当前时间为小时和分钟
    current_time = current_datetime.strftime('%H:%M')

    st.write(f"当前：{current_date.strftime('%m月%d号(')}周{today_weekday}) {current_time}")
    
    # 显示最近5次预约概要
    view_recent_appointments_summary()

    # 显示所选日期的预约信息
    view_appointments()

    # 显示所选日期的预约信息
    add_new_appointment_form()


def initialize_time_slots(start_date, end_date):
    conn = sqlite3.connect('admin.db')
    cursor = conn.cursor()

    time_slots = ["09:00-11:00", "11:00-13:00", "13:00-15:00", "15:00-17:00", "17:00-19:00"]
    start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    date_generated = [start + datetime.timedelta(days=x) for x in range(0, (end-start).days + 1)]

    for date in date_generated:
        formatted_date = date.strftime("%Y-%m-%d")
        for slot in time_slots:
            cursor.execute("INSERT OR IGNORE INTO date_time_slots (date, time_slot, is_open) VALUES (?, ?, ?)", (formatted_date, slot, True))

    conn.commit()
    conn.close()




