
photography_packages = [

    {"serial": 1, "id": "774390634", "title": "百天/周岁照亲子合影",
     "description": "3套服装 22张精修。",
     "image_path": "./static/1.jpg"},
     
    {"serial": 2, "id": "762127507", "title": "亲子全家福套系含老人",
     "description": "5套服装，女士化妆．18张精修．同底送18张底片。",
     "image_path": "./static/2.jpg"},

    {"serial": 3, "id": "763029119", "title": "超值宝宝单人加亲子主题套系",
     "description": "3套服装，精修24张，底片全送。",
     "image_path": "./static/3.jpg"},

    {"serial": 4, "id": "760210379", "title": "入园照入学照儿童证件照",
     "description": "立等可取，含打印。",
     "image_path": "./static/4.jpg"},

    {"serial": 5, "id": "761068311", "title": "儿童写真室内外任选",
     "description": "套系包含3套服装．24张精修．底片全送。",
     "image_path": "./static/5.jpg"},

    {"serial": 6, "id": "760201527", "title": "特惠儿童写真",
     "description": "3套服装 20张精修 同底精修20张。",
     "image_path": "./static/6.jpg"},     

    {"serial": 7, "id": "762152645", "title": "超值全家福体验套系",
     "description": "3套服装，10张精修．送10张底片。",
     "image_path": "./static/7.jpg"},

    {"serial": 8, "id": "767865862", "title": "化妆证件照职业形象照",
     "description": "在节假日提前一天预约即可，如在工作日拍，当天预约就可以哦。",
     "image_path": "./static/8.jpg"},

    {"serial": 9, "id": "761886204", "title": "孕妇照宝爸合影", 
     "description": "3套服装．20张精修，同时底片20张。",
     "image_path": "./static/9.jpg"},

    {"serial": 10, "id": "762199476", "title": "婴幼儿非假日体验套系",
     "description": "2套服装，14张精修，同底送14张底片。",
     "image_path": "./static/10.jpg"},

    {"serial": 11, "id": "761882403", "title": "孕妇工作日拍摄套系",
     "description": "2套服装，12张精修，同底送12张底片。",
     "image_path": "./static/11.jpg"},

    {"serial": 12, "id": "761069120", "title": "简洁儿童肖像照",
     "description": "1套简单服装，4张精修，还送4张底片。",
     "image_path": "./static/12.jpg"},

    {"serial": 13, "id": "769206064", "title": "新生儿满月照上门拍底片全送",
     "description": "3套服装．20张精修，底片全送。",
     "image_path": "./static/13.jpg"},

    {"serial": 14, "id": "762975357", "title": "公园儿童外景跟拍",
     "description": "3套服装，36张精修，底片全送。",
     "image_path": "./static/14.jpg"}
]

import streamlit as st
import datetime
import pandas as pd

from .yuyue_database import *
from .utils import send_booking_email
# 已经在main中带import


def get_week_start_date(date):
    # 计算并返回所给日期所在周的周一的日期
    return date - datetime.timedelta(days=date.weekday())


def is_slot_available(selected_date, slot):
    conn = create_connection()
    cursor = conn.cursor()
    
    # 查询特定日期的特定时间段的开放状态
    cursor.execute("SELECT is_open FROM date_time_slots WHERE date = ? AND time_slot = ?", (selected_date, slot))
    result = cursor.fetchone()
    
    conn.close()

    # 如果找到了对应的记录并且该时段是开放的，则返回 True
    return result is not None and result[0]

def parse_date(date_str):
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()  # 正确使用 datetime.strptime


