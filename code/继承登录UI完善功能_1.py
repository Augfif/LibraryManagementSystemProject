"""
    继承登录UI完善功能_1 模块
"""

# 通配符 '*'
__all__ = ['LoginUI_one']

import random
from 登录ui import LoginUI


class LoginUI_one(LoginUI):
    """继承LoginUI，完善登录UI功能"""

    def __init__(self):
        """构造方法"""

        # 调用LoginUI的构造方法
        super().__init__()

        # 完善登录UI功能

        # 隐藏错误提示标签
        self.hintLabel.place_forget()

        # 隐藏随机用户名按钮
        self.randomButton.place_forget()

        # 显示/隐藏密码
        self.showOrConcealButton.config(command=self.showOrConcealPassword)

        # 随机验证码
        self.verifyButton.config(command=self.updateVerifyCode)

        # 刷新验证码
        self.updateButton.config(command=self.updateVerifyCode)

        # 预显示提示输入（仅绑定到输入框，避免窗口聚焦误触发）
        self.userEntry.bind('<FocusIn>', self.hintFocusIn)
        self.userEntry.bind('<FocusOut>', self.hintFocusOut)
        self.passwordEntry.bind('<FocusIn>', self.hintFocusIn)
        self.passwordEntry.bind('<FocusOut>', self.hintFocusOut)
        self.verifyEntry.bind('<FocusIn>', self.hintFocusIn)
        self.verifyEntry.bind('<FocusOut>', self.hintFocusOut)

        # 初始化占位符
        self.hintFocusOut(event=type('evt', (), {'widget': self.userEntry})())
        self.hintFocusOut(event=type('evt', (), {'widget': self.passwordEntry})())
        self.hintFocusOut(event=type('evt', (), {'widget': self.verifyEntry})())
        self.userEntry.focus_set()

    # 更新验证码
    def updateVerifyCode(self, event=None):
        verify_code = self.getVerifyCode()
        self.showVerifyCode.set(verify_code)
        self.verifyButton.config(text=verify_code)

    # 获取验证码
    def getVerifyCode(self, num=6, event=None):

        # 获取6位验证码的容器
        container = []
        # 大小写字母
        for i in range(26):
            container.append(chr(ord('a') + i))
            container.append(chr(ord('A') + i))
        # 数字
        for i in range(26 * 2):
            container.append(str(i)[-1])

        # 在容器内获取随机数
        verify_code = ''
        for i in range(num):
            verify_code += random.choice(container)

        return verify_code

    # 显示密码/隐藏密码
    def showOrConcealPassword(self, event=None):
        self.showOrConcealCount += 1
        show_plain = self.showOrConcealCount % 2 == 1

        # 显示密码
        if show_plain:
            self.passwordEntry.config(show='')
            if self.concealPhoto is not None:
                self.showOrConcealButton.config(image=self.concealPhoto, text='')
            else:
                self.showOrConcealButton.config(text='隐藏')

        # 隐藏密码
        else:
            if self.password.get() != '请输入密码':
                self.passwordEntry.config(show='*')
            if self.showPhoto is not None:
                self.showOrConcealButton.config(image=self.showPhoto, text='')
            else:
                self.showOrConcealButton.config(text='显示')

    # 输入框聚焦：清理占位
    def hintFocusIn(self, event=None):
        current = event.widget if event is not None else None

        if current == self.userEntry:
            if self.userEntry.get() == '请输入用户名':
                self.userName.set('')
            self.userEntry.config(foreground='black')

        elif current == self.passwordEntry:
            if self.passwordEntry.get() == '请输入密码':
                self.password.set('')
            self.passwordEntry.config(foreground='black')
            if not self.showOrConcealCount % 2:
                self.passwordEntry.config(show='*')
            else:
                self.passwordEntry.config(show='')

        elif current == self.verifyEntry:
            if self.verifyEntry.get() == '请输入验证码':
                self.inputVerifyCode.set('')
            self.verifyEntry.config(foreground='black')

    # 输入框失焦：为空则恢复占位
    def hintFocusOut(self, event=None):
        current = event.widget if event is not None else None

        if current == self.userEntry and not self.userEntry.get().strip():
            self.userName.set('请输入用户名')
            self.userEntry.config(foreground='gray')

        elif current == self.passwordEntry and not self.passwordEntry.get().strip():
            self.passwordEntry.config(show='')
            self.password.set('请输入密码')
            self.passwordEntry.config(foreground='gray')

        elif current == self.verifyEntry and not self.verifyEntry.get().strip():
            self.inputVerifyCode.set('请输入验证码')
            self.verifyEntry.config(foreground='gray')


# 代码测试
if __name__ == '__main__':
    ui = LoginUI_one()  # 对象实例化
    ui.mainloop()  # 窗口主循环
else:
    print(f'导入【{__name__}】模块')