import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from services.menu import MenuService
from services.order import OrderService
from utils.api import WeatherAPI
from utils.exporter import PDFExporter
from typing import Optional, Dict, List


class StaffDashboard:
    TEMP_MAPPING = {
        'hot': ('Nóng 🔥', '#d32f2f'),
        'cold': ('Lạnh ❄️', '#2196F3'),
        'both': ('Cả hai 🌡️', '#4CAF50')
    }

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.cart: List[Dict] = []
        self.current_filter: Optional[str] = None
        self.search_keyword: str = ""

        # Khởi tạo services
        self.menu_service = MenuService()
        self.order_service = OrderService()
        self.weather_api = WeatherAPI()

        # Cấu hình giao diện
        self.window = self._configure_window()
        self._setup_ui()
        self._load_initial_data()

    # cấu hình
    def _configure_window(self) -> tk.Tk:
        """Cấu hình cửa sổ chính"""
        window = tk.Tk()
        window.title("Staff Dashboard")
        window.geometry("1280x720")
        window.configure(bg="#f0f2f5")
        self._setup_styles()
        return window

    @staticmethod
    def _setup_styles():
        """Cấu hình styles cho các widget"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview.Heading", font=('Arial', 10, 'bold'), background='#e0e0e0')
        style.configure("Treeview", font=('Arial', 10), rowheight=25)
        style.map("Treeview", background=[('selected', '#3d85c6')])
        style.configure('Search.TButton', font=('Arial', 10), padding=5, relief='flat')
    # -----------------

    # UI Setup
    def _setup_ui(self):
        """Xây dựng giao diện người dùng"""
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self._build_header(main_frame)
        self._build_content(main_frame)

    def _build_header(self, parent):
        """Xây dựng phần header"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        # Weather display
        self.weather_label = ttk.Label(
            header_frame,
            text="Đang tải thời tiết...",
            font=('Arial', 10, 'italic'),
            foreground="#666"
        )
        self.weather_label.pack(side=tk.LEFT, padx=5)

        # Recommendation buttons
        self.recommendation_frame = ttk.Frame(header_frame)
        self.recommendation_frame.pack(side=tk.RIGHT, padx=10)

    def _build_content(self, parent):
        """Xây dựng phần nội dung chính"""
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Menu section
        menu_frame = self._build_menu_frame(content_frame)
        self._build_menu_components(menu_frame)

        # Cart section
        cart_frame = self._build_cart_frame(content_frame)
        self._build_cart_components(cart_frame)

    def _build_menu_frame(self, parent) -> ttk.Frame:
        """Xây dựng khung menu"""
        menu_frame = ttk.LabelFrame(parent, text=" Thực đơn ", padding=10)
        menu_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        return menu_frame

    def _build_menu_components(self, parent):
        """Xây dựng các thành phần menu"""
        self._build_search_panel(parent)
        self._build_menu_treeview(parent)

    def _build_search_panel(self, parent):
        """Xây dựng thanh tìm kiếm"""
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        self.search_var = tk.StringVar()
        self.entry_search = ttk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Arial', 11),
            width=30
        )
        self.entry_search.pack(side=tk.LEFT, padx=(0, 5))
        self.entry_search.bind('<KeyRelease>', self._on_search)

        btn_clear_search = ttk.Button(
            search_frame,
            text="Xóa",
            command=self._clear_search,
            style='Search.TButton'
        )
        btn_clear_search.pack(side=tk.LEFT)

    def _build_menu_treeview(self, parent):
        """Xây dựng treeview cho menu"""
        self.tree_menu = ttk.Treeview(
            parent,
            columns=("ID", "Tên", "Size", "Nhiệt độ", "Giá"),
            show="headings",
            selectmode='browse'
        )

        columns = [
            ("ID", 50, 'center'),
            ("Tên", 150, 'w'),
            ("Size", 60, 'center'),
            ("Nhiệt độ", 80, 'center'),
            ("Giá", 100, 'e')
        ]

        for col, width, anchor in columns:
            self.tree_menu.column(col, width=width, anchor=anchor)
            self.tree_menu.heading(col, text=col)

        self.tree_menu.pack(fill=tk.BOTH, expand=True)

    def _build_cart_frame(self, parent) -> ttk.Frame:
        """Xây dựng khung giỏ hàng"""
        cart_frame = ttk.LabelFrame(parent, text=" Giỏ hàng ", padding=10)
        cart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        return cart_frame

    def _build_cart_components(self, parent):
        """Xây dựng các thành phần giỏ hàng"""
        self._build_cart_treeview(parent)
        self._build_cart_controls(parent)

    def _build_cart_treeview(self, parent):
        """Xây dựng treeview cho giỏ hàng"""
        self.tree_cart = ttk.Treeview(
            parent,
            columns=("ID", "Tên", "Size", "Nhiệt độ", "SL", "Thành tiền"),
            show="headings"
        )

        columns = [
            ("ID", 50, 'center'),
            ("Tên", 200, 'w'),
            ("Size", 60, 'center'),
            ("Nhiệt độ", 80, 'center'),
            ("SL", 60, 'center'),
            ("Thành tiền", 120, 'e')
        ]

        for col, width, anchor in columns:
            self.tree_cart.column(col, width=width, anchor=anchor)
            self.tree_cart.heading(col, text=col)

        self.tree_cart.pack(fill=tk.BOTH, expand=True)

    def _build_cart_controls(self, parent):
        """Xây dựng phần điều khiển giỏ hàng"""
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(10, 0))

        # Action buttons
        self._build_cart_action_buttons(control_frame)

        # Total label
        self.lbl_total = ttk.Label(
            parent,
            text="Tổng tiền: 0 VND",
            font=('Arial', 12, 'bold'),
            foreground="#d32f2f",
            anchor='e'
        )
        self.lbl_total.pack(fill=tk.X, pady=(10, 0))

    def _build_cart_action_buttons(self, parent):
        """Xây dựng các nút thao tác giỏ hàng"""
        button_configs = [
            ("➕ Thêm", self._add_to_cart, "#4CAF50", tk.LEFT),
            ("❌ Xóa", self._remove_from_cart, "#f44336", tk.LEFT),
            ("💰 Tạo đơn", self._create_order, "#2196F3", tk.RIGHT)
        ]

        for text, command, color, side in button_configs:
            btn = tk.Button(
                parent,
                text=text,
                command=command,
                bg=color,
                fg="white",
                font=('Arial', 10, 'bold'),
                width=12,
                padx=10,
                pady=5
            )
            if text == "💰 Tạo đơn":
                self.btn_checkout = btn
            btn.pack(side=side, padx=5)
    # ---------------------

    # load data và hiển thị
    def _load_initial_data(self):
        """Tải dữ liệu ban đầu"""
        self._load_menu()
        self._update_weather_recommendations()

    def _load_menu(self, temp_type: Optional[str] = None):
        """Tải danh sách menu"""
        try:
            items = self._get_filtered_items(temp_type)
            recommendations = self._get_recommendations()

            self.tree_menu.delete(*self.tree_menu.get_children())

            for item in items:
                tags = ('recommended',) if item['item_id'] in recommendations else ()
                self._insert_menu_item(item, tags)

            self.tree_menu.tag_configure('recommended', background='#e3f2fd')

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải menu: {str(e)}")

    def _update_cart_display(self):
        """Cập nhật hiển thị giỏ hàng"""
        self.tree_cart.delete(*self.tree_cart.get_children())
        total = 0

        for item in self.cart:
            subtotal = item['price'] * item['quantity']
            total += subtotal
            self._insert_cart_item(item, subtotal)

        self.lbl_total.config(text=f"Tổng tiền: {total:,.0f} VND")
        self._update_checkout_button_state()

    def _insert_menu_item(self, item: Dict, tags: tuple):
        """Thêm item vào treeview menu"""
        self.tree_menu.insert("", "end", values=(
            item['item_id'],
            item['name'],
            item['size'],
            self.TEMP_MAPPING[item['temperature_type']][0],
            f"{item['price']:,.0f}"
        ), tags=tags)

    def _insert_cart_item(self, item: Dict, subtotal: float):
        """Thêm item vào treeview giỏ hàng"""
        self.tree_cart.insert("", "end", values=(
            item['item_id'],
            item['name'],
            item['size'],
            self.TEMP_MAPPING[item['temperature_type']][0],
            item['quantity'],
            f"{subtotal:,.0f} VND"
        ))
    # ----------------------

    # Weather and Recommendations
    def _update_weather_recommendations(self):
        """Cập nhật thông tin thời tiết và đề xuất"""
        try:
            weather = self.weather_api.get_weather() or {}
            self._update_weather_display(weather)
            self._update_recommendation_buttons(weather.get('temp', 25))

        except Exception as e:
            print(f"Lỗi cập nhật thời tiết: {str(e)}")
            self.weather_label.config(text="Không thể cập nhật thời tiết")

    def _update_weather_display(self, weather: Dict):
        """Cập nhật hiển thị thông tin thời tiết"""
        temp = weather.get('temp', 25)
        desc = weather.get('description', 'N/A').capitalize()
        self.weather_label.config(text=f"{temp}°C - {desc}")

    def _update_recommendation_buttons(self, temperature: float):
        """Cập nhật các nút đề xuất theo nhiệt độ"""
        for widget in self.recommendation_frame.winfo_children():
            widget.destroy()

        self._create_filter_buttons()
        self._create_temperature_buttons(temperature)

    def _create_filter_buttons(self):
        """Tạo các nút lọc"""
        btn_all = tk.Button(
            self.recommendation_frame,
            text="🌐 Tất cả",
            command=lambda: self._apply_filter(None),
            bg="#4CAF50" if not self.current_filter else "#E0E0E0",
            fg="white",
            padx=8,
            pady=4
        )
        btn_all.pack(side=tk.LEFT, padx=2)

    def _create_temperature_buttons(self, temperature: float):
        """Tạo các nút lọc nhiệt độ"""
        recommendations = self.menu_service.get_recommendations(temperature)[:3]

        for item in recommendations:
            temp_type = item['temperature_type']
            btn = tk.Button(
                self.recommendation_frame,
                text=f"{item['name']} ({self.TEMP_MAPPING[temp_type][0]})",
                bg=self.TEMP_MAPPING[temp_type][1],
                fg="white",
                padx=8,
                pady=4,
                command=lambda t=temp_type: self._apply_filter(t)
            )
            btn.pack(side=tk.LEFT, padx=2)

    def _apply_filter(self, temp_type: Optional[str]):
        """Áp dụng bộ lọc nhiệt độ"""
        self.current_filter = temp_type
        self._load_menu(temp_type)
        self._update_button_styles()

    def _update_button_styles(self):
        """Cập nhật style cho các nút lọc"""
        for btn in self.recommendation_frame.winfo_children():
            if isinstance(btn, tk.Button):
                btn_text = btn.cget("text").lower()
                temp_type = None

                if 'nóng' in btn_text:
                    temp_type = 'hot'
                elif 'lạnh' in btn_text:
                    temp_type = 'cold'
                elif 'cả hai' in btn_text:
                    temp_type = 'both'
                elif 'tất cả' in btn_text:
                    temp_type = None

                btn.config(relief="sunken" if temp_type == self.current_filter else "raised")
    # ---------------------

    # cart
    def _add_to_cart(self):
        """Thêm món vào giỏ hàng"""
        selected = self.tree_menu.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn món từ menu")
            return

        item_id = self.tree_menu.item(selected[0])['values'][0]
        item = self.menu_service.get_item_by_id(item_id)

        if not self._validate_item_availability(item):
            return

        size = self._get_size_from_user()
        quantity = self._get_quantity_from_user()

        if not size or not quantity:
            return

        self._update_cart(item, size, quantity)

    def _remove_from_cart(self):
        """Xóa món khỏi giỏ hàng"""
        selected = self.tree_cart.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn món trong giỏ")
            return

        item_id = self.tree_cart.item(selected[0])['values'][0]
        size = self.tree_cart.item(selected[0])['values'][2]

        self.cart = [
            item for item in self.cart
            if not (item['item_id'] == item_id and item['size'] == size)
        ]

        self._update_cart_display()

    def _update_cart(self, item: Dict, size: str, quantity: int):
        """Cập nhật giỏ hàng"""
        existing_item = next(
            (i for i in self.cart
             if i['item_id'] == item['item_id'] and i['size'] == size),
            None
        )

        if existing_item:
            existing_item['quantity'] += quantity
        else:
            self.cart.append({
                **item,
                'size': size,
                'quantity': quantity
            })

        self._update_cart_display()

    def _validate_item_availability(self, item: Dict) -> bool:
        """Kiểm tra món có sẵn không"""
        if not item or not item.get('is_available'):
            messagebox.showerror("Lỗi", "Món này hiện không khả dụng!")
            return False
        return True

    def _get_size_from_user(self) -> Optional[str]:
        """Lấy size từ người dùng"""
        size = simpledialog.askstring("Chọn size", "Nhập size (S/M/L):", initialvalue="M")
        if size and size.upper() in {"S", "M", "L"}:
            return size.upper()
        messagebox.showerror("Lỗi", "Size không hợp lệ!")
        return None

    def _get_quantity_from_user(self) -> Optional[int]:
        """Lấy số lượng từ người dùng"""
        quantity = simpledialog.askinteger("Số lượng", "Nhập số lượng:", minvalue=1, initialvalue=1)
        if quantity and quantity > 0:
            return quantity
        messagebox.showerror("Lỗi", "Số lượng không hợp lệ!")
        return None

    def _update_checkout_button_state(self):
        """Cập nhật trạng thái nút thanh toán"""
        state = tk.NORMAL if self.cart else tk.DISABLED
        self.btn_checkout.config(state=state)
    # ---------------------

    # order
    def _create_order(self):
        """Tạo đơn hàng mới"""
        try:
            if not self.cart:
                messagebox.showwarning("Cảnh báo", "Giỏ hàng trống!")
                return

            order_id = self.order_service.create_order(self.user_id, self.cart)
            PDFExporter.export_order(order_id, self.cart, self.lbl_total.cget("text"))

            self._show_order_success(order_id)
            self._clear_cart()

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tạo đơn: {str(e)}")

    def _show_order_success(self, order_id: int):
        """Hiển thị thông báo tạo đơn thành công"""
        messagebox.showinfo(
            "Thành công",
            f"Đã tạo đơn #{order_id}\nHóa đơn đã được xuất ra!"
        )

    def _clear_cart(self):
        """Xóa toàn bộ giỏ hàng"""
        self.cart.clear()
        self._update_cart_display()
    # -----------------

    # Utility
    def _get_filtered_items(self, temp_type: Optional[str]) -> List[Dict]:
        """Lấy danh sách item đã lọc"""
        if self.search_keyword:
            return self.menu_service.search_items(self.search_keyword)

        items = self.menu_service.get_available_coffees()

        if temp_type:
            return [item for item in items if item['temperature_type'] == temp_type]

        return items

    def _get_recommendations(self) -> List[int]:
        """Lấy danh sách ID các món được đề xuất"""
        current_temp = self.weather_api.get_weather().get('temp', 25)
        recommendations = self.menu_service.get_recommendations(current_temp)
        return [item['item_id'] for item in recommendations]

    def _on_search(self, event=None):
        """Xử lý sự kiện tìm kiếm"""
        self.search_keyword = self.search_var.get().strip()
        self._load_menu(self.current_filter)

    def _clear_search(self):
        """Xóa bộ lọc tìm kiếm"""
        self.search_var.set("")
        self.search_keyword = ""
        self._load_menu(self.current_filter)
    # ----------------

    def run(self):
        self.window.mainloop()