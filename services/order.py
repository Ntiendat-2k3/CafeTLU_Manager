from database.db import Database

class OrderService:
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
