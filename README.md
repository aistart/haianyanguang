
# haianyanguang
海岸阳光预约平台


# streamlit example

streamlit example, features include:

- support login, register
- use sqlite record user info
- clear streamlit logo, title, menu

enjoy!

# 创建虚拟环境
python -m venv venv

# 进入虚拟环境
venv\Scripts\activate

# 安装requirements
pip install -r requirements.txt

# 退出虚拟环境
deactivate

# 运行预约平台
streamlit run main.py

# C:\Windows\System32\drivers\etc
20.27.177.113 github.com

# ################################3
# ubuntu 模式下
# 创建虚拟环境
 python3 -m venv venv

# 使用venv (在haianyanggang根目录下)
source venv/bin/activate
pip3 install -r requirements.txt

# 如何从github同步最新代码时，更新了init_streamlit.py，要注意修改路径
streamlit_model_path = os.path.join(ROOT_PATH, 'venv/lib/python3.8/site-packages/streamlit')