def show_booking_page(package):

    with st.container():
        col1, col2 = st.columns([1, 3])
    with col1:
        st.image(package["image_path"], use_column_width=True)
    with col2:
        st.subheader(f"您正在预约:")
        st.subheader(f"{package['serial']}. {package['title']}")
    st.write(f"{package['description']} ")
    if st.button('返回首页●选择其它套系'):
        del st.session_state['selected_package']
        st.experimental_rerun()  # 可选：刷新页面以反映状态的改变

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
    time_slots = ["09:00-11:00", "11:00-13:00", "13:00-15:00", "15:00-17:00", "17:00-19:00"]
    days = ["一", "二", "三", "四", "五", "六", "日"]

    # 获取今天的日期
    current_date = datetime.date.today()
    # 获取当前的日期和时间
    current_datetime = datetime.datetime.now()
    # 获取今天是周几，然后用中文表示
    today_weekday = weekday_mapping[current_datetime.strftime('%A')]


    # 默认selected_date为明天
    selected_date = st.date_input(f"今天{current_date.strftime('%m月%d号（')}周{today_weekday}）请选择预约日期", 
                                  datetime.date.today() + datetime.timedelta(days=1))

    # 根据用户选择的日期显示不同的信息
    if selected_date > current_date:

        # 获取今天和选择日期的周几，然后用中文表示
        selected_date_weekday = weekday_mapping[selected_date.strftime('%A')]

        st.markdown(f"请选{selected_date.strftime('%m月%d号（')}周{selected_date_weekday}）的具体时段\n")

        # 计算所选日期所在周的第一天（周一）
        start_date = get_week_start_date(selected_date)

        week_dates = [start_date + datetime.timedelta(days=i) for i in range(7)]

        # 创建 DataFrame周日历表格
        # current_date = datetime.datetime.now().date()  # 获取当前日期
        data = {day: [] for day in days}
        for slot in time_slots:
            for i, date in enumerate(week_dates):
                if date <= current_date:
                    data[days[i]].append("-")
                else:
                    status = is_slot_available(date, slot)
                    if status is None:
                        data[days[i]].append("/")
                    elif status:
                        # 如果是 selected_date 且状态为可预约，使用粗体显示
                        if date == selected_date:
                            data[days[i]].append("<b style='color: green;'>可</b>")
                        else:
                            data[days[i]].append(f"<span style='color: green;'>可</span>")
                    else:
                        # 如果是 selected_date 且状态为可预约，使用粗体显示
                        if date == selected_date:
                            data[days[i]].append("<b>满</b>")
                        else:
                            data[days[i]].append(f"<span>满</span>")

        df = pd.DataFrame(data, index=[slot[:2] for slot in time_slots])

        # 显示表格
        st.markdown(df.to_html(escape=False), unsafe_allow_html=True)
        
        st.markdown("（营业时间09:00-19:00）")
            # 使用会话状态存储所选时间
        if 'selected_time' not in st.session_state:
            st.session_state.selected_time = None
        for slot in time_slots:
            status = is_slot_available(selected_date, slot)
            slot_status = "仍有空档可选" if status else "已满"
            button_label = f"{slot} - {slot_status}"

            if st.button(button_label, key=f"{selected_date}_{slot}"):
                if status:
                    st.success(f"您已选择 {selected_date}_{slot} 时段")
                    st.session_state.selected_time = f"{slot}"
                else:
                    st.error(f"{selected_date}_{slot} 时段不可预约")
                    st.session_state.selected_time = None
                    
        with st.form(key='booking_form'):
            st.write("请填写预约信息：")
            name = st.text_input("姓名")
            phone = st.text_input("电话/微信")
            remarks = st.text_area("备注")  # 添加备注信息输入框

            # 格式化日期和时间为字符串（这里使用了年-月-日 时:分:秒的格式）
            current_datetime = datetime.datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

            # 将格式化的日期和时间附加到用户输入的备注信息后面
            full_remarks = f"{remarks} (提交预约时间: {formatted_datetime})"
            submit_button = st.form_submit_button(label='提交预约')

        if submit_button:
            # 验证用户是否已输入姓名和电话/微信
            if not name or not phone :
                st.error("您需输入预约人姓名、联系方式")
            elif st.session_state.selected_time:
                photoSet = f"{package['serial']}. {package['title']}"
                # 使用 st.session_state.selected_time 而不是 selected_time
                if save_booking(photoSet, name, phone, selected_date, st.session_state.selected_time, full_remarks):
                    # 预约成功的消息
                    st.success(f"\n您已预约：{photoSet}")
                    st.write(f"\n姓名: {name}")
                    st.write(f"\n电话/微信: {phone}")
                    st.write(f"\n日期: {selected_date}  ,  {st.session_state.selected_time}")
                    st.write(f"\n备注: {remarks}")
                    # 发送邮件
                    send_booking_email(photoSet, name, phone, selected_date, st.session_state.selected_time, remarks)
                    st.success("已收到您的预约信息，我们会尽快联系您，给您确认。")
                    # 查询数据库中的预约信息：对提交了多条预约信息的情况给予提示
                    bookings = get_user_bookings(name, phone)
                    future_bookings = [booking for booking in bookings if parse_date(booking[2]) >= current_date]
                    
                    if len(future_bookings) > 1:
                        st.warning("提醒您已有多条预约")
                        for booking in future_bookings:
                            st.write(f"预约日期: {booking[2]}, 时间段: {booking[3]}, 套系: {booking[4]}")
                        st.warning("如有重复预约，请联系客服取消。")
    
                else:
                    st.error("您在此时间段已有预约。取消预约请联系客服。")
            else:
                st.error("请先选择好拍照日期和时间段")
    else:
        st.markdown(f"此日期已不可在线预约。")

    st.markdown(f" * 如预定当天，请直接电话或微信联系。")

    st.write(f"* 北京海岸阳光亲子摄影工作室")
    st.write(f"电话/微信：18611401551。")
    st.write(f"座机：010-82927090。")
    st.write(f"-------------------- ")


