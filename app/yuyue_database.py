
# 预约信息数据库
import sqlite3

def setup_database():
    conn = sqlite3.connect('admin.db')
    cursor = conn.cursor()
    # 创建admin表（如果还未创建）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            email TEXT PRIMARY KEY,
            password TEXT
        )
    ''')
    # 增加或更新表以存储管理员的最后登录时间
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_login_status (
            email TEXT PRIMARY KEY,
            last_login_time TEXT
        )
    ''')
    # 创建appointments表（如果还未创建）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY,
            customer_name TEXT,
            appointment_date TEXT,
            appointment_time TEXT,
            package TEXT,
            contact_info TEXT,
            special_requirements TEXT
        )
    ''')  
    # 创建time_slots表（如果还未创建）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS date_time_slots (
            date TEXT,
            time_slot TEXT,
            is_open BOOLEAN,
            PRIMARY KEY (date, time_slot)
        )
    ''')
        # 创建 logs 表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            action TEXT,
            description TEXT,
            datetime TEXT
        )
    ''')
    conn.commit()
    conn.close()

# 数据库连接和操作函数
def create_connection():
    # 创建数据库连接
    conn = sqlite3.connect('admin.db')  # 使用不同的数据库文件以区分用户
    return conn

# 用户保存预约信息
def save_booking(package, name, contact_info, selected_date, selected_time, remarks):
    conn = create_connection()
    cursor = conn.cursor()

    # 检查是否已有相同联系方式的预约
    cursor.execute("SELECT * FROM appointments WHERE contact_info = ? AND appointment_date = ? AND appointment_time = ?", (contact_info, selected_date, selected_time))
    existing_appointment = cursor.fetchone()

    if not existing_appointment:
        cursor.execute("INSERT INTO appointments (customer_name, contact_info, appointment_date, appointment_time, package, special_requirements) VALUES (?, ?, ?, ?, ?, ?)", (name, contact_info, selected_date, selected_time, package, remarks))
        conn.commit()
        log_action(name, "__创建预约信息__", f"__套系{package},联系方式{contact_info},日期{selected_date},时段{selected_time}备注{remarks}__")

        print("New appointment saved:", package, name, contact_info, selected_date, selected_time)  # 调试信息
        return True
    else:
        print("Appointment already exists for:", contact_info, selected_date, selected_time)  # 调试信息
        return False

    conn.close()

def get_user_bookings(name, phone):
    conn = create_connection()
    cursor = conn.cursor()

    # 查询最近5次的预约信息
    cursor.execute("SELECT * FROM appointments WHERE customer_name = ? AND contact_info = ? ORDER BY appointment_date DESC, appointment_time DESC LIMIT 5", (name, phone))
    bookings = cursor.fetchall()

    conn.close()
    return bookings
