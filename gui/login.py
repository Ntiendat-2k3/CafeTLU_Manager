import tkinter as tk
from tkinter import messagebox
from services.auth import login
from database.db import Database
import bcrypt


class LoginWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Đăng Nhập")
        self.window.geometry("300x150")

        self.build_ui()

    def build_ui(self):
        tk.Label(self.window, text="Username:").grid(row=0, column=0, padx=10, pady=5)
        self.entry_user = tk.Entry(self.window)
        self.entry_user.grid(row=0, column=1)

        tk.Label(self.window, text="Password:").grid(row=1, column=0, padx=10, pady=5)
        self.entry_pass = tk.Entry(self.window, show="*")
        self.entry_pass.grid(row=1, column=1)

        tk.Button(self.window, text="Login", command=self.on_login).grid(row=2, column=1, pady=10)

    def login(username, password):
        db = Database()
        user = db.fetch("SELECT * FROM users WHERE username = %s", (username,))
        if not user:
            return False, None, None  # Thêm user_id vào return

        if bcrypt.checkpw(password.encode(), user[0]['password_hash'].encode()):
            # Trả về (success, role, user_id)
            return True, user[0]['role'], user[0]['id']
        return False, None, None

    def on_login(self):
        username = self.entry_user.get()
        password = self.entry_pass.get()

        # Nhận thêm user_id từ hàm login
        success, role, user_id = login(username, password)

        if success:
            self.open_dashboard(role, user_id)  # Truyền user_id vào
        else:
            messagebox.showerror("Lỗi", "Sai thông tin đăng nhập!")

    def open_dashboard(self, role, user_id):  # Thêm tham số user_id
        self.window.destroy()
        if role == "admin":
            from gui.admin import AdminDashboard
            AdminDashboard()
        else:
            from gui.staff import StaffDashboard
            StaffDashboard(user_id)  # Truyền user_id vào constructor

    def run(self):
        self.window.mainloop()