"""
图书管理系统后台主界面
"""

import os
import sqlite3
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename

import chineseize_matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from openpyxl import Workbook, load_workbook


def _project_root():
    # code 目录的上一级即项目根目录
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _book_db_path():
    # 统一将图书数据库放在项目根目录的 user_data 下
    user_data_dir = os.path.join(_project_root(), "user_data")
    os.makedirs(user_data_dir, exist_ok=True)
    return os.path.join(user_data_dir, "user_info.db")


def init_book_table():
    """
    初始化图书表（连接 user_info.db 并创建 book 表）
    """
    conn = sqlite3.connect(_book_db_path())
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS book (
                bookname varchar primary key,
                price varchar,
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
        tk.Label(self, text="图书列表页（ListFrame）", font=(None, 16, "bold")).pack(pady=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=12, pady=6)

        self.add_btn = ttk.Button(btn_frame, text="添加图书", command=self.go_add)
        self.add_btn.pack(side=tk.LEFT, padx=4)

        self.del_btn = ttk.Button(btn_frame, text="删除图书", command=self.delete_book)
        self.del_btn.pack(side=tk.LEFT, padx=4)

        self.refresh_btn = ttk.Button(btn_frame, text="刷新列表", command=self.reload)
        self.refresh_btn.pack(side=tk.LEFT, padx=4)

        columns = ("bookname", "author", "price", "pubcom")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=18)
        self.tree.heading("bookname", text="书名")
        self.tree.heading("author", text="作者")
        self.tree.heading("price", text="价格")
        self.tree.heading("pubcom", text="出版社")
        self.tree.column("bookname", width=140, anchor=tk.CENTER)
        self.tree.column("author", width=120, anchor=tk.CENTER)
        self.tree.column("price", width=90, anchor=tk.CENTER)
        self.tree.column("pubcom", width=160, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        self.reload()
        if self.master.role != "admin":
            self.add_btn.config(state=tk.DISABLED)
            self.del_btn.config(state=tk.DISABLED)

    def _db_path(self):
        return _book_db_path()

    def go_add(self):
        self.master.showFrame(self.master.add_frame)

    def reload(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = sqlite3.connect(self._db_path())
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT bookname, author, price, pubcom FROM book")
            rows = cursor.fetchall()
        finally:
            conn.close()

        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def delete_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "请先选择要删除的图书")
            return

        bookname = self.tree.item(selected[0], "values")[0]
        if not messagebox.askyesno("确认删除", f"确定删除《{bookname}》吗？"):
            return

        conn = sqlite3.connect(self._db_path())
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM book WHERE bookname=?", (bookname,))
            conn.commit()
        finally:
            conn.close()

        self.reload()


class AddFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        tk.Label(self, text="图书添加页（AddFrame）", font=(None, 16, "bold")).pack(pady=10)

        form = tk.Frame(self)
        form.pack(pady=20)

        self.bookname_var = tk.StringVar()
        self.author_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.pubcom_var = tk.StringVar()

        tk.Label(form, text="书名").grid(row=0, column=0, padx=8, pady=8, sticky=tk.E)
        self.bookname_entry = ttk.Entry(form, textvariable=self.bookname_var, width=28)
        self.bookname_entry.grid(row=0, column=1, padx=8, pady=8)

        tk.Label(form, text="作者").grid(row=1, column=0, padx=8, pady=8, sticky=tk.E)
        self.author_entry = ttk.Entry(form, textvariable=self.author_var, width=28)
        self.author_entry.grid(row=1, column=1, padx=8, pady=8)

        tk.Label(form, text="价格").grid(row=2, column=0, padx=8, pady=8, sticky=tk.E)
        self.price_entry = ttk.Entry(form, textvariable=self.price_var, width=28)
        self.price_entry.grid(row=2, column=1, padx=8, pady=8)

        tk.Label(form, text="出版社").grid(row=3, column=0, padx=8, pady=8, sticky=tk.E)
        self.pubcom_entry = ttk.Entry(form, textvariable=self.pubcom_var, width=28)
        self.pubcom_entry.grid(row=3, column=1, padx=8, pady=8)

        action = tk.Frame(self)
        action.pack(pady=6)
        ttk.Button(action, text="保存图书", command=self.save_book).pack(side=tk.LEFT, padx=6)
        ttk.Button(
            action,
            text="返回列表",
            command=lambda: self.master.showFrame(self.master.list_frame)
        ).pack(side=tk.LEFT, padx=6)

    def _db_path(self):
        return _book_db_path()

    def save_book(self):
        # 直接从 Entry 取值，避免窗口重建后旧 StringVar 失效
        bookname = self.bookname_entry.get().strip()
        author = self.author_entry.get().strip()
        price = self.price_entry.get().strip()
        pubcom = self.pubcom_entry.get().strip()

        if not all([bookname, author, price, pubcom]):
            messagebox.showwarning("提示", "请完整填写图书信息")
            return

        conn = sqlite3.connect(self._db_path())
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO book (bookname, price, author, pubcom) VALUES (?, ?, ?, ?)",
                (bookname, price, author, pubcom),
            )
            conn.commit()
        finally:
            conn.close()

        messagebox.showinfo("成功", "图书添加成功")
        for entry in (self.bookname_entry, self.author_entry, self.price_entry, self.pubcom_entry):
            entry.delete(0, tk.END)
        self.master.list_frame.reload()
        self.master.showFrame(self.master.list_frame)


class DataFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        tk.Label(self, text="数据分析页（DataFrame）", font=(None, 16, "bold")).pack(pady=30)

        self.pub_pie_btn = ttk.Button(
            self,
            text="出版社发行数量统计",
            command=self.show_pie_chart
        )
        self.pub_pie_btn.pack(pady=12)

    def show_pie_chart(self):
        conn = sqlite3.connect(_book_db_path())
        try:
            df = pd.read_sql_query("SELECT pubcom FROM book", conn)
        finally:
            conn.close()

        pub_series = df["pubcom"].dropna().astype(str).str.strip()
        pub_series = pub_series[pub_series != ""]
        counts = pub_series.value_counts()

        if counts.empty:
            messagebox.showinfo("提示", "当前没有可用于统计的出版社数据")
            return

        plt.figure(figsize=(8, 6))
        plt.pie(
            counts.values,
            labels=counts.index,
            autopct="%.1f%%"
        )
        plt.title("各出版社图书数量占比")
        plt.show()


class AboutFrame(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        tk.Label(self, text="关于我们（AboutFrame）", font=(None, 16, "bold")).pack(pady=30)


class ManageWin(tk.Tk):
    def __init__(self, role="student"):
        super().__init__()
        self.role = role
        self.title("后台管理界面")
        self.geometry("600x600")
        self.resizable(False, False)

        # 初始化数据库图书表
        init_book_table()

        # 预创建各页面
        self.welcome_frame = WelcomeFrame(self)
        self.list_frame = ListFrame(self)
        self.add_frame = AddFrame(self)
        self.data_frame = DataFrame(self)
        self.about_frame = AboutFrame(self)
        self.current_frame = None

        # 创建菜单栏
        self.create_menu()

        # 初始显示欢迎页
        self.showFrame(self.welcome_frame)

    def create_menu(self):
        menubar = tk.Menu(self)

        # 图书管理
        book_menu = tk.Menu(menubar, tearoff=0)
        book_menu.add_command(label="欢迎页", command=lambda: self.showFrame(self.welcome_frame))
        book_menu.add_command(label="图书列表", command=lambda: self.showFrame(self.list_frame))
        if self.role == "admin":
            book_menu.add_command(label="添加图书", command=lambda: self.showFrame(self.add_frame))
        menubar.add_cascade(label="图书管理", menu=book_menu)

        # 数据分析
        menubar.add_command(label="数据分析", command=lambda: self.showFrame(self.data_frame))

        # 导入导出
        io_menu = tk.Menu(menubar, tearoff=0)
        io_menu.add_command(label="导入", command=self.import_data)
        io_menu.add_command(label="导出", command=self.export_data)
        menubar.add_cascade(label="导入导出", menu=io_menu)

        # 帮助
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于我们", command=lambda: self.showFrame(self.about_frame))
        help_menu.add_separator()
        help_menu.add_command(label="退出系统", command=self.destroy)
        menubar.add_cascade(label="帮助", menu=help_menu)

        self.config(menu=menubar)

    def export_data(self):
        file_path = asksaveasfilename(
            title="导出图书数据",
            defaultextension=".xlsx",
            filetypes=[("Excel 文件", "*.xlsx")],
        )
        if not file_path:
            return

        conn = sqlite3.connect(_book_db_path())
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT bookname, author, price, pubcom FROM book")
            rows = cursor.fetchall()
        finally:
            conn.close()

        wb = Workbook()
        ws = wb.active
        ws.title = "图书数据"
        ws.append(["书名", "作者", "价格", "出版社"])
        for row in rows:
            ws.append(list(row))

        try:
            wb.save(file_path)
            messagebox.showinfo("提示", "导出成功")
        except PermissionError:
            messagebox.showerror("错误", "导出失败！文件正被其他程序占用，请关闭后重试。")
        except Exception as e:
            messagebox.showerror("错误", f"导出时发生未知错误：{e}")

    def import_data(self):
        file_path = askopenfilename(
            title="导入图书数据",
            filetypes=[("Excel 文件", "*.xlsx *.xlsm *.xltx *.xltm")],
        )
        if not file_path:
            return

        try:
            wb = load_workbook(file_path)
            ws = wb.active
        except Exception as e:
            messagebox.showerror("错误", f"读取 Excel 失败：{e}")
            return

        conn = sqlite3.connect(_book_db_path())
        try:
            cursor = conn.cursor()
            success_count = 0
            error_count = 0
            for row in ws.iter_rows(min_row=2, values_only=True):
                if not row:
                    continue

                try:
                    values = list(row) + [None] * (4 - len(row))
                    bookname, author, price, pubcom = values[0], values[1], values[2], values[3]
                    if bookname is None or str(bookname).strip() == "":
                        error_count += 1
                        continue

                    cursor.execute(
                        "INSERT OR REPLACE INTO book (bookname, price, author, pubcom) VALUES (?, ?, ?, ?)",
                        (
                            str(bookname).strip(),
                            "" if price is None else str(price).strip(),
                            "" if author is None else str(author).strip(),
                            "" if pubcom is None else str(pubcom).strip(),
                        ),
                    )
                    success_count += 1
                except Exception:
                    error_count += 1
            conn.commit()
        except Exception as e:
            messagebox.showerror("错误", f"导入失败：{e}")
            return
        finally:
            conn.close()

        messagebox.showinfo("提示", f"导入完成：成功 {success_count} 条，失败 {error_count} 条")
        self.list_frame.reload()

    def showFrame(self, frame):
        """
        利用 pack() 和 pack_forget() 实现页面切换
        """
        if self.current_frame is not None:
            self.current_frame.pack_forget()
        self.current_frame = frame
        self.current_frame.pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    app = ManageWin()
    app.mainloop()
