"""
    登录UI 模块
"""

# 通配符 '*'
__all__ = ['LoginUI']

import os
import tkinter as tk
from tkinter import ttk

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


class LoginUI(tk.Tk):
    """继承tk.Tk，创建登录UI"""

    WINDOW_WIDTH = 620
    WINDOW_HEIGHT = 406

    def __init__(self):
        """构造方法"""

        # 调用tk.Tk的构造方法
        super().__init__()

        self.width = self.winfo_screenwidth()  # 屏幕宽度
        self.height = self.winfo_screenheight()  # 屏幕高度

        # 设计自己项目的UI
        self.title('图书管理登录界面')  # 标题
        self.geometry(
            f'{self.WINDOW_WIDTH}x{self.WINDOW_HEIGHT}+'
            f'{(self.width - self.WINDOW_WIDTH) // 2}+{(self.height - self.WINDOW_HEIGHT) // 3}'
        )
        self.resizable(0, 0)  # 窗口大小禁止调节

        # 窗口背景图（自适应）
        self.backgroundPhoto = self._load_photo('用户登录背景.png', (self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        if self.backgroundPhoto is not None:
            self.backgroundLabel = tk.Label(self, image=self.backgroundPhoto, bd=0, highlightthickness=0)
        else:
            self.backgroundLabel = tk.Label(self, bg='#f5f7fb', bd=0, highlightthickness=0)
        self.backgroundLabel.place(x=0, y=0, relwidth=1, relheight=1)

        # 系统名
        self.titleLabel = tk.Label(self, text='图  书  管  理  系  统', font=('Tahoma', 30, 'bold'))
        self.titleLabel.place(x=118, y=40)

        # 输入格式错误提示
        self.hintLabel = tk.Label(self, text='输入格式错误提示', width=20)
        self.hintLabel.place(x=228, y=115)

        # 用户名
        tk.Label(self, text='用户名').place(x=170, y=160)

        # 输入用户名
        self.userName = tk.StringVar()
        self.userEntry = ttk.Entry(self, textvariable=self.userName, width=22)
        self.userEntry.place(x=223, y=161)

        # 随机用户名按钮（图标/纯文本降级）
        self.randomPhoto = self._load_photo('随机用户名.png', (20, 20))
        if self.randomPhoto is not None:
            self.randomButton = tk.Button(self, image=self.randomPhoto, relief=tk.FLAT, bd=0, highlightthickness=0)
        else:
            self.randomButton = tk.Button(self, text='随机', relief=tk.FLAT)
        self.randomButton.place(x=358, y=162)

        # 密码
        tk.Label(self, text='密   码').place(x=170, y=200)

        # 输入密码
        self.password = tk.StringVar()
        self.passwordEntry = ttk.Entry(self, textvariable=self.password, width=22, show='*')
        self.passwordEntry.place(x=223, y=201)

        # 显示/隐藏密码按钮（图标/纯文本降级）
        self.showOrConcealCount = 0
        self.showPhoto = self._load_photo('密码显示.png', (20, 20))
        self.concealPhoto = self._load_photo('密码隐藏.png', (20, 20))
        if self.showPhoto is not None:
            self.showOrConcealButton = tk.Button(
                self, image=self.showPhoto, relief=tk.FLAT, bd=0, highlightthickness=0
            )
        else:
            self.showOrConcealButton = tk.Button(self, text='显示', relief=tk.FLAT)
        self.showOrConcealButton.place(x=358, y=205)

        # 验证码
        tk.Label(self, text='验证码').place(x=170, y=244)

        # 输入验证码
        self.inputVerifyCode = tk.StringVar()
        self.verifyEntry = ttk.Entry(self, textvariable=self.inputVerifyCode, width=15)
        self.verifyEntry.place(x=223, y=244)

        # 随机验证码
        self.showVerifyCode = tk.StringVar(value='获取验证码')
        self.verifyButton = tk.Button(self, text=self.showVerifyCode.get(), relief='flat', width=10)
        self.verifyButton.place(x=350, y=240)

        # 刷新验证码按钮（图标/纯文本降级）
        self.updatePhoto = self._load_photo('验证码更新.png', (18, 18))
        if self.updatePhoto is not None:
            self.updateButton = tk.Button(self, image=self.updatePhoto, relief='flat', bd=0, highlightthickness=0)
        else:
            self.updateButton = tk.Button(self, text='刷新', relief='flat')
        self.updateButton.place(x=310, y=245)

        # 注册
        self.registerButton = ttk.Button(self, text='注册', width=4)
        self.registerButton.place(x=395, y=159)

        # 找回
        self.retrieveButton = ttk.Button(self, text='找回', width=4)
        self.retrieveButton.place(x=395, y=199)

        # 登录
        self.loginButton = ttk.Button(self, text='登录')
        self.loginButton.place(x=200, y=300)

        # 退出
        self.close = ttk.Button(self, text='退出', command=self.destroy)
        self.close.place(x=310, y=300)

    def _project_root(self):
        # code 目录的上一级即项目根目录
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _asset_path(self, *parts):
        return os.path.join(self._project_root(), *parts)

    def _load_photo(self, filename, size=None):
        path = self._asset_path('photo', filename)
        if not os.path.exists(path):
            return None

        if Image is not None and ImageTk is not None:
            try:
                img = Image.open(path)
                if size:
                    # 兼容不同 Pillow 版本的重采样常量
                    if hasattr(Image, 'Resampling'):
                        resample_mode = Image.Resampling.LANCZOS
                    else:
                        resample_mode = Image.LANCZOS
                    img = img.resize(size, resample_mode)
                # 关键：绑定到当前窗口 self
                return ImageTk.PhotoImage(img, master=self)
            except Exception:
                return None

        try:
            # 关键：绑定到当前窗口 self
            return tk.PhotoImage(file=path, master=self)
        except tk.TclError:
            return None


# 代码测试
if __name__ == '__main__':
    ui = LoginUI()  # 对象实例化
    ui.mainloop()  # 窗口主循环
else:
    print(f'导入【{__name__}】模块')