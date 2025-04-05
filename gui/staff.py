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

        self.current_filter = None
        self.search_keyword = ""
        self.filter_buttons = {}

        self.setup_styles()
        self.build_ui()
        self.load_menu()
        self.update_weather_recommendations()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'), background='#e0e0e0')
        style.configure("Treeview", font=('Arial', 10), rowheight=25)
        style.map("Treeview", background=[('selected', '#3d85c6')])
        style.configure('Search.TButton', font=('Arial', 10), padding=5, relief='flat')

    def build_ui(self):
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Header section
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # Weather display
        self.weather_label = ttk.Label(
            header_frame,
            text="Đang tải thời tiết...",
            font=('Arial', 10, 'italic'),
            foreground="#666"
        )
        self.weather_label.pack(side=tk.LEFT, padx=5)

        # Recommendations frame
        self.recommendation_frame = ttk.Frame(header_frame)
        self.recommendation_frame.pack(side=tk.RIGHT, padx=10)

        # Main content
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Menu section
        menu_frame = ttk.LabelFrame(content_frame, text=" Thực đơn ", padding=10)
        menu_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Search panel
        search_frame = ttk.Frame(menu_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        self.search_var = tk.StringVar()
        self.entry_search = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Arial', 11),
            width=30
        )
        self.entry_search.pack(side=tk.LEFT, padx=(0, 5))
        self.entry_search.bind('<KeyRelease>', self.on_search)

        btn_clear_search = ttk.Button(
            search_frame,
            text="Xóa",
            command=self.clear_search,
            style='Search.TButton'
        )
        btn_clear_search.pack(side=tk.LEFT)

        # Menu treeview
        self.tree_menu = ttk.Treeview(
            menu_frame,
            columns=("ID", "Tên", "Size", "Nhiệt độ", "Giá"),
            show="headings",
            selectmode='browse'
        )

        # Treeview configuration
        for col, width, anchor in [("ID", 50, 'center'), ("Tên", 150, 'w'),
                                   ("Size", 60, 'center'), ("Nhiệt độ", 80, 'center'),
                                   ("Giá", 100, 'e')]:
            self.tree_menu.column(col, width=width, anchor=anchor)
            self.tree_menu.heading(col, text=col)

        self.tree_menu.pack(fill=tk.BOTH, expand=True)

        # Cart section
        cart_frame = ttk.LabelFrame(content_frame, text=" Giỏ hàng ", padding=10)
        cart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Cart treeview
        self.tree_cart = ttk.Treeview(
            cart_frame,
            columns=("ID", "Tên", "Size", "Nhiệt độ", "SL", "Thành tiền"),
            show="headings"
        )

        # Cart configuration
        for col, width, anchor in [("ID", 50, 'center'), ("Tên", 200, 'w'),
                                   ("Size", 60, 'center'), ("Nhiệt độ", 80, 'center'),
                                   ("SL", 60, 'center'), ("Thành tiền", 120, 'e')]:
            self.tree_cart.column(col, width=width, anchor=anchor)
            self.tree_cart.heading(col, text=col)

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

        self.lbl_total = ttk.Label(
            cart_frame,
            text="Tổng tiền: 0 VND",
            font=('Arial', 12, 'bold'),
            foreground="#d32f2f",
            anchor='e'
        )
        self.lbl_total.pack(fill=tk.X, pady=(10, 0))

    def load_menu(self, temp_type=None):
        try:
            items = self.menu_service.search_items(self.search_keyword) if self.search_keyword \
                else self.menu_service.get_available_coffees()

            if temp_type:
                items = [item for item in items if item['temperature_type'] == temp_type]

            current_temp = self.weather_api.get_weather().get('temp', 25)
            recommendations = self.menu_service.get_recommendations(current_temp)
            rec_ids = [item['item_id'] for item in recommendations]

            self.tree_menu.delete(*self.tree_menu.get_children())

            for item in items:
                tags = ('recommended',) if item['item_id'] in rec_ids else ()
                self.tree_menu.insert("", "end", values=(
                    item['item_id'],
                    item['name'],
                    item['size'],
                    self.temp_mapping[item['temperature_type']][0],
                    f"{item['price']:,.0f}"
                ), tags=tags)

            self.tree_menu.tag_configure('recommended', background='#e3f2fd')

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải menu: {str(e)}")

    def on_search(self, event=None):
        self.search_keyword = self.search_var.get().strip()
        self.load_menu(self.current_filter)

    def clear_search(self):
        self.search_var.set("")
        self.search_keyword = ""
        self.load_menu(self.current_filter)

    def update_weather_recommendations(self):
        try:
            weather = self.weather_api.get_weather() or {}
            temp = weather.get('temp', 25)
            desc = weather.get('description', 'N/A')

            self.weather_label.config(text=f"{temp}°C - {desc.capitalize()}")

            # Clear old widgets
            for widget in self.recommendation_frame.winfo_children():
                widget.destroy()

            # Add filter buttons
            btn_all = tk.Button(
                self.recommendation_frame,
                text="🌐 Tất cả",
                command=lambda: self.apply_filter(None),
                bg="#4CAF50" if not self.current_filter else "#E0E0E0",
                fg="white",
                padx=8,
                pady=4
            )
            btn_all.pack(side=tk.LEFT, padx=2)

            recommendations = self.menu_service.get_recommendations(temp)[:3]
            for item in recommendations:
                temp_type = item['temperature_type']
                btn = tk.Button(
                    self.recommendation_frame,
                    text=f"{item['name']} ({self.temp_mapping[temp_type][0]})",
                    bg=self.temp_mapping[temp_type][1],
                    fg="white",
                    padx=8,
                    pady=4,
                    command=lambda t=temp_type: self.apply_filter(t)
                )
                btn.pack(side=tk.LEFT, padx=2)
                self.filter_buttons[temp_type] = btn

            self.update_button_styles()

        except Exception as e:
            print(f"Lỗi cập nhật thời tiết: {str(e)}")
            self.weather_label.config(text="Không thể cập nhật thời tiết")

    def apply_filter(self, temp_type):
        self.current_filter = temp_type
        self.load_menu(temp_type)
        self.update_button_styles()

    def update_button_styles(self):
        for btn in self.filter_buttons.values():
            btn.config(relief="raised")
        if self.current_filter in self.filter_buttons:
            self.filter_buttons[self.current_filter].config(relief="sunken")

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

    def run(self):
        self.window.mainloop()