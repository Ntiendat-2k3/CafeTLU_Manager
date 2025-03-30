from gui.login import LoginWindow
from services.auth import initialize_admin

if __name__ == "__main__":
    initialize_admin()

    app = LoginWindow()
    app.run()