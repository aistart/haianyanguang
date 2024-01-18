import os
import yaml
import init_streamlit
import streamlit as st
import libs.streamlit_authenticator as stauth

from app.utils import view_logs
from app.admin import admin_dashboard
from app.yuyue_database import *
from app.user import *



st.set_page_config(page_title='海岸阳光预约平台', page_icon='./static/logo.jpg')

st.sidebar.title("导航栏")


def init_authenticator():
    filepath = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(filepath, 'auth.yaml')) as file:
        config = yaml.load(file, Loader=stauth.SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
    )
    return authenticator


def register_user(authenticator):
    try:
        if authenticator.register_user('管理员注册专用', preauthorization=False):
            st.success('新用户注册成功')
    except Exception as e:
        st.error(e)


def main():
    """主函数"""
    # 自定义 CSS 来增大单选按钮间距的效果
    st.markdown("""
        <style>
            /* 增大字体大小 */
            div[role="radiogroup"] > label {
                padding: 20px !important;
            }
        </style>
    """, unsafe_allow_html=True)


    setup_database()


    authenticator = init_authenticator()
    # check cookie not login again
    authenticator._check_cookie()
    if st.session_state["authentication_status"]:
        authenticator.logout('退出登录', 'sidebar')
        # 当管理员已登录时，显示所有选项
        page = st.sidebar.radio(" ", ["预约管理", "新管理员注册", "管理员日志"])
        if page == "预约管理":
            admin_dashboard()  # 新增函数，用于展示日志信息
        elif page == "新管理员注册":
            register_user(authenticator)
        elif page == "管理员日志":
            view_logs()  # 显示管理员界面
    else:
        # 当管理员未登录时，仅显示“用户预约”和“管理员登录”
        page = st.sidebar.radio(" ", ["用户预约", "管理员登录"])
        if page == "用户预约":
            user_main()
            pass
        elif page == "管理员登录":
            # register_user(authenticator)
            name, authentication_status, username = authenticator.login(
                '管理员登录', 'main')
            if st.session_state["authentication_status"] == False:
                st.error('用户名/密码 错误')
            elif st.session_state["authentication_status"] == None:
                st.warning('请输入用户密码')


main()