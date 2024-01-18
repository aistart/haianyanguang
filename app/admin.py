import streamlit as st
import sqlite3
import datetime
from datetime import datetime,date,timedelta
import random
import string
from .yuyue_database import create_connection
from .utils import view_logs,log_action



admin_email  = ""

def edit_and_delete_appointment_form(appointment, selected_date, time_slot, context=''):
    appointment_id, customer_name, appointment_date, appointment_time, package, contact_info, remarks = appointment

    # 修改按钮的 key 参数，加入 context 字符串以确保唯一性
    delete_save_key = f"delete_save_{context}_{appointment_id}"
    delete_key = f"delete_{context}_{appointment_id}"
    save_key = f"save_{context}_{appointment_id}"

    edited_package = st.text_input("套系", value=package, key=f"package_{context}_{appointment_id}")
    edited_contact_info = st.text_input("联系方式", value=contact_info, key=f"contact_{context}_{appointment_id}")
    edited_remarks = st.text_input("备注", value=remarks, key=f"remarks_{context}_{appointment_id}")

    if f'delete_save_clicked_{delete_save_key}' not in st.session_state:
        st.session_state[f'delete_save_clicked_{delete_save_key}'] = False

    if st.button('删除此预约或已完成修改', key=delete_save_key):
        st.session_state[f'delete_save_clicked_{delete_save_key}'] = True

    if st.session_state[f'delete_save_clicked_{delete_save_key}']:
        col1, col2 = st.columns(2)
        with col1:
            delete_button = st.button("确认删除预约", key=delete_key)
        with col2:
            save_button = st.button("确认保存修改", key=save_key)

        if delete_button:
            delete_appointment(appointment_id)
            st.session_state[f'delete_save_clicked_{delete_save_key}'] = False

        if save_button:
            update_appointment(appointment_id, edited_package, customer_name, edited_contact_info, selected_date, time_slot, edited_remarks)
            st.session_state[f'delete_save_clicked_{delete_save_key}'] = False


# 登录后显示当前的预约情况：
def view_appointments():
    conn = create_connection()
    cursor = conn.cursor()

    st.subheader("选择日期查看预约")

    # 设置默认值为当天的日期
    today =date.today()
    three_months_later = today + timedelta(days=90)
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
        has_appointments = len(appointments) > 0

        with st.expander(f"时间：{time_slot}", expanded=has_appointments):
            # 使用日期和时间段的组合作为唯一的 key
            is_open_checkbox = st.checkbox("可预约（去掉✔后新用户无法约）", value=is_open, key=f"open_{selected_date}_{time_slot}")


            for index, appointment in enumerate(appointments, start=1):
                st.markdown(f"**<{index}> 客户 {appointment[1]} 已预约：**")

                edit_and_delete_appointment_form(appointment, selected_date, appointment[3], context='view_appointments')

                
            # 更新可预约状态
            if is_open_checkbox != is_open:
                cursor.execute("REPLACE INTO date_time_slots (date, time_slot, is_open) VALUES (?, ?, ?)", (selected_date, time_slot, is_open_checkbox))
                conn.commit()
                log_action("admin", "__更新可预约状态__", f"__日期{selected_date},时段{time_slot}状态{is_open_checkbox}__")
    conn.close()

def add_new_appointment_form():
    st.subheader("新增用户预约信息")

    # 创建表单
    with st.form(key="new_appointment_form"):
        new_customer_name = st.text_input("用户姓名")
        new_package = st.text_input("套系")
        new_contact_info = st.text_input("联系方式")
        new_remarks = st.text_input("备注")

        # 添加日期和时间段选择器
        new_appointment_date = st.date_input("选择预约日期")
        time_slots = ["09:00-11:00", "11:00-13:00", "13:00-15:00", "15:00-17:00", "17:00-19:00"]
        new_appointment_time = st.selectbox("选择时间段", time_slots)

        # 提交按钮
        submit_button = st.form_submit_button(label="保存新预约")

    if submit_button:
        # 保存逻辑
        state = add_new_appointment(new_package, new_customer_name, new_contact_info, new_appointment_date, new_appointment_time, new_remarks)
        if state:
            st.success("已新增一条预约信息")
        else:
            st.error("相同联系方式的用户已有预约")



def update_appointment(appointment_id, package, customer_name, contact_info, selected_date, selected_time, remarks):
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE appointments SET package = ?, customer_name = ?, contact_info = ?, appointment_date = ?, appointment_time = ?, special_requirements = ? WHERE id = ?", (package, customer_name, contact_info, selected_date, selected_time, remarks, appointment_id))
    conn.commit()
    conn.close()
    log_action("admin", "__更新预约内容__", f"__套系{package},用户名称{customer_name},电话/微信{contact_info},日期{selected_date},时段{selected_time}备注{remarks}__索引号{appointment_id}__")
    st.success("预约信息已更新")


def delete_appointment(appointment_id):
    conn = create_connection()
    cursor = conn.cursor()
    # 执行删除操作
    cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
        # 可以选择在此处添加一个成功删除的消息
    print(f"预约 {appointment_id} 已成功删除")
    conn.commit()
    conn.close()
    log_action("admin", "__删除预约__", f"__索引号{appointment_id}__")


def add_new_appointment( package, customer_name,  contact_info, selected_date,selected_time, remarks):
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
        return True
    else:
        print("Appointment already exists for:", customer_name, contact_info, selected_date, selected_time)  # 调试信息
        return False
    conn.close()
    

def view_recent_appointments_summary():
    conn = create_connection()
    cursor = conn.cursor()

    # 获取当前日期和时间
    current_date = date.today().strftime("%Y-%m-%d")
    current_time = datetime.now().strftime("%H:%M")

    # 查询数据库以获取当前时间之后的最新5个预约
    cursor.execute("""
    SELECT * FROM appointments 
    WHERE (appointment_date > ?) OR (appointment_date = ? AND appointment_time >= ?)
    ORDER BY appointment_date ASC, appointment_time ASC 
    LIMIT 5""", (current_date, current_date, current_time))

    recent_appointments = cursor.fetchall()

    st.subheader("最近5次预约概要")
    for appointment in recent_appointments:
        with st.expander(f"{appointment[2]}, {appointment[3]} - 用户：{appointment[1]}"):
            edit_and_delete_appointment_form(appointment, appointment[2], appointment[3], context='view_recent')

    conn.close()



def admin_dashboard():
    st.title("海岸阳光摄影●预约管理")

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
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    date_generated = [start + timedelta(days=x) for x in range(0, (end-start).days + 1)]

    for date in date_generated:
        formatted_date = date.strftime("%Y-%m-%d")
        for slot in time_slots:
            cursor.execute("INSERT OR IGNORE INTO date_time_slots (date, time_slot, is_open) VALUES (?, ?, ?)", (formatted_date, slot, True))

    conn.commit()
    conn.close()




