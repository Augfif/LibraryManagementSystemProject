"""
    继承登录UI完善功能_2 模块
"""

# 通配符 '*'
__all__ = ['LoginUI_two']

import os, time, sqlite3
import tkinter as tk
from tkinter import ttk

from 继承登录UI完善功能_1 import LoginUI_one
from manage_gui import ManageWin


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
        # 登录成功后直接关闭登录窗口，进入后台管理界面
        self.destroy()
        manage_win = ManageWin()
        manage_win.mainloop()

    # 获取已注册的用户数据
    def getUserData(self, path):
        # 兼容旧调用方式：若传入的是txt路径，则将db放在同目录下
        if path and os.path.splitext(path)[1].lower() == '.db':
            self.db_path = path
        else:
            base_dir = os.path.dirname(path) if path else os.getcwd()
            self.db_path = os.path.join(base_dir, 'user_info.db')

        # 初始化数据库与用户表（若不存在则自动创建）
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_info (
                    username TEXT PRIMARY KEY,
                    password TEXT NOT NULL,
                    phone TEXT,
                    role TEXT DEFAULT 'student'
                )
            """)
            conn.commit()
        finally:
            conn.close()

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

        # 实时查询数据库（不再依赖 self.userData）
        conn = sqlite3.connect(getattr(self, 'db_path', 'user_info.db'))
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT username, password, role FROM user_info WHERE username = ?",
                (username,)
            )
            row = cursor.fetchone()
        finally:
            conn.close()

        # 用户名不存在
        if row is None:
            self.userEntry.focus_set()
            self.hintLabel.config(text='用户名输入错误', background='red')
        else:
            db_username, db_password, db_role = row
            account_role = (db_role or 'student').strip().lower()
            if account_role not in self.VALID_ROLES:
                account_role = 'student'

            # 密码错误
            if db_password != password:
                self.passwordEntry.focus_set()
                self.hintLabel.config(text='密码输入错误', background='red')
            # 验证码错误
            elif not self.verify_code_ok(self.showVerifyCode.get(), input_verify):
                self.verifyEntry.focus_set()
                self.hintLabel.config(text='验证码输入错误', background='red')
            # 角色越权
            elif account_role != expected_role:
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
            else:
                # 登录成功：按角色分流
                print('登录成功')
                self.route_to_system(account_role)
                return

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