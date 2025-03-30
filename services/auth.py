from database.db import Database
import bcrypt

def initialize_admin():
    """Tạo admin nếu chưa tồn tại"""
    db = Database()
    existing_admin = db.fetch("SELECT * FROM users WHERE username = 'admin'")
    if not existing_admin:
        hashed_pw = bcrypt.hashpw(b"admin123", bcrypt.gensalt())
        db.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
            ("admin", hashed_pw.decode(), "admin")
        )

def create_staff(username, password):
    """Chỉ Admin có thể gọi hàm này để tạo staff"""
    db = Database()
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    db.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, 'staff')",
        (username, hashed_pw.decode())
    )

def login(username, password):
    db = Database()
    user = db.fetch("SELECT * FROM users WHERE username = %s", (username,))
    if not user:
        return False, None, None  # Thêm None cho user_id nếu không tìm thấy người dùng
    if bcrypt.checkpw(password.encode(), user[0]['password_hash'].encode()):
        return True, user[0]['role'], user[0]['user_id']  # Thêm user_id vào đây
    return False, None, None  # Trả về None cho role và user_id nếu sai mật khẩu
