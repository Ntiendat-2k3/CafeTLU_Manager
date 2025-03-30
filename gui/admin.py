import tkinter as tk
from tkinter import ttk, messagebox
from services.menu import MenuService
from services.auth import create_staff


class AdminDashboard:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Admin Dashboard")
        self.window.geometry("1200x800")
        self.menu_service = MenuService()
        self.selected_item = None

        self.build_ui()
        self.load_data()

    def build_ui(self):
        # Treeview
        self.tree = ttk.Treeview(
            self.window,
            columns=("ID", "Tên", "Giá", "Size", "Trạng thái"),
            show="headings",
            height=25
        )
        self.tree.heading("ID", text="ID")
        self.tree.heading("Tên", text="Tên món")
        self.tree.heading("Giá", text="Giá (VND)")
        self.tree.heading("Size", text="Size")
        self.tree.heading("Trạng thái", text="Trạng thái")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_item_selected)

        # Control buttons
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=10)

        buttons = [
            ("Thêm mới", self.open_add_dialog),
            ("Sửa", self.open_edit_dialog),
            ("Xóa", self.delete_item),
            ("Đổi trạng thái", self.toggle_availability),
            ("Tải lại", self.load_data),
            ("Tạo Staff", self.open_create_staff_dialog)
        ]

        for text, command in buttons:
            tk.Button(btn_frame, text=text, command=command).pack(side=tk.LEFT, padx=5)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        items = self.menu_service.get_all_coffees()
        for item in items:
            self.tree.insert("", "end", values=(
                item['item_id'],
                item['name'],
                f"{item['price']:,.0f}",
                item['size'],
                "🟢 Có" if item['is_available'] else "🔴 Hết"
            ))

    def on_item_selected(self, event):
        selected = self.tree.selection()
        if selected:
            self.selected_item = self.tree.item(selected[0])["values"]

    def open_add_dialog(self):
        dialog = tk.Toplevel()
        dialog.title("Thêm Cà Phê Mới")
        dialog.grab_set()

        # Form fields
        fields = [
            ("Tên món:", tk.Entry(dialog, width=30)),
            ("Giá (VND):", tk.Entry(dialog)),
            ("Size:", ttk.Combobox(dialog, values=["S", "M", "L"])),
            ("Mô tả:", tk.Entry(dialog, width=40)),
            ("Có sẵn:", tk.BooleanVar(value=True))
        ]

        for i, (label, widget) in enumerate(fields):
            tk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5)
            if isinstance(widget, tk.Entry):
                widget.grid(row=i, column=1)
            elif isinstance(widget, ttk.Combobox):
                widget.grid(row=i, column=1)
                widget.current(1)  # Mặc định size M
            else:
                tk.Checkbutton(dialog, variable=widget).grid(row=i, column=1, sticky="w")

        def submit():
            try:
                self.menu_service.add_coffee(
                    name=fields[0][1].get(),
                    price=float(fields[1][1].get()),
                    size=fields[2][1].get(),
                    description=fields[3][1].get(),
                    is_available=fields[4][1].get()
                )
                self.load_data()
                dialog.destroy()
                messagebox.showinfo("Thành công", "Thêm món thành công!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")

        tk.Button(dialog, text="Lưu", command=submit).grid(row=5, column=1, pady=10)

    def open_edit_dialog(self):
        if not self.selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn món")
            return

        item_id = self.selected_item[0]
        current_item = self.menu_service.get_item_by_id(item_id)

        dialog = tk.Toplevel()
        dialog.title("Chỉnh sửa cà phê")
        dialog.grab_set()

        # Form fields
        fields = [
            ("Tên món:", tk.Entry(dialog, width=30)),
            ("Giá (VND):", tk.Entry(dialog)),
            ("Size:", ttk.Combobox(dialog, values=["S", "M", "L"])),
            ("Mô tả:", tk.Entry(dialog, width=40)),
            ("Có sẵn:", tk.BooleanVar())
        ]

        # Điền giá trị hiện tại
        fields[0][1].insert(0, current_item['name'])
        fields[1][1].insert(0, str(current_item['price']))
        fields[2][1].set(current_item['size'])
        fields[3][1].insert(0, current_item['description'])
        fields[4][1].set(current_item['is_available'])

        for i, (label, widget) in enumerate(fields):
            tk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5)
            if isinstance(widget, tk.Entry):
                widget.grid(row=i, column=1)
            elif isinstance(widget, ttk.Combobox):
                widget.grid(row=i, column=1)
            else:
                tk.Checkbutton(dialog, variable=widget).grid(row=i, column=1, sticky="w")

        def submit():
            try:
                self.menu_service.update_coffee(
                    item_id=item_id,
                    name=fields[0][1].get(),
                    price=float(fields[1][1].get()),
                    size=fields[2][1].get(),
                    description=fields[3][1].get(),
                    is_available=fields[4][1].get()
                )
                self.load_data()
                dialog.destroy()
                messagebox.showinfo("Thành công", "Cập nhật thành công!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")

        tk.Button(dialog, text="Lưu", command=submit).grid(row=5, column=1, pady=10)

    def delete_item(self):
        if not self.selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn món để xóa")
            return

        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa món này?"):
            try:
                self.menu_service.delete_item(self.selected_item[0])
                self.load_data()
                messagebox.showinfo("Thành công", "Đã xóa món!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Xóa thất bại: {str(e)}")

    def toggle_availability(self):
        if not self.selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn món")
            return

        try:
            self.menu_service.toggle_availability(self.selected_item[0])
            self.load_data()
            messagebox.showinfo("Thành công", "Đã đổi trạng thái!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Thao tác thất bại: {str(e)}")

    # endregion

    # region Staff Management
    def open_create_staff_dialog(self):
        dialog = tk.Toplevel()
        dialog.title("Tạo Staff Mới")
        dialog.grab_set()

        tk.Label(dialog, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        entry_username = tk.Entry(dialog)
        entry_username.grid(row=0, column=1)

        tk.Label(dialog, text="Password:").grid(row=1, column=0, padx=5, pady=5)
        entry_password = tk.Entry(dialog, show="*")
        entry_password.grid(row=1, column=1)

        def submit():
            try:
                create_staff(
                    username=entry_username.get(),
                    password=entry_password.get()
                )
                messagebox.showinfo("Thành công", "Tạo staff thành công!")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Tạo staff thất bại: {str(e)}")

        tk.Button(dialog, text="Tạo", command=submit).grid(row=2, column=1, pady=10)

    # endregion

    def run(self):
        self.window.mainloop()