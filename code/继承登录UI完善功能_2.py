"""
    继承登录UI完善功能_2 模块
"""

# 通配符 '*'
__all__ = ['LoginUI_two', 'load_all_users', 'upsert_user']

import os, sqlite3, time
import tkinter as tk
from tkinter import ttk

from manage_gui import ManageWin
from 继承登录UI完善功能_1 import LoginUI_one


# === 用户数据库（user_info.db / user 表）相关工具函数 ===

_VALID_ROLES_DB = {'student', 'admin'}


def _user_db_path_static():
    """user_info.db 路径，统一放在项目根目录下的 user_data/。"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    user_data_dir = os.path.join(project_root, 'user_data')
    os.makedirs(user_data_dir, exist_ok=True)
    return os.path.join(user_data_dir, 'user_info.db')


def _init_user_table():
    """确保 user_info.db 中存在 user 表。"""
    conn = sqlite3.connect(_user_db_path_static())
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user (
                username varchar PRIMARY KEY,
                password varchar,
                phone    varchar,
                role     varchar
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def _migrate_users_from_txt(txt_path):
    """
    若 user 表为空且旧 txt 用户库存在，则一次性迁移到 SQLite。
    迁移完成后保留 txt 文件，但后续读写都不再使用它。
    """
    if not txt_path or not os.path.exists(txt_path):
        return

    conn = sqlite3.connect(_user_db_path_static())
    try:
        cursor = conn.cursor()
        count = cursor.execute("SELECT COUNT(*) FROM user").fetchone()[0]
        if count > 0:
            return

        with open(txt_path, encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()

                if len(parts) >= 4:
                    username, password, phone = parts[0], parts[1], parts[2]
                    role = parts[3].strip().lower()
                    if role not in _VALID_ROLES_DB:
                        role = 'student'
                elif len(parts) == 3:
                    username, password, phone = parts[0], parts[1], parts[2]
                    role = 'student'
                else:
                    continue

                cursor.execute(
                    "INSERT OR IGNORE INTO user "
                    "(username, password, phone, role) VALUES (?, ?, ?, ?)",
                    (username, password, phone, role),
                )
        conn.commit()
    finally:
        conn.close()


def load_all_users():
    """读取 user 表所有用户，返回 [[username, password, phone, role], ...]。"""
    _init_user_table()
    conn = sqlite3.connect(_user_db_path_static())
    try:
        cursor = conn.cursor()
        rows = cursor.execute(
            "SELECT username, password, phone, role FROM user"
        ).fetchall()
    finally:
        conn.close()
    return [list(row) for row in rows]


def upsert_user(username, password, phone, role):
    """新增或覆盖一条用户记录。"""
    if role not in _VALID_ROLES_DB:
        role = 'student'
    _init_user_table()
    conn = sqlite3.connect(_user_db_path_static())
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO user "
            "(username, password, phone, role) VALUES (?, ?, ?, ?)",
            (username, password, phone, role),
        )
        conn.commit()
    finally:
        conn.close()


def find_user(username):
    """按用户名查询单条用户，返回 [username, password, phone, role] 或 None。"""
    _init_user_table()
    conn = sqlite3.connect(_user_db_path_static())
    try:
        cursor = conn.cursor()
        row = cursor.execute(
            "SELECT username, password, phone, role FROM user WHERE username=?",
            (username,),
        ).fetchone()
    finally:
        conn.close()
    return list(row) if row else None


class LoginUI_two(LoginUI_one):
    """继承LoginUI，完善登录UI功能"""

    VALID_ROLES = {'student', 'admin'}
    ROLE_NAME_MAP = {'student': '学生', 'admin': '管理员'}

    def __init__(self):
        """构造方法"""

        # 调用LoginUI的构造方法
        super().__init__()

        # 完善登录UI功能

        # 获取已注册的用户数据
        self.getUserData(self._user_data_path('已注册用户数据库.txt'))

        # 用户登录
        self.loginButton.config(command=self.userLogin)
        # self.loginSucceedUI()   # 模拟登录成功

    # 登录成功(UI)
    def loginSucceedUI(self, role='student'):
        role = role if role in self.VALID_ROLES else 'student'
        self.destroy()
        manage_win = ManageWin(role=role)
        manage_win.mainloop()

    # 显示时钟
    def showTime(self):
        if not self.stopFlag:
            return
        self.timeVar.set(time.strftime('%X\n%x\n%A'))
        self._time_job = self.succeedUI.after(200, self.showTime)

    # 登录成功UI返回
    def succeedUI_return(self):
        self.stopFlag = 0  # 停止显示时钟（结束循环）
        if getattr(self, '_time_job', None) is not None:
            try:
                self.succeedUI.after_cancel(self._time_job)
            except tk.TclError:
                pass
            self._time_job = None

        self.deiconify()  # 显示主窗口（登录UI）
        self.succeedUI.destroy()  # 销毁成功登录UI

        # 初始化数据
        self.userName.set('')
        self.password.set('')
        self.inputVerifyCode.set('')
        self.showVerifyCode.set('获取验证码')
        self.verifyButton.config(text='获取验证码')
        self.showOrConcealCount = 0  # 默认是密码隐藏

    # 获取已注册的用户数据（数据源：user_info.db / user 表）
    def getUserData(self, path=None):
        """
        从 user_info.db 加载已注册用户。
        path 参数保留以兼容旧调用：若指向旧 txt 用户库，且 user 表为空，
        会自动把 txt 数据迁移进 SQLite，然后再读取。
        """
        _init_user_table()
        if path:
            _migrate_users_from_txt(path)
        self.userData = load_all_users()

    def _user_data_path(self, filename):
        return self._asset_path('user_data', filename)

    def verify_code_ok(self, expected_code, input_code):
        expected = (expected_code or '').strip()
        current = (input_code or '').strip()
        if not expected or expected == '获取验证码':
            return False
        return expected.lower() == current.lower()

    # 用户登录
    def userLogin(self):
        expected_role = getattr(self, 'current_role', 'student')
        if expected_role not in self.VALID_ROLES:
            expected_role = 'student'
        expected_role_name = self.ROLE_NAME_MAP[expected_role]

        # 未获取验证码时直接拦截
        if self.showVerifyCode.get() == '获取验证码':
            self.bell()
            self.verifyButton.focus_set()
            self.hintLabel.config(text='请先获取验证码', background='red')
            self.hintLabel.place(x=228, y=115)
            self.update()
            time.sleep(1)
            self.hintLabel.place_forget()
            return

        username = self.userEntry.get().strip()
        password = self.passwordEntry.get().strip()
        input_verify = self.verifyEntry.get().strip()

        if username == '请输入用户名':
            username = ''
        if password == '请输入密码':
            password = ''
        if input_verify == '请输入验证码':
            input_verify = ''

        if username in ('', '请输入用户名'):
            self.bell()
            self.userEntry.focus_set()
            self.hintLabel.config(text='请输入用户名', background='red')
            self.hintLabel.place(x=228, y=115)
            self.update()
            time.sleep(1)
            self.hintLabel.place_forget()
            return

        if password in ('', '请输入密码'):
            self.bell()
            self.passwordEntry.focus_set()
            self.hintLabel.config(text='请输入密码', background='red')
            self.hintLabel.place(x=228, y=115)
            self.update()
            time.sleep(1)
            self.hintLabel.place_forget()
            return

        if input_verify in ('', '请输入验证码'):
            self.bell()
            self.verifyEntry.focus_set()
            self.hintLabel.config(text='请输入验证码', background='red')
            self.hintLabel.place(x=228, y=115)
            self.update()
            time.sleep(1)
            self.hintLabel.place_forget()
            return

        # 如果用户数据为空
        if not self.userData:
            self.bell()  # 警告声
            self.hintLabel.config(text='恭喜您是首位用户\n  快来注册体验吧！', background='pink')
            self.hintLabel.place(x=228, y=115)
            self.update()
            time.sleep(1)
            self.hintLabel.place_forget()
            return

        # 查找用户名是否已注册
        for name in self.userData:
            # name: [用户名, 密码, 手机号, 角色]
            if name[0] == username:
                # 验证密码是否正确
                if name[1] == password:
                    # 判断验证码是否正确
                    if self.verify_code_ok(self.showVerifyCode.get(), input_verify):
                        account_role = name[3] if len(name) > 3 else 'student'
                        account_role = account_role if account_role in self.VALID_ROLES else 'student'

                        # 角色越权校验
                        if account_role != expected_role:
                            self.bell()
                            self.hintLabel.config(
                                text=f'权限不足：该账号不是{expected_role_name}',
                                background='red'
                            )
                            self.hintLabel.place(x=228, y=115)
                            self.update()
                            time.sleep(1)
                            self.hintLabel.place_forget()
                            return

                        # 登录成功：按角色分流
                        print('登录成功')
                        self.route_to_system(account_role)
                        return
                    else:
                        self.verifyEntry.focus()
                        self.hintLabel.config(text='验证码输入错误', background='red')
                        break
                else:
                    self.passwordEntry.focus()
                    self.hintLabel.config(text='密码输入错误', background='red')
                    break
            elif name == self.userData[-1]:
                self.userEntry.focus_set()
                self.hintLabel.config(text='用户名输入错误', background='red')

        # 警告声与更新验证码
        self.bell()
        self.updateVerifyCode()
        self.hintLabel.place(x=228, y=115)
        self.update()
        time.sleep(1)
        self.hintLabel.place_forget()

    def route_to_system(self, role):
        """登录后按角色进入对应系统页"""
        if role == 'admin':
            self.adminSystemUI()
        else:
            self.studentSystemUI()

    def adminSystemUI(self):
        """管理员系统入口（预留）"""
        print('进入管理员系统（预留接口：adminSystemUI）')
        self.loginSucceedUI(role='admin')

    def studentSystemUI(self):
        """学生系统入口（预留）"""
        print('进入学生系统（预留接口：studentSystemUI）')
        self.loginSucceedUI(role='student')

# 代码测试
if __name__ == '__main__':
    ui = LoginUI_two()  # 对象实例化
    ui.mainloop()  # 窗口主循环
else:
    print(f'导入【{__name__}】模块')