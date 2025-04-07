import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, List, Tuple, Optional
from services.menu import MenuService
from services.auth import create_staff, check_username_exists


class AdminDashboard:
    STYLES = {
        'bg_color': "#f4f4f4",
        'primary_color': "#4CAF50",
        'secondary_color': "#388E3C",
        'accent_color': "#81C784",
        'font': ("Arial", 12),
        'title_font': ("Arial", 14, "bold"),
        'tree_style': "Custom.Treeview",
        'button_width': 20,
        'button_height': 2,
        'dialog_padding': 10
    }

    TEMP_MAPPING = {
        'hot': 'Nóng 🔥',
        'cold': 'Lạnh ❄️',
        'both': 'Cả hai 🌡️'
    }

    def __init__(self):
        self.window = self._configure_window()
        self.menu_service = MenuService()
        self.selected_item: Optional[Dict] = None

        self._setup_styles()
        self._build_main_layout()
        self.load_data()

    def _configure_window(self) -> tk.Tk:
        """Cấu hình cửa sổ chính"""
        window = tk.Tk()
        window.title("Admin Dashboard")
        window.geometry("1440x600")
        window.config(bg=self.STYLES['bg_color'])
        return window

    def _setup_styles(self):
        """Cấu hình styles cho các widget"""
        style = ttk.Style()
        style.configure(
            self.STYLES['tree_style'],
            font=self.STYLES['font'],
            background="#E8F5E9",
            fieldbackground="#E8F5E9",
            rowheight=35
        )
        style.configure(
            f"{self.STYLES['tree_style']}.Heading",
            font=("Arial", 12, "bold"),
            background=self.STYLES['accent_color'],
            foreground=self.STYLES['secondary_color']
        )

    def _build_main_layout(self):
        """Xây dựng layout chính"""
        main_frame = tk.Frame(self.window, bg=self.STYLES['bg_color'])
        main_frame.pack(fill=tk.BOTH, expand=True)

        self._build_sidebar(main_frame)
        self._build_content_area(main_frame)

    def _build_sidebar(self, parent):
        """Xây dựng sidebar"""
        sidebar = tk.Frame(parent, bg=self.STYLES['primary_color'], width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self._add_sidebar_title(sidebar)
        self._add_sidebar_buttons(sidebar)

    def _add_sidebar_title(self, parent):
        """Thêm tiêu đề sidebar"""
        title = tk.Label(
            parent,
            text="Quản Lý",
            font=self.STYLES['title_font'],
            bg=self.STYLES['secondary_color'],
            fg="white",
            pady=20
        )
        title.pack(fill=tk.X)

    def _add_sidebar_buttons(self, parent):
        """Thêm các nút chức năng sidebar"""
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
            btn = tk.Button(
                parent,
                text=text,
                command=command,
                bg=self.STYLES['primary_color'],
                fg="white",
                font=self.STYLES['font'],
                relief="flat",
                width=self.STYLES['button_width'],
                height=self.STYLES['button_height']
            )
            btn.pack(pady=5)

    def _build_content_area(self, parent):
        """Xây dựng vùng nội dung chính"""
        content_frame = tk.Frame(parent, bg=self.STYLES['bg_color'])
        content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._add_content_header(content_frame)
        self._build_menu_treeview(content_frame)

    def _add_content_header(self, parent):
        """Thêm tiêu đề nội dung"""
        header = tk.Label(
            parent,
            text="Quản Lý Menu Cà Phê",
            font=("Arial", 18, "bold"),
            bg=self.STYLES['accent_color'],
            fg="white",
            pady=20
        )
        header.pack(fill=tk.X)

    def _build_menu_treeview(self, parent):
        """Xây dựng treeview menu"""
        columns = ("ID", "Tên", "Giá", "Size", "Nhiệt độ", "Trạng thái")

        self.tree = ttk.Treeview(
            parent,
            columns=columns,
            show="headings",
            height=40,
            style=self.STYLES['tree_style']
        )

        column_configs = {
            "ID": {"width": 80, "anchor": "center"},
            "Tên": {"width": 200},
            "Giá": {"width": 120, "anchor": "e"},
            "Size": {"width": 80, "anchor": "center"},
            "Nhiệt độ": {"width": 120},
            "Trạng thái": {"width": 100, "anchor": "center"}
        }

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, **column_configs[col])

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree.bind("<<TreeviewSelect>>", self._on_item_selected)

    def load_data(self):
        """Tải lại dữ liệu menu"""
        self._clear_treeview()
        items = self.menu_service.get_all_coffees()
        self._populate_treeview(items)

    def _clear_treeview(self):
        """Xóa toàn bộ dữ liệu treeview"""
        self.tree.delete(*self.tree.get_children())

    def _populate_treeview(self, items: List[Dict]):
        """Đổ dữ liệu vào treeview"""
        for item in items:
            self.tree.insert("", "end", values=(
                item['item_id'],
                item['name'],
                f"{item['price']:,.0f}",
                item['size'],
                self.TEMP_MAPPING[item['temperature_type']],
                "🟢 Có" if item['is_available'] else "🔴 Hết"
            ))

    def _on_item_selected(self, event):
        """Xử lý sự kiện chọn item"""
        selected = self.tree.selection()
        self.selected_item = self.tree.item(selected[0])["values"] if selected else None

    def _create_form_dialog(self, title: str, fields: List[Tuple]) -> Tuple[tk.Toplevel, list]:
        """Tạo form dialog chung"""
        dialog = tk.Toplevel()
        dialog.title(title)
        dialog.grab_set()

        entries = []
        for i, (label, widget_type, options) in enumerate(fields):
            tk.Label(dialog, text=label, font=self.STYLES['font']).grid(
                row=i, column=0, padx=self.STYLES['dialog_padding'],
                pady=self.STYLES['dialog_padding'], sticky="e"
            )

            if widget_type == tk.Entry:
                widget = tk.Entry(dialog, **options)
            elif widget_type == ttk.Combobox:
                widget = ttk.Combobox(dialog, **options)
            elif widget_type == tk.BooleanVar:
                widget = tk.BooleanVar()
                tk.Checkbutton(dialog, variable=widget).grid(
                    row=i, column=1, sticky="w",
                    padx=self.STYLES['dialog_padding'],
                    pady=self.STYLES['dialog_padding']
                )
            else:
                raise ValueError(f"Widget type {widget_type} không được hỗ trợ")

            if widget_type != tk.BooleanVar:
                widget.grid(
                    row=i, column=1,
                    padx=self.STYLES['dialog_padding'],
                    pady=self.STYLES['dialog_padding']
                )

            entries.append(widget)

        return dialog, entries

    def open_add_dialog(self):
        """Mở dialog thêm món mới"""
        fields = [
            ("Tên món:", tk.Entry, {'width': 30}),
            ("Giá (VND):", tk.Entry, {}),
            ("Size:", ttk.Combobox, {'values': ["S", "M", "L"]}),
            ("Mô tả:", tk.Entry, {'width': 40}),
            ("Nhiệt độ:", ttk.Combobox, {'values': list(self.TEMP_MAPPING.keys())}),
            ("Có sẵn:", tk.BooleanVar, {'value': True})
        ]

        dialog, entries = self._create_form_dialog("Thêm Cà Phê Mới", fields)

        btn_submit = tk.Button(
            dialog,
            text="Lưu",
            command=lambda: self._handle_add_submit(dialog, entries),
            bg=self.STYLES['primary_color'],
            fg="white",
            font=self.STYLES['font']
        )
        btn_submit.grid(row=6, column=1, pady=20)

    def _handle_add_submit(self, dialog: tk.Toplevel, entries: list):
        """Xử lý submit form thêm mới"""
        try:
            self.menu_service.add_coffee(
                name=entries[0].get(),
                price=float(entries[1].get()),
                size=entries[2].get(),
                description=entries[3].get(),
                temperature_type=entries[4].get(),
                is_available=entries[5].get()
            )
            self.load_data()
            dialog.destroy()
            messagebox.showinfo("Thành công", "Thêm món thành công!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")

    def open_edit_dialog(self):
        """Mở dialog chỉnh sửa món"""
        if not self.selected_item:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn món")
            return

        item_id = self.selected_item[0]
        current_item = self.menu_service.get_item_by_id(item_id)

        fields = [
            ("Tên món:", tk.Entry, {'width': 30}),
            ("Giá (VND):", tk.Entry, {}),
            ("Size:", ttk.Combobox, {'values': ["S", "M", "L"]}),
            ("Mô tả:", tk.Entry, {'width': 40}),
            ("Nhiệt độ:", ttk.Combobox, {'values': list(self.TEMP_MAPPING.keys())}),
            ("Có sẵn:", tk.BooleanVar, {})
        ]

        dialog, entries = self._create_form_dialog("Chỉnh sửa cà phê", fields)

        # Điền dữ liệu hiện tại
        entries[0].insert(0, current_item['name'])
        entries[1].insert(0, str(current_item['price']))
        entries[2].set(current_item['size'])
        entries[3].insert(0, current_item['description'])
        entries[4].set(current_item['temperature_type'])
        entries[5].set(current_item['is_available'])

        btn_submit = tk.Button(
            dialog,
            text="Lưu",
            command=lambda: self._handle_edit_submit(dialog, entries, item_id),
            bg=self.STYLES['primary_color'],
            fg="white",
            font=self.STYLES['font']
        )
        btn_submit.grid(row=6, column=1, pady=20)

    def _handle_edit_submit(self, dialog: tk.Toplevel, entries: list, item_id: int):
        """Xử lý submit form chỉnh sửa"""
        try:
            self.menu_service.update_coffee(
                item_id=item_id,
                name=entries[0].get(),
                price=float(entries[1].get()),
                size=entries[2].get(),
                description=entries[3].get(),
                temperature_type=entries[4].get(),
                is_available=entries[5].get()
            )
            self.load_data()
            dialog.destroy()
            messagebox.showinfo("Thành công", "Cập nhật thành công!")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi: {str(e)}")

    def delete_item(self):
        """Xóa món đã chọn"""
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
        """Thay đổi trạng thái có sẵn"""
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
        """Mở dialog tạo staff mới"""
        dialog = tk.Toplevel()
        dialog.title("Tạo Staff Mới")
        dialog.grab_set()

        entries = []  # List để lưu các widget Entry

        # Tạo các trường nhập liệu và lưu vào list entries
        tk.Label(dialog, text="Username:", font=self.STYLES['font']).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        username_entry = tk.Entry(dialog, font=self.STYLES['font'])
        username_entry.grid(row=0, column=1, padx=10, pady=10)
        entries.append(username_entry)

        tk.Label(dialog, text="Password:", font=self.STYLES['font']).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        password_entry = tk.Entry(dialog, show="*", font=self.STYLES['font'])
        password_entry.grid(row=1, column=1, padx=10, pady=10)
        entries.append(password_entry)

        btn_submit = tk.Button(
            dialog,
            text="Tạo",
            command=lambda: self._handle_create_staff(dialog, entries[0].get(), entries[1].get()),
            bg=self.STYLES['primary_color'],
            fg="white",
            font=self.STYLES['font']
        )
        btn_submit.grid(row=2, column=1, pady=20)

    def _handle_create_staff(self, dialog: tk.Toplevel, username: str, password: str):
        """Xử lý tạo staff mới"""
        try:
            # Validate input
            if not username or not password:
                messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ username và password")
                return

            if check_username_exists(username):
                messagebox.showerror("Lỗi", "Username đã tồn tại! Vui lòng chọn username khác")
                return

            if len(password) < 6:
                messagebox.showerror("Lỗi", "Password phải có ít nhất 6 ký tự")
                return

            create_staff(username=username, password=password)
            messagebox.showinfo("Thành công", "Tạo staff thành công!")
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Tạo staff thất bại: {str(e)}")

    def open_sales_statistics(self):
        """Mở thống kê bán hàng"""
        dialog = tk.Toplevel()
        dialog.title("Thống Kê Bán Hàng")
        dialog.geometry("1400x600")

        notebook = ttk.Notebook(dialog)

        # Tạo các tab
        tabs = [
            ("Theo Ngày", self.menu_service.get_daily_sales,
             ("Ngày", "Số Đơn", "Tổng Cốc", "Doanh Thu")),
            ("Theo Tháng", self.menu_service.get_monthly_sales,
             ("Tháng", "Số Đơn", "Tổng Cốc", "Doanh Thu")),
            ("Theo Năm", self.menu_service.get_yearly_sales,
             ("Năm", "Số Đơn", "Tổng Cốc", "Doanh Thu"))
        ]

        for tab_text, data_func, columns in tabs:
            frame = ttk.Frame(notebook)
            self._create_statistics_table(frame, data_func(), columns)
            notebook.add(frame, text=tab_text)

        notebook.pack(expand=True, fill='both', padx=10, pady=10)

    def _create_statistics_table(self, parent, data: List[Dict], columns: Tuple):
        """Tạo bảng thống kê"""
        container = ttk.Frame(parent)
        container.pack(fill='both', expand=True, padx=10, pady=10)

        # Tiêu đề
        lbl_title = ttk.Label(
            container,
            text=f"THỐNG KÊ {columns[0].upper()}",
            font=('Arial', 12, 'bold'),
            foreground=self.STYLES['secondary_color']
        )
        lbl_title.pack(pady=10)

        # Treeview
        tree = ttk.Treeview(
            container,
            columns=columns,
            show='headings',
            style=self.STYLES['tree_style'],
            height=15
        )

        # Cấu hình cột
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
                item[list(item.keys())[0]],
                item['total_orders'],
                item['total_cups'],
                f"{item['total_revenue']:,.0f}₫"
            )
            tree.insert('', 'end', values=values)

        # Thanh cuộn
        scroll_y = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll_y.set)

        # Layout
        tree.pack(side='left', fill='both', expand=True)
        scroll_y.pack(side='right', fill='y')

    def run(self):
        """Chạy ứng dụng"""
        self.window.mainloop()
