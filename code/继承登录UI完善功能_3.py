"""
    继承登录UI完善功能_3 模块
"""

# 通配符 '*'
__all__ = ['Retrieve']

import time
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as tkmb

from 继承登录UI完善功能_2 import LoginUI_two


class Retrieve(LoginUI_two):
    """继承LoginUI_two，设计用户密码找回"""

    def __init__(self):
        """构造方法"""

        # 调用LoginUI的构造方法
        super().__init__()

        # 设计用户密码找回

        # 找回按钮
        self.retrieveButton.config(command=self.passwordRetrieve)

    # 用户密码找回
    def passwordRetrieve(self):
        # 设计窗口
        self.retrieveUI = tk.Toplevel(self)
        self.retrieveUI.title('用户密码找回')
        self.retrieveUI.geometry(f'600x375+{self.width // 4}+{self.height // 8}')
        self.retrieveUI.resizable(0, 0)  # 窗口大小禁止调节
        self.retrieveUI.focus_force()  # 窗口焦点
        self.withdraw()  # 隐藏主窗口（登录UI）

        # 输入格式错误提示
        self.retrieve_hintLabel = tk.Label(self.retrieveUI, text='输入格式错误提示', width=20)
        # self.retrieve_hintLabel.place(x=155, y=55)

        # 用户名
        tk.Label(self.retrieveUI, text='用  户 名').place(x=100, y=100)

        # 用户名输入框
        self.retrieve_userVar = tk.StringVar()
        if self.userName.get() != '请输入用户名': self.retrieve_userVar.set(self.userName.get())
        self.retrieve_userEntry = ttk.Entry(self.retrieveUI, textvariable=self.retrieve_userVar)
        self.retrieve_userEntry.place(x=160, y=100)

        # 手机号码
        tk.Label(self.retrieveUI, text='手机号码').place(x=100, y=150)

        # 手机号码输入框
        self.retrieve_phoneVar = tk.StringVar()
        self.retrieve_phoneEntry = ttk.Entry(self.retrieveUI, textvariable=self.retrieve_phoneVar)
        self.retrieve_phoneEntry.place(x=160, y=150)

        # 验证码
        tk.Label(self.retrieveUI, text='验  证 码').place(x=100, y=200)

        # 验证码输入框
        self.retrieve_inputVerifyVar = tk.StringVar()
        self.retrieve_verifyEntry = ttk.Entry(self.retrieveUI, width=9, textvariable=self.retrieve_inputVerifyVar)
        self.retrieve_verifyEntry.place(x=160, y=200)

        # 获取验证码
        self.retrieve_showVerifyVar = tk.StringVar(value='获取验证码')
        self.retrieve_verifyButton = ttk.Button(self.retrieveUI, width=9, textvariable=self.retrieve_showVerifyVar,
                                                command=lambda: self.retrieve_showVerifyVar.set(self.getVerifyCode()))
        self.retrieve_verifyButton.place(x=234, y=198)

        # 确认
        self.retrieve_confirmButton = ttk.Button(self.retrieveUI, text='确认', command=self.confirmRetrieve)
        self.retrieve_confirmButton.place(x=100, y=250)

        # 取消(没有头绪设计)
        self.retrieve_cancelButton = ttk.Button(self.retrieveUI, text='取消', command=self.retrieveUI_return)
        self.retrieve_cancelButton.place(x=220, y=250)

        # 返回
        self.retrieve_returnButton = ttk.Button(self.retrieveUI, text='返回', command=self.retrieveUI_return)
        self.retrieve_returnButton.place(x=460, y=320)

        # 窗口关闭触发
        self.retrieveUI.protocol("WM_DELETE_WINDOW", self.retrieveUI_return)

    # 确认找回密码
    def confirmRetrieve(self):
        # print([self.retrieve_userVar.get(),self.retrieve_phoneVar.get(),self.retrieve_inputVerifyVar.get(),self.retrieve_showVerifyVar.get()])

        # 如果用户数据为空
        if not self.userData:
            self.bell()  # 警告声
            self.retrieve_hintLabel.config(text='恭喜您是首位用户\n  快来注册体验吧！', background='pink')  # 输入错误提示语
            self.retrieve_hintLabel.place(x=155, y=55)  # 显示错误提示标签内容
            self.retrieveUI.update()  # 窗口更新
            time.sleep(1)  # 睡眠1秒
            self.retrieve_hintLabel.place_forget()  # 隐藏错误提示标签内容
            return

        # 查找用户名是否已注册
        for name in self.userData:
            # 如果已注册
            if name[0] == self.retrieve_userVar.get():
                # 验证手机号码是否正确
                if name[2] == self.retrieve_phoneVar.get():
                    # 判断验证码是否正确
                    if self.verify_code_ok(self.retrieve_showVerifyVar.get(), self.retrieve_inputVerifyVar.get()):
                        # 登录成功
                        print('找回成功')
                        self.retrieve_password(name)

                        return
                    # 验证码错误
                    else:
                        self.retrieve_verifyButton.focus()  # 设置焦点
                        self.retrieve_hintLabel.config(text='验证码输入错误', background='red')  # 输入错误提示语
                        break
                # 手机号码错误
                else:
                    self.retrieve_phoneEntry.focus_set()  # 设置焦点
                    self.retrieve_hintLabel.config(text='手机号码输入错误', background='red')  # 输入错误提示语
                    break
            # 用户名错误
            elif name == self.userData[-1]:
                self.retrieve_userEntry.focus()  # 设置焦点
                self.retrieve_hintLabel.config(text='用户名输入错误', background='red')  # 输入错误提示语

        # 警告声与更新验证码
        self.bell()  # 警告声
        self.retrieve_showVerifyVar.set('获取验证码')
        self.retrieve_hintLabel.place(x=155, y=55)  # 显示错误提示标签内容
        self.retrieveUI.update()  # 窗口更新
        time.sleep(1)  # 睡眠1秒
        self.retrieve_hintLabel.place_forget()  # 隐藏错误提示标签内容

    # 找回用户密码
    def retrieve_password(self, name):
        self.retrieveUI.bell()  # 警告声
        # 禁止窗口使用
        self.retrieveUI.attributes("-disabled", True)

        # 确认是否
        if tkmb.askokcancel('密码成功找回',
                            f'您的账户信息如下:{" " * 50}\n用户名: {name[0]}\n密    码: {name[1]}\n绑定手机号码: {name[2]}'
                            f'\n\n是否返回登录？', parent=self.retrieveUI):
            # 恢复窗口使用
            self.retrieveUI.attributes("-disabled", False)
            # 返回登录UI
            self.retrieveUI_return()
            return

        # 恢复窗口使用
        self.retrieveUI.attributes("-disabled", False)

        self.retrieve_showVerifyVar.set('获取验证码')
        self.retrieveUI.focus_force()  # 窗口焦点

    # 返回登录UI
    def retrieveUI_return(self):
        self.deiconify()  # 显示主窗口（登录UI）
        self.retrieveUI.destroy()  # 销毁当前窗口

        if self.retrieve_userVar.get() != self.userName.get():
            self.userName.set(self.retrieve_userVar.get())
            self.userEntry.config(foreground='black')

        # 初始化数据
        self.password.set('')
        self.inputVerifyCode.set('')
        self.showVerifyCode.set('获取验证码')
        self.showOrConcealCount = 0  # 默认是密码隐藏


# 代码测试
if __name__ == '__main__':
    ui = Retrieve()  # 对象实例化
    ui.mainloop()  # 窗口主循环
else:
    print(f'导入【{__name__}】模块')