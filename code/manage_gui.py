"""
图书管理系统后台主界面
"""

import os
import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox


def get_db_path():
    """
    优先连接现有 user_info.db；若不存在则在当前目录创建
    """
    current_dir = os.path.dirname(__file__)
    candidates = [
        os.path.join(current_dir, "user_info.db"),
        os.path.join(current_dir, "user_data", "user_info.db"),
        os.path.join(os.path.dirname(current_dir), "user_info.db"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return candidates[0]


def init_book_table():
    """
    初始化图书表（连接 user_info.db 并创建 book 表）
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS book (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bookname varchar,
                price REAL,
                author varchar,
                pubcom varchar
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


class WelcomeFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        tk.Label(self, text="欢迎页（WelcomeFrame）", font=(None, 16, "bold")).pack(pady=30)


class ListFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # 图书列表表格
        self.book_tree = ttk.Treeview(
            self,
            columns=("bookname", "price", "author", "pubcom"),
            show="headings",
            height=18
        )
        self.book_tree.heading("bookname", text="图书名称")
        self.book_tree.heading("price", text="图书价格")
        self.book_tree.heading("author", text="图书作者")
        self.book_tree.heading("pubcom", text="出版社")

        self.book_tree.column("bookname", width=180, anchor="center")
        self.book_tree.column("price", width=110, anchor="center")
        self.book_tree.column("author", width=140, anchor="center")
        self.book_tree.column("pubcom", width=140, anchor="center")

        self.book_tree.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 10), sticky="nsew")

        # 功能按钮
        self.add_btn = ttk.Button(self, text="添加图书", command=lambda: self.master.showFrame("add"))
        self.del_btn = ttk.Button(self, text="删除图书", command=self.delRow)
        self.reload_btn = ttk.Button(self, text="刷新图书", command=self.reload)

        self.add_btn.grid(row=1, column=0, padx=20, pady=(10, 20), sticky="ew")
        self.del_btn.grid(row=1, column=1, padx=20, pady=(10, 20), sticky="ew")
        self.reload_btn.grid(row=1, column=2, padx=20, pady=(10, 20), sticky="ew")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

        # 初始化时自动加载一次数据
        self.reload()

    def reload(self):
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT bookname, price, author, pubcom FROM book")
            rows = cursor.fetchall()
        finally:
            conn.close()

        # 清空旧数据
        for item in self.book_tree.get_children():
            self.book_tree.delete(item)

        # 载入新数据（bookname, price, author, pubcom）
        for row in rows:
            self.book_tree.insert("", tk.END, values=(row[0], row[1], row[2], row[3]))

    def delRow(self):
        selected = self.book_tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请选择一条记录")
            return

        if not messagebox.askokcancel("删除确认", "您确定要删除此记录么？"):
            return

        item_id = selected[0]
        values = self.book_tree.item(item_id, "values")
        if not values:
            messagebox.showerror("错误", "选中记录无效")
            return

        bookname = values[0]
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM book WHERE bookname = ?", (bookname,))
            conn.commit()
        finally:
            conn.close()

        self.reload()


class AddFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.columnconfigure(1, weight=1)

        tk.Label(self, text="图书添加页", font=(None, 16, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(20, 25)
        )

        tk.Label(self, text="书名").grid(row=1, column=0, padx=20, pady=8, sticky="e")
        tk.Label(self, text="作者").grid(row=2, column=0, padx=20, pady=8, sticky="e")
        tk.Label(self, text="价格").grid(row=3, column=0, padx=20, pady=8, sticky="e")
        tk.Label(self, text="出版社").grid(row=4, column=0, padx=20, pady=8, sticky="e")

        self.bookname_var = tk.StringVar()
        self.author_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.pubcom_var = tk.StringVar()

        self.bookname_entry = ttk.Entry(self, textvariable=self.bookname_var, width=35)
        self.author_entry = ttk.Entry(self, textvariable=self.author_var, width=35)
        self.price_entry = ttk.Entry(self, textvariable=self.price_var, width=35)
        self.pubcom_entry = ttk.Entry(self, textvariable=self.pubcom_var, width=35)

        self.bookname_entry.grid(row=1, column=1, padx=(0, 30), pady=8, sticky="w")
        self.author_entry.grid(row=2, column=1, padx=(0, 30), pady=8, sticky="w")
        self.price_entry.grid(row=3, column=1, padx=(0, 30), pady=8, sticky="w")
        self.pubcom_entry.grid(row=4, column=1, padx=(0, 30), pady=8, sticky="w")

        self.save_btn = ttk.Button(self, text="保存图书", command=self.save_book)
        self.cancel_btn = ttk.Button(self, text="取消返回", command=lambda: self.master.showFrame("list"))
        self.save_btn.grid(row=5, column=0, padx=20, pady=(25, 10), sticky="ew")
        self.cancel_btn.grid(row=5, column=1, padx=(0, 30), pady=(25, 10), sticky="ew")

    def save_book(self):
        bookname = self.bookname_var.get().strip()
        author = self.author_var.get().strip()
        price_text = self.price_var.get().strip()
        pubcom = self.pubcom_var.get().strip()

        if not all([bookname, author, price_text, pubcom]):
            messagebox.showwarning("提示", "请完整填写图书信息")
            return

        try:
            price = float(price_text)
        except ValueError:
            messagebox.showwarning("提示", "价格必须是数字")
            return

        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO book (bookname, price, author, pubcom) VALUES (?, ?, ?, ?)",
                (bookname, price, author, pubcom)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("保存失败", "该书名已存在，请更换书名")
            return
        finally:
            conn.close()

        messagebox.showinfo("保存成功", "图书保存成功")
        self.bookname_var.set("")
        self.author_var.set("")
        self.price_var.set("")
        self.pubcom_var.set("")

        list_frame = self.master.frames.get("list")
        if list_frame is not None:
            list_frame.reload()


class DataFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        tk.Label(self, text="数据分析页（DataFrame）", font=(None, 16, "bold")).pack(pady=30)


class AboutFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        tk.Label(self, text="关于我们（AboutFrame）", font=(None, 16, "bold")).pack(pady=30)


class ManageWin(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("后台管理界面")
        self.geometry("600x600")
        self.resizable(False, False)

        # 初始化数据库图书表
        init_book_table()

        # 预创建并统一管理各页面
        self.frames = {
            "welcome": WelcomeFrame(self),
            "list": ListFrame(self),
            "add": AddFrame(self),
            "data": DataFrame(self),
            "about": AboutFrame(self),
        }

        # 创建菜单栏
        self.create_menu()

        # 初始显示欢迎页
        self.showFrame("welcome")

    def create_menu(self):
        menubar = tk.Menu(self)

        # 图书管理
        book_menu = tk.Menu(menubar, tearoff=0)
        book_menu.add_command(label="欢迎页", command=lambda: self.showFrame("welcome"))
        book_menu.add_command(label="图书列表", command=lambda: self.showFrame("list"))
        book_menu.add_command(label="添加图书", command=lambda: self.showFrame("add"))
        menubar.add_cascade(label="图书管理", menu=book_menu)

        # 数据分析
        menubar.add_command(label="数据分析", command=lambda: self.showFrame("data"))

        # 导入导出
        io_menu = tk.Menu(menubar, tearoff=0)
        io_menu.add_command(label="导入", command=lambda: self.showFrame("list"))
        io_menu.add_command(label="导出", command=lambda: self.showFrame("list"))
        menubar.add_cascade(label="导入导出", menu=io_menu)

        # 帮助
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于我们", command=lambda: self.showFrame("about"))
        help_menu.add_separator()
        help_menu.add_command(label="退出系统", command=self.destroy)
        menubar.add_cascade(label="帮助", menu=help_menu)

        self.config(menu=menubar)

    def showFrame(self, frame_name):
        """
        利用 pack() 和 pack_forget() 实现页面切换
        """
        for frame in self.frames.values():
            frame.pack_forget()
        target_frame = self.frames.get(frame_name)
        if target_frame is not None:
            target_frame.pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    app = ManageWin()
    app.mainloop()
