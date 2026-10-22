import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database.db import init_db
from app.ui.app_ui import HospitalApp


def main():
    print("=" * 68)
    print("  🏥  HOSPITAL MANAGEMENT SYSTEM — BBAT104 TQM QUALITY GOAL Q03")
    print("  Student: Gautam Bisht | Roll No: 21 (2410301021) | CSE-A")
    print("  Features: Dark Mode | Custom Themes | Dashboard | Search | Calendar")
    print("=" * 68)
    print("[1/2] Initializing SQLite database and verifying seed data...")
    init_db()
    print("[2/2] Launching Tkinter GUI application...")
    app = HospitalApp()
    app.mainloop()


if __name__ == "__main__":
    main()
