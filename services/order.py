from database.db import Database

class OrderService:
    def __init__(self):
        self.db = Database()

    def create_order(self, user_id, items):
        db = Database()
        try:
            # Tính tổng tiền
            total = 0
            for item in items:
                result = db.fetch(
                    "SELECT price FROM menu WHERE item_id = %s",
                    (item['item_id'],)
                )
                total += result[0]['price'] * item['quantity']

            # Tạo đơn hàng
            order_id = db.execute(
                "INSERT INTO orders (user_id, total) VALUES (%s, %s)",
                (user_id, total)
            )

            # Thêm chi tiết đơn
            for item in items:
                db.execute(
                    """INSERT INTO order_details 
                    (order_id, item_id, size, quantity) 
                    VALUES (%s, %s, %s, %s)""",
                    (
                        order_id,
                        item['item_id'],
                        item['size'],
                        item['quantity'],
                    )
                )

            return order_id


        except Exception as e:
            raise Exception(f"Lỗi tạo đơn: {str(e)}")

    def get_all_orders(self):
        """Lấy tất cả hóa đơn với tổng tiền và số lượng món"""
        query = """
        SELECT 
            o.order_id,
            o.order_date,
            o.total,
            u.username,
            SUM(od.quantity) as total_items
        FROM orders o
        LEFT JOIN users u ON o.user_id = u.user_id
        LEFT JOIN order_details od ON o.order_id = od.order_id
        GROUP BY o.order_id
        ORDER BY o.order_date DESC
        """
        return self.db.fetch(query)

    def get_order_details(self, order_id: int):
        """Lấy chi tiết đơn hàng cụ thể"""
        query = """
        SELECT 
            m.name,
            od.size,
            od.quantity,
            m.price
        FROM order_details od
        JOIN menu m ON od.item_id = m.item_id
        WHERE od.order_id = %s
        """
        return self.db.fetch(query, (order_id,))