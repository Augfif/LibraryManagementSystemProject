"""
    图书管理系统入口
"""

__all__ = ['Main', 'MainPortal']

import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as tkmb

from 继承登录UI完善功能_3 import Retrieve
from 继承登录UI完善功能_4 import Register


class Main(Retrieve, Register):
    """继承Retrieve、Register，创建登录主界面"""

    def __init__(self, role='student', portal=None):
        self.current_role = role
        self.portal = portal
        super().__init__()

        role_text = '管理员' if self.current_role == 'admin' else '学生'
        self.title(f'图书管理系统 - {role_text}登录')

        # 恢复验证码刷新图标，不隐藏
        # 保持和 LoginUI 原始布局一致，避免按钮重叠
        self.verifyEntry.config(width=15)
        self.verifyButton.place(x=350, y=240)
        self.updateButton.place(x=310, y=245)

        # 进入界面时自动生成验证码
        self.updateVerifyCode()

        self.loginButton.place(x=170, y=300)
        self.close.place(x=297, y=300)

        self.close.config(command=self.back_to_portal)
        self.protocol("WM_DELETE_WINDOW", self.back_to_portal)

    def back_to_portal(self):
        """关闭登录界面并返回启动页"""
        if self.portal is not None:
            self.portal.login_ui = None
            try:
                if self.portal.winfo_exists():
                    self.portal.deiconify()
                    self.portal.focus_force()
            except tk.TclError:
                # 启动页若已销毁，忽略
                pass

        try:
            self.destroy()
        except tk.TclError:
            pass


class MainPortal(tk.Tk):
    """程序总入口启动页"""

    def __init__(self):
        super().__init__()
        self.title('图书管理系统')
        self.geometry('420x260+620+280')
        self.resizable(0, 0)

        # 记录当前登录窗口引用，避免重复创建与悬空引用
        self.login_ui = None

        tk.Label(self, text='图书管理系统', font=('Tahoma', 22, 'bold')).pack(pady=20)

        self.admin_btn = ttk.Button(self, text='管理员登陆', command=lambda: self.open_login('admin'))
        self.admin_btn.pack(pady=8, ipadx=10)

        self.student_btn = ttk.Button(self, text='学生登陆', command=lambda: self.open_login('student'))
        self.student_btn.pack(pady=8, ipadx=10)

        self.help_btn = ttk.Button(self, text='使用说明', command=self.show_help)
        self.help_btn.pack(pady=8, ipadx=10)

    def _login_ui_alive(self):
        """安全判断 login_ui 是否还可用"""
        if self.login_ui is None:
            return False
        try:
            return bool(self.login_ui.winfo_exists())
        except tk.TclError:
            # Tk 应用已销毁时会抛错
            self.login_ui = None
            return False

    def open_login(self, role):
        """打开登录页并传递角色"""
        if self._login_ui_alive():
            self.login_ui.lift()
            self.login_ui.focus_force()
            return

        self.withdraw()
        self.login_ui = Main(role=role, portal=self)
        self.login_ui.focus_force()

    def show_help(self):
        tkmb.showinfo(
            '使用说明',
            '1. 选择“管理员登陆”或“学生登陆”进入对应入口。\n'
            '2. 账号密码正确后会进行角色校验。\n'
            '3. 角色不匹配将被拦截。'
        )


if __name__ == '__main__':
    portal = MainPortal()
    portal.mainloop()
else:
    print(f'导入【{__name__}】模块')