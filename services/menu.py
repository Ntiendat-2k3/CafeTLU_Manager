from database.db import Database

class MenuService:
    def get_all_coffees(self):
        db = Database()
        return db.fetch("SELECT * FROM menu")

    def get_available_coffees(self):
        db = Database()
        return db.fetch("SELECT * FROM menu WHERE is_available = TRUE")

    def add_coffee(self, name, price, size, description, temperature_type='hot', is_available=True):
        db = Database()

        if not temperature_type:
            temperature_type = 'hot'

        if is_available is None:
            is_available = True

        if not size:
            size = "S"

        return db.execute(
            """INSERT INTO menu 
            (name, price, size, description, is_available, temperature_type) 
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (name, price, size, description, is_available, temperature_type)
        )

    def search_items(self, keyword):
        db = Database()
        return db.fetch(
            "SELECT * FROM menu WHERE name LIKE %s AND is_available = TRUE",
            (f"%{keyword}%",)
        )

    def update_coffee(self, item_id, name, price, size, description, is_available, temperature_type):
        db = Database()
        db.execute(
            """UPDATE menu SET 
            name=%s, price=%s, size=%s, 
            description=%s, is_available=%s,
            temperature_type=%s 
            WHERE item_id=%s""",
            (name, price, size, description, is_available, temperature_type, item_id)
        )

    def delete_item(self, item_id):
        db = Database()
        db.execute("DELETE FROM menu WHERE item_id = %s", (item_id,))

    def toggle_availability(self, item_id):
        db = Database()
        current = db.fetch("SELECT is_available FROM menu WHERE item_id = %s", (item_id,))[0]
        new_status = not current['is_available']
        db.execute(
            "UPDATE menu SET is_available = %s WHERE item_id = %s",
            (new_status, item_id)
        )

    def get_item_by_id(self, item_id):
        db = Database()
        result = db.fetch("SELECT * FROM menu WHERE item_id = %s", (item_id,))
        return result[0] if result else None

    def get_recommendations(self, temp):
        if temp < 20:
            return self.get_available_coffees_by_temp('hot')
        elif temp > 35:
            return self.get_available_coffees_by_temp('cold')
        else:
            return self.get_available_coffees_by_temp('both')

    def get_available_coffees_by_temp(self, temp_type):
        db = Database()
        return db.fetch(
            "SELECT * FROM menu WHERE is_available = TRUE AND temperature_type IN (%s, 'both')",
            (temp_type,)
        )

    def get_coffees_by_temperature(self, temp_type):
        db = Database()
        return db.fetch(
            """SELECT * FROM menu 
            WHERE is_available = TRUE 
            AND temperature_type IN (%s, 'both')""",
            (temp_type,))

    def get_daily_sales(self):
        db = Database()
        query = """
            SELECT 
                DATE_FORMAT(o.order_date, '%d/%m/%Y') as sale_date,
                COUNT(DISTINCT o.order_id) as total_orders,
                SUM(od.quantity) as total_cups,
                SUM(o.total) as total_revenue
            FROM orders o
            JOIN order_details od ON o.order_id = od.order_id
            GROUP BY sale_date
            ORDER BY o.order_date DESC
            LIMIT 30
        """
        return db.fetch(query)

    def get_monthly_sales(self):
        db = Database()
        query = """
            SELECT 
                DATE_FORMAT(o.order_date, '%m/%Y') as sale_month,
                COUNT(DISTINCT o.order_id) as total_orders,
                SUM(od.quantity) as total_cups,
                SUM(o.total) as total_revenue
            FROM orders o
            JOIN order_details od ON o.order_id = od.order_id
            GROUP BY sale_month
            ORDER BY o.order_date DESC
            LIMIT 12
        """
        return db.fetch(query)

    def get_yearly_sales(self):
        db = Database()
        query = """
            SELECT 
                DATE_FORMAT(o.order_date, '%Y') as sale_year,
                COUNT(DISTINCT o.order_id) as total_orders,
                SUM(od.quantity) as total_cups,
                SUM(o.total) as total_revenue
            FROM orders o
            JOIN order_details od ON o.order_id = od.order_id
            GROUP BY sale_year
            ORDER BY o.order_date DESC
            LIMIT 5
        """
        return db.fetch(query)