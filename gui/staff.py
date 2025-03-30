import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from services.menu import MenuService
from services.order import OrderService
from utils.exporter import PDFExporter

class StaffDashboard:
    def __init__(self, user_id):
        self.user_id = user_id
        self.window = tk.Tk()
        self.window.title("Staff Dashboard")
        self.window.geometry("1200x800")

        self.cart = []
        self.menu_service = MenuService()
        self.order_service = OrderService()

        self.build_ui()
        self.load_menu()

    def build_ui(self):
        # Phần menu
        menu_frame = tk.Frame(self.window)
        menu_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        weather_frame = tk.Frame(self.window)
        weather_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # Hiển thị thông tin thời tiết
        self.lbl_weather = tk.Label(
            weather_frame,
            text="Đang tải thời tiết...",
            font=("Arial", 10, "italic"),
            fg="#666"
        )
        self.lbl_weather.pack(side=tk.LEFT)

        # Frame gợi ý
        self.recommendation_frame = tk.Frame(weather_frame)
        self.recommendation_frame.pack(side=tk.RIGHT)

        # Treeview menu
        self.tree_menu = ttk.Treeview(
            menu_frame,
            columns=("ID", "Tên", "Size", "Giá"),
            show="headings",
            height=25
        )
        self.tree_menu.heading("ID", text="ID")
        self.tree_menu.heading("Tên", text="Tên món")
        self.tree_menu.heading("Size", text="Size")
        self.tree_menu.heading("Giá", text="Giá (VND)")
        self.tree_menu.pack(fill=tk.BOTH, expand=True)

        # Phần giỏ hàng
        cart_frame = tk.Frame(self.window)
        cart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Treeview giỏ hàng
        self.tree_cart = ttk.Treeview(
            cart_frame,
            columns=("ID", "Tên", "Size", "SL", "Thành tiền"),
            show="headings",
            height=15
        )
        self.tree_cart.heading("ID", text="ID")
        self.tree_cart.heading("Tên", text="Tên món")
        self.tree_cart.heading("Size", text="Size")
        self.tree_cart.heading("SL", text="Số lượng")
        self.tree_cart.heading("Thành tiền", text="Thành tiền")
        self.tree_cart.pack(fill=tk.BOTH, expand=True)

        # Control buttons
        control_frame = tk.Frame(cart_frame)
        control_frame.pack(pady=10)

        self.btn_add = tk.Button(
            control_frame,
            text="Thêm vào đơn",
            command=self.add_to_cart,
            bg="#4CAF50",
            fg="white"
        )
        self.btn_add.pack(side=tk.LEFT, padx=5)

        self.btn_remove = tk.Button(
            control_frame,
            text="Xóa món",
            command=self.remove_from_cart,
            bg="#f44336",
            fg="white"
        )
        self.btn_remove.pack(side=tk.LEFT, padx=5)

        self.btn_checkout = tk.Button(
            control_frame,
            text="Tạo đơn",
            command=self.create_order,
            bg="#2196F3",
            fg="white"
        )
        self.btn_checkout.pack(side=tk.RIGHT, padx=5)

        # Hiển thị tổng tiền
        self.lbl_total = tk.Label(
            cart_frame,
            text="Tổng tiền: 0 VND",
            font=("Arial", 14, "bold"),
            fg="red"
        )
        self.lbl_total.pack(pady=10)

    def load_menu(self):
        for item in self.tree_menu.get_children():
            self.tree_menu.delete(item)

        items = self.menu_service.get_available_coffees()
        for item in items:
            self.tree_menu.insert("", "end", values=(
                item['item_id'],
                item['name'],
                item['size'],
                f"{item['price']:,.0f}"
            ))

    def add_to_cart(self):
        selected = self.tree_menu.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn món từ menu")
            return

        item_id = self.tree_menu.item(selected[0])['values'][0]

        # Nhập size với kiểm tra nếu người dùng hủy bỏ (None)
        size = simpledialog.askstring("Chọn size", "Nhập size (S/M/L):", initialvalue="M")

        # Kiểm tra nếu giá trị là None (người dùng hủy bỏ) hoặc size không hợp lệ
        if size is None or size.upper() not in ["S", "M", "L"]:
            messagebox.showerror("Lỗi", "Size không hợp lệ hoặc bạn đã hủy bỏ!")
            return

        size = size.upper()  # Chuyển đổi size về chữ in hoa

        quantity = simpledialog.askinteger("Số lượng", "Nhập số lượng:", minvalue=1, initialvalue=1)

        if not quantity:
            return

        # Kiểm tra đã có trong giỏ chưa
        for item in self.cart:
            if item['item_id'] == item_id and item['size'] == size:
                item['quantity'] += quantity
                self.update_cart_display()
                return

        # Thêm mới vào giỏ
        item = self.menu_service.get_item_by_id(item_id)
        self.cart.append({
            "item_id": item_id,
            "name": item['name'],
            "price": item['price'],
            "size": size,
            "quantity": quantity
        })
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
                item['quantity'],
                f"{subtotal:,.0f} VND"
            ))
            total += subtotal

        self.lbl_total.config(text=f"Tổng tiền: {total:,.0f} VND")
        self.btn_checkout.config(state=tk.NORMAL if self.cart else tk.DISABLED)

    def remove_from_cart(self):
        selected = self.tree_cart.selection()
        if not selected:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn món trong giỏ hàng để xóa")
            return

        item_id = self.tree_cart.item(selected[0])['values'][0]
        size = self.tree_cart.item(selected[0])['values'][2]

        # Tìm và xóa món trong giỏ
        self.cart = [item for item in self.cart if not (item['item_id'] == item_id and item['size'] == size)]
        self.update_cart_display()

        messagebox.showinfo("Thành công", "Đã xóa món khỏi giỏ!")

    def create_order(self):
        try:
            order_id = self.order_service.create_order(self.user_id, self.cart)
            PDFExporter.export_order(order_id, self.cart, self.lbl_total.cget("text"))

            messagebox.showinfo("Thành công",
                                f"Đã tạo đơn #{order_id}\nHóa đơn đã được xuất ra file PDF!")

            self.cart.clear()
            self.update_cart_display()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi tạo đơn: {str(e)}")

    def run(self):
        self.window.mainloop()
