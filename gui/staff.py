import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from services.menu import MenuService
from services.order import OrderService
from utils.api import WeatherAPI
from utils.exporter import PDFExporter


class StaffDashboard:
    def __init__(self, user_id):
        self.user_id = user_id
        self.window = tk.Tk()
        self.window.title("Staff Dashboard")
        self.window.geometry("1280x720")
        self.window.configure(bg="#f0f2f5")

        self.cart = []
        self.menu_service = MenuService()
        self.order_service = OrderService()
        self.weather_api = WeatherAPI()

        self.temp_mapping = {
            'hot': ('Nóng 🔥', '#d32f2f'),
            'cold': ('Lạnh ❄️', '#2196F3'),
            'both': ('Cả hai 🌡️', '#4CAF50')
        }

        self.setup_styles()
        self.build_ui()
        self.load_menu()
        self.update_weather_recommendations()

        self.current_filter = None  # Thêm biến lưu trạng thái filter
        self.filter_buttons = {}

    def setup_styles(self):
            style = ttk.Style()
            style.theme_use('clam')

            # Configure Treeview style
            style.configure("Treeview.Heading", font=('Arial', 10, 'bold'), background='#e0e0e0')
            style.configure("Treeview", font=('Arial', 10), rowheight=25)
            style.map("Treeview", background=[('selected', '#3d85c6')])

    def build_ui(self):
        # Main container
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Weather header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        self.weather_label = ttk.Label(
            header_frame,
            text="Đang tải thời tiết...",
            font=('Arial', 10, 'italic'),
            foreground="#666"
        )
        self.weather_label.pack(side=tk.LEFT, padx=5)

        self.recommendation_frame = ttk.Frame(header_frame)
        self.recommendation_frame.pack(side=tk.RIGHT, padx=10)

        # Main content
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Menu section (40% width)
        menu_frame = ttk.LabelFrame(content_frame, text=" Thực đơn ", padding=10)
        menu_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        menu_frame.pack_propagate(False)
        menu_frame.config(width=500)

        self.tree_menu = ttk.Treeview(
            menu_frame,
            columns=("ID", "Tên", "Size", "Nhiệt độ", "Giá"),
            show="headings",
            selectmode='browse'
        )

        # Configure columns
        self.tree_menu.column("ID", width=50, anchor='center')
        self.tree_menu.column("Tên", width=150)
        self.tree_menu.column("Size", width=60, anchor='center')
        self.tree_menu.column("Nhiệt độ", width=80, anchor='center')
        self.tree_menu.column("Giá", width=100, anchor='e')

        # Set headings
        self.tree_menu.heading("ID", text="ID")
        self.tree_menu.heading("Tên", text="Tên món")
        self.tree_menu.heading("Size", text="Size")
        self.tree_menu.heading("Nhiệt độ", text="Nhiệt độ")
        self.tree_menu.heading("Giá", text="Giá (VND)")

        self.tree_menu.pack(fill=tk.BOTH, expand=True)

        # Cart section (60% width)
        cart_frame = ttk.LabelFrame(content_frame, text=" Giỏ hàng ", padding=10)
        cart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        cart_frame.pack_propagate(False)
        cart_frame.config(width=700)

        # Cart treeview
        self.tree_cart = ttk.Treeview(
            cart_frame,
            columns=("ID", "Tên", "Size", "Nhiệt độ", "SL", "Thành tiền"),
            show="headings"
        )

        # Configure columns
        self.tree_cart.column("ID", width=50, anchor='center')
        self.tree_cart.column("Tên", width=200)
        self.tree_cart.column("Size", width=60, anchor='center')
        self.tree_cart.column("Nhiệt độ", width=80, anchor='center')
        self.tree_cart.column("SL", width=60, anchor='center')
        self.tree_cart.column("Thành tiền", width=120, anchor='e')

        # Set headings
        self.tree_cart.heading("ID", text="ID")
        self.tree_cart.heading("Tên", text="Tên món")
        self.tree_cart.heading("Size", text="Size")
        self.tree_cart.heading("Nhiệt độ", text="Nhiệt độ")
        self.tree_cart.heading("SL", text="Số lượng")
        self.tree_cart.heading("Thành tiền", text="Thành tiền (VND)")

        self.tree_cart.pack(fill=tk.BOTH, expand=True)

        # Control buttons
        control_frame = ttk.Frame(cart_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))

        button_style = {
            'font': ('Arial', 10, 'bold'),
            'width': 12,
            'padx': 10,
            'pady': 5
        }

        self.btn_add = tk.Button(
            control_frame,
            text="➕ Thêm",
            command=self.add_to_cart,
            bg="#4CAF50",
            fg="white",
            **button_style
        )
        self.btn_add.pack(side=tk.LEFT, padx=5)

        self.btn_remove = tk.Button(
            control_frame,
            text="❌ Xóa ",
            command=self.remove_from_cart,
            bg="#f44336",
            fg="white",
            **button_style
        )
        self.btn_remove.pack(side=tk.LEFT, padx=5)

        self.btn_checkout = tk.Button(
            control_frame,
            text="💰 Tạo đơn",
            command=self.create_order,
            bg="#2196F3",
            fg="white",
            **button_style
        )
        self.btn_checkout.pack(side=tk.RIGHT, padx=5)

        # Total label
        self.lbl_total = ttk.Label(
            cart_frame,
            text="Tổng tiền: 0 VND",
            font=('Arial', 12, 'bold'),
            foreground="#d32f2f",
            anchor='e'
        )
        self.lbl_total.pack(fill=tk.X, pady=(10, 0))

        self.btn_all = tk.Button(
            control_frame,
            text="🌐 Tất cả",
            command=lambda: self.apply_filter(None),
            bg="#9E9E9E",
            fg="white",
            **button_style
        )
        self.btn_all.pack(side=tk.LEFT, padx=5)

    def load_menu(self, temp_type=None):
        current_temp = self.weather_api.get_weather().get('temp', 25)
        recommendations = self.menu_service.get_recommendations(current_temp)
        rec_ids = [item['item_id'] for item in recommendations]

        if temp_type:
            items = self.menu_service.get_coffees_by_temperature(temp_type)
        else:
            items = self.menu_service.get_available_coffees()

        for item in self.tree_menu.get_children():
            self.tree_menu.delete(item)

        for item in items:
            tags = ('recommended',) if item['item_id'] in rec_ids else ()
            self.tree_menu.insert("", "end", values=(
                item['item_id'],
                item['name'],
                item['size'],
                self.temp_mapping[item['temperature_type']][0], # Lấy phần text
                f"{item['price']:,.0f}"
            ), tags=tags)

        self.tree_menu.tag_configure('recommended', background='#e3f2fd')

    def update_button_styles(self):
        # Reset tất cả button
        for btn in self.filter_buttons.values():
            btn.config(relief="raised", bg="#E0E0E0")
        self.btn_all.config(relief="raised", bg="#9E9E9E")

        # Highlight button đang chọn
        if self.current_filter:
            self.filter_buttons[self.current_filter].config(
                relief="sunken",
                bg=self.temp_mapping[self.current_filter][1]
            )
        else:
            self.btn_all.config(relief="sunken", bg="#757575")

    def add_to_cart(self):
        selected = self.tree_menu.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn món từ menu")
            return

        item_id = self.tree_menu.item(selected[0])['values'][0]

        # Nhập size
        size = simpledialog.askstring("Chọn size", "Nhập size (S/M/L):", initialvalue="M")
        if size is None or size.upper() not in ["S", "M", "L"]:
            messagebox.showerror("Lỗi", "Size không hợp lệ!")
            return
        size = size.upper()

        quantity = simpledialog.askinteger("Số lượng", "Nhập số lượng:", minvalue=1, initialvalue=1)
        if not quantity:
            return

        # Lấy thông tin món
        item = self.menu_service.get_item_by_id(item_id)
        new_item = {
            "item_id": item_id,
            "name": item['name'],
            "price": item['price'],
            "size": size,
            "temperature": item['temperature_type'],
            "quantity": quantity
        }

        # Kiểm tra trùng
        for idx, cart_item in enumerate(self.cart):
            if cart_item['item_id'] == item_id and cart_item['size'] == size:
                self.cart[idx]['quantity'] += quantity
                self.update_cart_display()
                return

        self.cart.append(new_item)
        self.update_cart_display()

    def update_cart_display(self):
        for item in self.tree_cart.get_children():
            self.tree_cart.delete(item)

        total = 0
        for item in self.cart:
            subtotal = item['price'] * item['quantity']
            self.tree_cart.insert("", "end", values=(
                item['item_id'],
                item['name'],
                item['size'],
                self.temp_mapping[item['temperature']][0],
                item['quantity'],
                f"{subtotal:,.0f} VND"
            ))
            total += subtotal

        self.lbl_total.config(text=f"Tổng tiền: {total:,.0f} VND")
        self.btn_checkout.config(state=tk.NORMAL if self.cart else tk.DISABLED)

    def remove_from_cart(self):
        selected = self.tree_cart.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn món trong giỏ")
            return

        item_id = self.tree_cart.item(selected[0])['values'][0]
        size = self.tree_cart.item(selected[0])['values'][2]
        self.cart = [item for item in self.cart if not (item['item_id'] == item_id and item['size'] == size)]
        self.update_cart_display()

    def create_order(self):
        try:
            order_id = self.order_service.create_order(self.user_id, self.cart)
            PDFExporter.export_order(order_id, self.cart, self.lbl_total.cget("text"))

            messagebox.showinfo("Thành công",
                                f"Đã tạo đơn #{order_id}\nHóa đơn đã được xuất ra!")

            self.cart.clear()
            self.update_cart_display()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tạo đơn: {str(e)}")

    def update_weather_recommendations(self):
        try:
            weather = self.weather_api.get_weather()
            temp = weather['temp']
            # temp = 40
            desc = weather['description']

            self.weather_label.config(text=f"{temp}°C - {desc.capitalize()}")

            recommendations = self.menu_service.get_recommendations(temp)

            # Clear old widgets
            for widget in self.recommendation_frame.winfo_children():
                widget.destroy()

            # Thêm nút "Tất cả"
            btn_all = tk.Button(
                self.recommendation_frame,
                text="🌐 Tất cả",
                command=lambda: self.apply_filter(None),
                bg="#9E9E9E",
                fg="white",
                padx=8,
                pady=4
            )
            btn_all.pack(side=tk.LEFT, padx=2)

            # Thêm các nút gợi ý có thể click
            ttk.Label(self.recommendation_frame,
                      text="Gợi ý:",
                      font=('Arial', 9)).pack(side=tk.LEFT, padx=5)

            for item in recommendations[:3]:  # Hiển thị tối đa 3 món
                temp_text, color = self.temp_mapping[item['temperature_type']]

                btn = tk.Button(
                    self.recommendation_frame,
                    text=f"{item['name']} ({temp_text})",
                    fg=color,
                    font=('Arial', 9, 'underline'),
                    cursor="hand2",
                    relief="flat",
                    command=lambda t=item['temperature_type']: self.apply_filter(t)
                )
                btn.pack(side=tk.LEFT, padx=5)

        except Exception as e:
            print(f"Lỗi thời tiết: {str(e)}")

    def apply_filter(self, temp_type):
        """Áp dụng bộ lọc nhiệt độ cho menu"""
        self.current_filter = temp_type
        self.load_menu(temp_type)

        # Cập nhật trạng thái các nút
        self.update_filter_buttons()

    def update_filter_buttons(self):
        """Cập nhật style cho các nút filter"""
        # Lấy tất cả widget trong khung recommendation
        for widget in self.recommendation_frame.winfo_children():
            if isinstance(widget, tk.Button) and "🌐" not in widget.cget("text"):
                # Reset style các nút gợi ý
                widget.config(relief="flat", bg=self.window.cget('bg'))

        # Highlight nút được chọn
        if self.current_filter:
            for widget in self.recommendation_frame.winfo_children():
                if isinstance(widget, tk.Button) and self.current_filter in widget.cget("text"):
                    widget.config(relief="sunken", bg="#f0f0f0")

    def run(self):
        self.window.mainloop()