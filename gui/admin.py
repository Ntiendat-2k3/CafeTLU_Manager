import tkinter as tk
from tkinter import ttk, messagebox
from services.menu import MenuService
from services.auth import create_staff

class AdminDashboard:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Admin Dashboard")
        self.window.geometry("1440x600")
        self.window.config(bg="#f4f4f4")
        self.menu_service = MenuService()
        self.selected_item = None

        # Mapping hiển thị
        self.temp_mapping = {
            'hot': 'Nóng 🔥',
            'cold': 'Lạnh ❄️',
            'both': 'Cả hai 🌡️'
        }

        self.build_ui()
        self.load_data()

    def build_ui(self):
        # Main Frame
        main_frame = tk.Frame(self.window, bg="#f4f4f4")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Sidebar Frame
        sidebar = tk.Frame(main_frame, bg="#4CAF50", width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        # Sidebar Title
        sidebar_title = tk.Label(sidebar, text="Quản Lý", font=("Arial", 14, "bold"), bg="#388E3C", fg="white", pady=20)
        sidebar_title.pack(fill=tk.X)

        # Sidebar Buttons
        buttons = [
            ("Thêm mới", self.open_add_dialog),
            ("Sửa", self.open_edit_dialog),
            ("Xóa", self.delete_item),
            ("Đổi trạng thái", self.toggle_availability),
            ("Tải lại", self.load_data),
            ("Tạo Staff", self.open_create_staff_dialog),
            ("Thống kê bán hàng", self.open_sales_statistics)
        ]

        for text, command in buttons:
            tk.Button(sidebar, text=text, command=command, bg="#4CAF50", fg="white", font=("Arial", 12), relief="flat", width=20, height=2).pack(pady=5)

        # Main Content Area
        content_frame = tk.Frame(main_frame, bg="#f4f4f4")
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header Label for content area
        header_label = tk.Label(content_frame, text="Quản Lý Menu Cà Phê", font=("Arial", 18, "bold"), bg="#81C784", fg="white", pady=20)
        header_label.pack(fill=tk.X)

        # Treeview with styling
        self.tree = ttk.Treeview(
            content_frame,
            columns=("ID", "Tên", "Giá", "Size", "Nhiệt độ", "Trạng thái"),
            show="headings",
            height=40,
            style="Custom.Treeview",
        )
        self.tree.heading("ID", text="ID")
        self.tree.heading("Tên", text="Tên món")
        self.tree.heading("Giá", text="Giá (VND)")
        self.tree.heading("Size", text="Size")
        self.tree.heading("Nhiệt độ", text="Nhiệt độ")
        self.tree.heading("Trạng thái", text="Trạng thái")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self.on_item_selected)

        # Treeview Styling
        style = ttk.Style()
        style.configure("Custom.Treeview", font=("Arial", 11), background="#E8F5E9", foreground="black", fieldbackground="#E8F5E9", rowheight=35)
        style.configure("Custom.Treeview.Heading", font=("Arial", 12, "bold"), background="#81C784", foreground="#388E3C")

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
                self.temp_mapping[item['temperature_type']],
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

        # Form fields with padding and consistency
        fields = [
            ("Tên món:", tk.Entry(dialog, width=30)),
            ("Giá (VND):", tk.Entry(dialog)),
            ("Size:", ttk.Combobox(dialog, values=["S", "M", "L"])),
            ("Mô tả:", tk.Entry(dialog, width=40)),
            ("Nhiệt độ:", ttk.Combobox(dialog, values=list(self.temp_mapping.keys()))),
            ("Có sẵn:", tk.BooleanVar(value=True))
        ]

        for i, (label, widget) in enumerate(fields):
            tk.Label(dialog, text=label, font=("Arial", 12)).grid(row=i, column=0, padx=10, pady=10, sticky="e")
            if isinstance(widget, tk.Entry):
                widget.grid(row=i, column=1, padx=10, pady=10)
            elif isinstance(widget, ttk.Combobox):
                widget.grid(row=i, column=1, padx=10, pady=10)
            else:
                tk.Checkbutton(dialog, variable=widget).grid(row=i, column=1, sticky="w", padx=10, pady=10)

        def submit():
            try:
                self.menu_service.add_coffee(
                    name=fields[0][1].get(),
                    price=float(fields[1][1].get()),
                    size=fields[2][1].get(),
                    description=fields[3][1].get(),
                    temperature_type=fields[4][1].get(),
                    is_available=fields[5][1].get()
                )
                self.load_data()
                dialog.destroy()
                messagebox.showinfo("Thành công", "Thêm món thành công!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")

        tk.Button(dialog, text="Lưu", command=submit, bg="#4CAF50", fg="white", font=("Arial", 12), relief="flat").grid(row=6, column=1, pady=20)

    def open_edit_dialog(self):
        if not self.selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn món")
            return

        item_id = self.selected_item[0]
        current_item = self.menu_service.get_item_by_id(item_id)

        dialog = tk.Toplevel()
        dialog.title("Chỉnh sửa cà phê")
        dialog.grab_set()

        # Form fields with padding and consistency
        fields = [
            ("Tên món:", tk.Entry(dialog, width=30)),
            ("Giá (VND):", tk.Entry(dialog)),
            ("Size:", ttk.Combobox(dialog, values=["S", "M", "L"])),
            ("Mô tả:", tk.Entry(dialog, width=40)),
            ("Nhiệt độ:", ttk.Combobox(dialog, values=list(self.temp_mapping.keys()))),
            ("Có sẵn:", tk.BooleanVar())
        ]

        # Pre-fill fields
        fields[0][1].insert(0, current_item['name'])
        fields[1][1].insert(0, str(current_item['price']))
        fields[2][1].set(current_item['size'])
        fields[3][1].insert(0, current_item['description'])
        fields[4][1].set(current_item['temperature_type'])
        fields[5][1].set(current_item['is_available'])

        for i, (label, widget) in enumerate(fields):
            tk.Label(dialog, text=label, font=("Arial", 12)).grid(row=i, column=0, padx=10, pady=10, sticky="e")
            if isinstance(widget, tk.Entry):
                widget.grid(row=i, column=1, padx=10, pady=10)
            elif isinstance(widget, ttk.Combobox):
                widget.grid(row=i, column=1, padx=10, pady=10)
            else:
                tk.Checkbutton(dialog, variable=widget).grid(row=i, column=1, sticky="w", padx=10, pady=10)

        def submit():
            try:
                self.menu_service.update_coffee(
                    item_id=item_id,
                    name=fields[0][1].get(),
                    price=float(fields[1][1].get()),
                    size=fields[2][1].get(),
                    description=fields[3][1].get(),
                    temperature_type=fields[4][1].get(),
                    is_available=fields[5][1].get()
                )
                self.load_data()
                dialog.destroy()
                messagebox.showinfo("Thành công", "Cập nhật thành công!")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")

        tk.Button(dialog, text="Lưu", command=submit, bg="#4CAF50", fg="white", font=("Arial", 12), relief="flat").grid(row=6, column=1, pady=20)

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

    def open_create_staff_dialog(self):
        dialog = tk.Toplevel()
        dialog.title("Tạo Staff Mới")
        dialog.grab_set()

        tk.Label(dialog, text="Username:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10)
        entry_username = tk.Entry(dialog, font=("Arial", 12))
        entry_username.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(dialog, text="Password:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10)
        entry_password = tk.Entry(dialog, show="*", font=("Arial", 12))
        entry_password.grid(row=1, column=1, padx=10, pady=10)

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

        tk.Button(dialog, text="Tạo", command=submit, bg="#4CAF50", fg="white", font=("Arial", 12), relief="flat").grid(row=2, column=1, pady=20)

    def open_sales_statistics(self):
        dialog = tk.Toplevel()
        dialog.title("Thống Kê Bán Hàng")
        dialog.geometry("1400x600")

        # Tạo notebook
        notebook = ttk.Notebook(dialog)

        # Tab theo ngày
        daily_frame = ttk.Frame(notebook)
        self.create_statistics_table(
            parent=daily_frame,
            data=self.menu_service.get_daily_sales(),
            columns=("Ngày", "Số Đơn", "Tổng Cốc", "Doanh Thu"),
            title="THỐNG KÊ THEO NGÀY"
        )

        # Tab theo tháng
        monthly_frame = ttk.Frame(notebook)
        self.create_statistics_table(
            parent=monthly_frame,
            data=self.menu_service.get_monthly_sales(),
            columns=("Tháng", "Số Đơn", "Tổng Cốc", "Doanh Thu"),
            title="THỐNG KÊ THEO THÁNG"
        )

        # Tab theo năm
        yearly_frame = ttk.Frame(notebook)
        self.create_statistics_table(
            parent=yearly_frame,
            data=self.menu_service.get_yearly_sales(),
            columns=("Năm", "Số Đơn", "Tổng Cốc", "Doanh Thu"),
            title="THỐNG KÊ THEO NĂM"
        )

        notebook.add(daily_frame, text="Theo Ngày")
        notebook.add(monthly_frame, text="Theo Tháng")
        notebook.add(yearly_frame, text="Theo Năm")
        notebook.pack(expand=True, fill='both', padx=10, pady=10)

    def create_statistics_table(self, parent, data, columns, title):
        # Frame chứa nội dung
        container = ttk.Frame(parent)
        container.pack(fill='both', expand=True, padx=10, pady=10)

        # Tiêu đề
        lbl_title = ttk.Label(
            container,
            text=title,
            font=('Arial', 12, 'bold'),
            foreground="#4CAF50"
        )
        lbl_title.pack(pady=10)

        # Tạo Treeview
        tree = ttk.Treeview(
            container,
            columns=columns,
            show='headings',
            style="Custom.Treeview",
            height=15
        )

        # Định dạng cột
        col_widths = {
            "Ngày": 120,
            "Tháng": 100,
            "Năm": 80,
            "Số Đơn": 100,
            "Tổng Cốc": 120,
            "Doanh Thu": 180
        }

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col,
                        width=col_widths.get(col, 100),
                        anchor='center' if col != "Doanh Thu" else 'e'
                        )

        # Thêm dữ liệu
        for item in data:
            values = (
                item[list(item.keys())[0]],  # Ngày/Tháng/Năm
                item['total_orders'],
                item['total_cups'],
                f"{item['total_revenue']:,.0f}₫"  # Định dạng tiền tệ
            )
            tree.insert('', 'end', values=values)

        # Thanh cuộn
        scroll_y = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll_y.set)

        # Layout
        tree.pack(side='left', fill='both', expand=True)
        scroll_y.pack(side='right', fill='y')

    def run(self):
        self.window.mainloop()