def show_user_bookings(name, phone):
    # 这里假设有一个函数 get_user_bookings 来获取预约信息
    bookings = get_user_bookings(name, phone)
    if bookings:
        print(f"bookings:{bookings}")
        st.write(f"**您已预约：**")
        for booking in bookings:
            # 解析预约信息中的各个字段
            booking_id, user_name, booking_date, booking_time, package_name, phone_number, additional_info = booking
            # 按照指定格式输出信息
            st.success(f"预约所用名：{user_name}\n\n 预约：{booking_date} , {booking_time}  \n\n 套系序号：{package_name}  \n\n 备注：{additional_info}")
            
        st.write("**咨询微信：18611401551。**")
        st.write("**座机：010-82927090。**")
    else:
        st.write(f"暂无预约。可选择您喜欢的套系后点击预约。")

def user_main():
        # 在页面顶部放置一个锚点
    st.markdown("<a id='page-top'></a>", unsafe_allow_html=True)

    st.title("海岸阳光摄影●用户预约")

    # 检查会话状态是否已经初始化
    if 'name' not in st.session_state:
        st.session_state['name'] = ''
    if 'phone' not in st.session_state:
        st.session_state['phone'] = ''

    with st.expander("点击可查询已预约信息"):  # 使用 expander 组件
        with st.form(key='query_form'):
            # name_input = st.text_input("姓名", value=st.session_state['name'])
            phone_input = st.text_input("预约所用的电话/微信", value=st.session_state['phone'])
            submit_query = st.form_submit_button("查询已预约信息")

    if submit_query:
        # 更新会话状态
        # st.session_state['name'] = name_input if name_input is not None else ''
        st.session_state['phone'] = phone_input if phone_input is not None else ''
        show_user_bookings(st.session_state['name'], st.session_state['phone'])


    if 'selected_package' not in st.session_state:
        for package in photography_packages:
            with st.container():
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.image(package["image_path"], use_column_width=True)
                with col2:
                    st.subheader(f"{package['serial']}. {package['title']}")
                    if st.button(f"预约●{package['title']}", key=package["serial"]):
                        st.session_state['selected_package'] = package
    else:
        show_booking_page(st.session_state['selected_package'])
    
    # 在页面底部添加一个返回顶部的链接
    st.markdown("[返回顶部](#page-top)", unsafe_allow_html=True)
    
    st.write("\n ")
    st.write("\n ")
    st.write("\n ")
    st.write("\n ")
    st.write("\n ")
    st.write("网站备案号: [京ICP备2022032803号-1](https://beian.miit.gov.cn)")
