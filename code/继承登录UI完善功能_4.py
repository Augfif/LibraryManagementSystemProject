# 通配符 '*'
__all__ = ['Register']

import os, re, time, random
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as tkmb

from 继承登录UI完善功能_2 import LoginUI_two, upsert_user


class Register(LoginUI_two):
    """继承LoginUI_two，设计新用户注册"""

    def __init__(self):
        """构造方法"""

        # 调用LoginUI_two的构造方法
        super().__init__()

        # 获取随机用户名数据库数据
        self.getRandomUserNameData(self._user_data_path('随机用户名数据库.txt'))

        # 用户注册
        self.registerButton.config(command=self.userRegister)

    # === 新增：占位符处理辅助方法 ===
    def set_placeholder(self, entry, text, is_password=False):
        """为Entry组件添加占位符"""
        entry.insert(0, text)
        if is_password:
            entry.config(show='')  # 占位符状态下显示明文

        def on_focus_in(event):
            if entry.get() == text:
                entry.delete(0, tk.END)
                if is_password:
                    entry.config(show='*')  # 输入密码时变成星号

        def on_focus_out(event):
            if not entry.get():
                if is_password:
                    entry.config(show='')  # 恢复占位符时显示明文
                entry.insert(0, text)

        entry.bind("<FocusIn>", on_focus_in, add='+')
        entry.bind("<FocusOut>", on_focus_out, add='+')

    # 1) 用户注册(UI)
    def userRegister(self):
        # 设计用户注册(UI)
        self.registerUI = tk.Toplevel(self)
        self.registerUI.title('用户注册')
        self.registerUI.geometry(f'620x406+{self.width // 4}+{self.height // 8}')
        self.registerUI.resizable(0, 0)
        self.registerUI.focus_force()
        self.withdraw()

        self.registerBackgroundPhoto = self._load_photo('用户注册背景.png', (620, 406))
        if self.registerBackgroundPhoto is not None:
            self.registerBackgroundLabel = tk.Label(self.registerUI, image=self.registerBackgroundPhoto, bd=0,
                                                    highlightthickness=0)
        else:
            self.registerBackgroundLabel = tk.Label(self.registerUI, bg='#f5f7fb', bd=0, highlightthickness=0)
        self.registerBackgroundLabel.place(x=0, y=0, relwidth=1, relheight=1)

        self.register_hintLabel = tk.Label(self.registerUI, text='输入格式错误提示', width=22)

        tk.Label(self.registerUI, text='新用户名').place(x=340, y=90)
        self.newUserVar = tk.StringVar()
        self.newUserEntry = ttk.Entry(self.registerUI, textvariable=self.newUserVar, width=22)
        self.newUserEntry.place(x=400, y=90)
        self.set_placeholder(self.newUserEntry, '请输入用户名')  # 添加占位符

        # 随机用户名（图标优先）
        if hasattr(self, 'randomPhoto') and self.randomPhoto is not None:
            self.register_randomButton = tk.Button(self.registerUI, image=self.randomPhoto, relief=tk.FLAT, bd=0,
                                                   highlightthickness=0, command=self.randomUser)
        else:
            self.register_randomButton = tk.Button(self.registerUI, text='随机', relief=tk.FLAT,
                                                   command=self.randomUser)
        self.register_randomButton.place(x=535, y=91)

        tk.Label(self.registerUI, text='设置密码').place(x=340, y=130)
        self.setPasswordVar = tk.StringVar()
        self.setPasswordEntry = ttk.Entry(self.registerUI, textvariable=self.setPasswordVar, width=22)
        self.setPasswordEntry.place(x=400, y=130)
        self.set_placeholder(self.setPasswordEntry, '请输入密码', is_password=True)  # 添加占位符

        tk.Label(self.registerUI, text='确认密码').place(x=340, y=170)
        self.confirmPasswordVar = tk.StringVar()
        self.confirmPasswordEntry = ttk.Entry(self.registerUI, textvariable=self.confirmPasswordVar, width=22)
        self.confirmPasswordEntry.place(x=400, y=170)
        self.set_placeholder(self.confirmPasswordEntry, '请确认密码', is_password=True)  # 添加占位符

        tk.Label(self.registerUI, text='手机号码').place(x=340, y=210)
        self.registerPhoneVar = tk.StringVar()
        self.registerPhoneEntry = ttk.Entry(self.registerUI, textvariable=self.registerPhoneVar, width=22)
        self.registerPhoneEntry.place(x=400, y=210)
        self.set_placeholder(self.registerPhoneEntry, '请输入11位手机号')  # 添加占位符

        # 角色选择（默认学生）
        tk.Label(self.registerUI, text='注册角色').place(x=340, y=250)
        self.registerRoleVar = tk.StringVar(value='student')
        self.studentRadio = tk.Radiobutton(self.registerUI, text='学生', value='student', variable=self.registerRoleVar)
        self.adminRadio = tk.Radiobutton(self.registerUI, text='管理员', value='admin', variable=self.registerRoleVar)
        self.studentRadio.place(x=400, y=248)
        self.adminRadio.place(x=460, y=248)

        # 从入口页进入注册时，默认并锁定为当前入口角色，避免跨入口越权注册
        current_role = getattr(self, 'current_role', None)
        if current_role in ('student', 'admin'):
            self.registerRoleVar.set(current_role)
            self.studentRadio.config(state=tk.DISABLED)
            self.adminRadio.config(state=tk.DISABLED)

        tk.Label(self.registerUI, text='验 证 码').place(x=340, y=290)
        self.register_inputVerifyVar = tk.StringVar()
        self.registerVerifyEntry = ttk.Entry(self.registerUI, textvariable=self.register_inputVerifyVar, width=10)
        self.registerVerifyEntry.place(x=400, y=290)
        self.set_placeholder(self.registerVerifyEntry, '输入验证码')

        self.register_showVerifyVar = tk.StringVar(value='获取验证码')
        self.register_verifyButton = tk.Button(
            self.registerUI,
            text=self.register_showVerifyVar.get(),
            width=10,
            relief=tk.FLAT,
            command=self.updateRegisterVerifyCode
        )
        self.register_verifyButton.place(x=486, y=288)

        # 验证码更新图标按钮（图标优先）
        if hasattr(self, 'updatePhoto') and self.updatePhoto is not None:
            self.register_updateButton = tk.Button(self.registerUI, image=self.updatePhoto, relief=tk.FLAT, bd=0,
                                                   highlightthickness=0, command=self.updateRegisterVerifyCode)
        else:
            self.register_updateButton = tk.Button(self.registerUI, text='刷新', relief=tk.FLAT,
                                                   command=self.updateRegisterVerifyCode)
        self.register_updateButton.place(x=452, y=290)

        self.confirmButton = ttk.Button(self.registerUI, text='确定', command=self.registerUI_confirm)
        self.confirmButton.place(x=340, y=345)

        self.register_returnButton = ttk.Button(self.registerUI, text='返回', command=self.registerUI_return)
        self.register_returnButton.place(x=472, y=345)

        self.registerUI.protocol("WM_DELETE_WINDOW", self.registerUI_return)
        self.registerUI.bind('<KeyPress>', self.restrictInput)

        # 默认将光标焦点设置在用户名输入框上
        self.newUserEntry.focus_set()

    # 2) 注册页更新验证码
    def updateRegisterVerifyCode(self, event=None):
        verify_code = self.getVerifyCode()
        self.register_showVerifyVar.set(verify_code)
        self.register_verifyButton.config(text=verify_code)

    # 3) 确认注册（已全量改为使用 Entry.get()）
    def registerUI_confirm(self):
        self.register_hintLabel.place(x=400, y=40)  # 显示错误提示标签内容

        # 获取Entry真实内容，若等于占位符内容则视为空
        username = self.newUserEntry.get()
        username = '' if username == '请输入用户名' else username

        password = self.setPasswordEntry.get()
        password = '' if password == '请输入密码' else password

        confirm_password = self.confirmPasswordEntry.get()
        confirm_password = '' if confirm_password == '请确认密码' else confirm_password

        phone = self.registerPhoneEntry.get()
        phone = '' if phone == '请输入11位手机号' else phone

        verify_input = self.registerVerifyEntry.get()
        verify_input = '' if verify_input == '输入验证码' else verify_input

        # 用户名输入空
        if not username:
            self.register_hintLabel.config(text=f'用户名不能为空', background='red')
            self.newUserEntry.focus()
        # 密码输入空
        elif not password:
            self.register_hintLabel.config(text=f'密码不能为空', background='red')
            self.setPasswordEntry.focus()
        # 确认密码输入空
        elif not confirm_password:
            self.register_hintLabel.config(text=f'确认密码不能为空', background='red')
            self.confirmPasswordEntry.focus()
        # 手机号码输入空
        elif not phone:
            self.register_hintLabel.config(text=f'手机号码不能为空', background='red')
            self.registerPhoneEntry.focus()
        # 验证码输入空
        elif not verify_input:
            self.register_hintLabel.config(text=f'验证码不能为空', background='red')
            self.registerVerifyEntry.focus()

        # 判断输入两次密码是否相同
        elif password != confirm_password:
            self.register_hintLabel.config(text=f'两次密码输入不一致', background='red')
            self.confirmPasswordEntry.focus()
        # 判断输入手机号码长度是否为11位
        elif len(phone) != 11:
            self.register_hintLabel.config(text=f'11位手机号码输入有误', background='red')
            self.registerPhoneEntry.focus()
        # 判断验证码是否正确
        elif not self.verify_code_ok(self.register_showVerifyVar.get(), verify_input):
            self.register_hintLabel.config(text=f'6位验证码输入有误', background='red')
            self.register_verifyButton.focus()

        # 判断已注册用户数据库是否为空
        elif not self.userData:
            print('首位用户注册成功')
            self.register_hintLabel.place_forget()
            self.userData.append([username, password, phone, self.registerRoleVar.get()])
            self.write_register_user_data(self._user_data_path('已注册用户数据库.txt'))
            self.register_user_succeed(username)
            return

        else:
            # 查找用户名是否已注册
            for name in self.userData:
                if name[0] == username:
                    self.register_hintLabel.config(text=f'该用户名已注册', background='red')
                    self.newUserEntry.focus()
                    break
                elif name == self.userData[-1] and username:
                    print('注册成功')
                    self.register_hintLabel.place_forget()
                    self.userData.append([username, password, phone, self.registerRoleVar.get()])
                    self.write_register_user_data(self._user_data_path('已注册用户数据库.txt'))
                    self.register_user_succeed(username)
                    return

        # 警告声与更新验证码
        self.bell()
        self.register_showVerifyVar.set('获取验证码')
        self.register_verifyButton.config(text='获取验证码')
        self.register_hintLabel.place(x=400, y=40)
        self.registerUI.update()
        time.sleep(1)
        self.register_hintLabel.place_forget()

    # 用户注册成功UI（传入注册时的username）
    def register_user_succeed(self, username):
        self.registerUI.bell()
        self.registerUI.attributes("-disabled", True)
        if tkmb.askokcancel('用户注册成功', f'恭喜您已注册成功！\n是否登录"{username}"？'):
            self.registerUI.destroy()
            self.loginSucceedUI(role=self.registerRoleVar.get())
        else:
            self.registerUI_return()

    # 4) 将最新注册用户写入数据库（user_info.db / user 表）
    def write_register_user_data(self, path=None):
        """
        将 self.userData 中最新追加的用户写入 user_info.db。
        path 参数保留以兼容旧调用，但不再被使用（不再写 txt）。
        """
        if not self.userData:
            return
        user = self.userData[-1]
        username = user[0]
        password = user[1]
        phone = user[2]
        role = user[3] if len(user) > 3 else 'student'
        upsert_user(username, password, phone, role)

    # 限制输入内容
    def restrictInput(self, event=None):
        # 排除对占位符内容的错误拦截
        placeholders = ['请输入用户名', '请输入密码', '请确认密码', '请输入11位手机号', '输入验证码']

        # 用户名输入框限制
        if event.widget == self.newUserEntry:
            input_data = self.newUserVar.get()
            if input_data in placeholders: return
            chr_match = re.findall(' ', input_data)
            if chr_match or len(input_data) > 10:
                self.bell()
                self.register_hintLabel.place(x=400, y=40)
                if chr_match:
                    self.register_hintLabel.config(text='用户名格式无效空格" "', background='red')
                    self.newUserVar.set(input_data[:-len(chr_match):])
                elif len(input_data) > 10:
                    self.register_hintLabel.config(text='用户名超过命名最大长度', background='red')
                    self.newUserVar.set(input_data[:10:])
                self.registerUI.update()
                time.sleep(1)
                self.register_hintLabel.place_forget()

        # 设置密码输入框限制
        elif event.widget == self.setPasswordEntry:
            input_data = self.setPasswordVar.get()
            if input_data in placeholders: return
            chr_match = re.findall(' ', input_data)
            chinese_match = re.findall(r'[\u4e00-\u9fff]', input_data)
            if chr_match or chinese_match or len(input_data) > 10:
                self.bell()
                self.register_hintLabel.place(x=400, y=40)
                if chr_match:
                    self.register_hintLabel.config(text='密码格式无效空格" "', background='red')
                    self.setPasswordVar.set(input_data[:-len(chr_match):])
                elif chinese_match:
                    self.register_hintLabel.config(text='密码格式无效中文', background='red')
                    self.setPasswordVar.set(input_data[:-len(chinese_match):])
                elif len(input_data) > 10:
                    self.register_hintLabel.config(text='密码超过最大设置长度', background='red')
                    self.setPasswordVar.set(input_data[:10:])
                self.registerUI.update()
                time.sleep(1)
                self.register_hintLabel.place_forget()

        # 确认输入密码框限制
        elif event.widget == self.confirmPasswordEntry:
            input_data = self.confirmPasswordVar.get()
            if input_data in placeholders: return
            chr_match = re.findall(' ', input_data)
            chinese_match = re.findall(r'[\u4e00-\u9fff]', input_data)
            if chr_match or chinese_match or len(input_data) > 10:
                self.bell()
                self.register_hintLabel.place(x=400, y=40)
                if chr_match:
                    self.register_hintLabel.config(text='确认密码格式无效空格" "', background='red')
                    self.confirmPasswordVar.set(input_data[:-len(chr_match):])
                elif chinese_match:
                    self.register_hintLabel.config(text='确认密码格式无效中文', background='red')
                    self.confirmPasswordVar.set(input_data[:-len(chinese_match):])
                elif len(input_data) > 10:
                    self.register_hintLabel.config(text='确认密码超过最大设置长度', background='red')
                    self.confirmPasswordVar.set(input_data[:10:])
                self.registerUI.update()
                time.sleep(1)
                self.register_hintLabel.place_forget()

        # 输入手机号框限制
        elif event.widget == self.registerPhoneEntry:
            input_data = self.registerPhoneVar.get()
            if input_data in placeholders: return
            chr_match = re.findall(r'\D', input_data)
            if chr_match or len(input_data) > 11:
                self.bell()
                self.register_hintLabel.place(x=400, y=40)
                if chr_match:
                    self.register_hintLabel.config(text='手机号码仅限数字1-9', background='red')
                    self.registerPhoneVar.set(input_data[:-len(chr_match):])
                elif len(input_data) > 11:
                    self.register_hintLabel.config(text='手机号码超过最大长度', background='red')
                    self.registerPhoneVar.set(input_data[:11:])
                self.registerUI.update()
                time.sleep(1)
                self.register_hintLabel.place_forget()

        # 验证码输入框限制
        elif event.widget == self.registerVerifyEntry:
            input_data = self.register_inputVerifyVar.get()
            if input_data in placeholders: return
            chr_match = re.findall(r'\w', input_data)
            chinese_match = re.findall(r'[\u4e00-\u9fff]', input_data)
            if len(chr_match) != len(input_data) or chinese_match or len(input_data) > 6:
                self.bell()
                self.register_hintLabel.place(x=400, y=40)
                if len(chr_match) != len(input_data):
                    self.register_hintLabel.config(text='验证码格式无效特殊符号', background='red')
                    self.register_inputVerifyVar.set(input_data[:len(chr_match):])
                elif chinese_match:
                    self.register_hintLabel.config(text='验证码格式无效中文', background='red')
                    self.register_inputVerifyVar.set(input_data[:-len(chinese_match):])
                elif len(input_data) > 6:
                    self.register_hintLabel.config(text='验证码超过最大长度', background='red')
                    self.register_inputVerifyVar.set(input_data[:6:])
                self.registerUI.update()
                time.sleep(1)
                self.register_hintLabel.place_forget()

    # 获取随机用户名数据库数据
    def getRandomUserNameData(self, path):
        self.randomName = []
        if os.path.exists(path):
            with open(path, encoding='utf-8') as file:
                for line in file:
                    if line != '\n':
                        self.randomName.extend(line.split())

    # 随机用户名
    def randomUser(self, event=None):
        if self.randomName:
            self.newUserVar.set(random.choice(self.randomName))
            self.newUserEntry.focus_set()  # 随机后自动获取焦点去隐藏占位符
            return

        self.register_hintLabel.place(x=400, y=40)
        self.bell()
        self.register_hintLabel.config(text='随机用户名数据库为空', background='red')
        self.registerUI.update()
        time.sleep(1)
        self.register_hintLabel.place_forget()

    # 返回登录UI
    def registerUI_return(self):
        self.deiconify()
        if hasattr(self, 'registerUI') and self.registerUI.winfo_exists():
            self.registerUI.destroy()

        if hasattr(self, 'register_showVerifyVar'):
            self.register_showVerifyVar.set('获取验证码')
        if hasattr(self, 'register_verifyButton'):
            self.register_verifyButton.config(text='获取验证码')
        self.showOrConcealCount = 0


# 代码测试
if __name__ == '__main__':
    ui = Register()
    ui.mainloop()
else:
    print(f'导入【{__name__}】模块')