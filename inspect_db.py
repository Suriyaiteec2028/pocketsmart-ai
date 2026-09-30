"""
PocketSmart AI – Database Inspector & Viewer Utility
Run this script from the terminal to view and inspect all database records.
Usage:
    python inspect_db.py           # Prints complete summary & recent data
    python inspect_db.py --users   # Lists all registered users
    python inspect_db.py --plans   # Lists all recommendation plans
    python inspect_db.py --saved   # Lists all saved recommendation items
"""

import sys
import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).resolve().parent / "pocketsmart.db"

def get_connection():
    if not DB_FILE.exists():
        print(f"[-] Database file not found at: {DB_FILE}")
        sys.exit(1)
    return sqlite3.connect(DB_FILE)

def print_separator(title=""):
    print("\n" + "=" * 60)
    if title:
        print(f" {title.upper()} ".center(60, "="))
        print("=" * 60)

def show_summary():
    conn = get_connection()
    cur = conn.cursor()
    print_separator("Database Overview & Stats")
    print(f"Database File: {DB_FILE.name}")
    print(f"Full Path:     {DB_FILE}")
    print("-" * 60)
    
    tables = ["users", "recommendation_plans", "saved_recommendations"]
    for table in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            count = cur.fetchone()[0]
            print(f"  • {table.ljust(24)} : {count} record(s)")
        except sqlite3.OperationalError:
            print(f"  • {table.ljust(24)} : Table not found")
    print("-" * 60)
    conn.close()

def show_users():
    conn = get_connection()
    cur = conn.cursor()
    print_separator("Registered Users")
    cur.execute("SELECT id, name, email, created_at FROM users ORDER BY id ASC")
    rows = cur.fetchall()
    
    if not rows:
        print("No users found in database.")
    else:
        print(f"{'ID':<5} | {'Name':<20} | {'Email':<30} | {'Created At':<20}")
        print("-" * 80)
        for r in rows:
            created = str(r[3])[:19] if r[3] else "N/A"
            print(f"{r[0]:<5} | {r[1]:<20} | {r[2]:<30} | {created:<20}")
    conn.close()

def show_plans():
    conn = get_connection()
    cur = conn.cursor()
    print_separator("Recommendation Plans")
    cur.execute("""
        SELECT p.id, u.name, p.planner_type, p.title, p.budget, p.estimated_total, p.created_at 
        FROM recommendation_plans p
        LEFT JOIN users u ON p.user_id = u.id
        ORDER BY p.id DESC
    """)
    rows = cur.fetchall()
    
    if not rows:
        print("No recommendation plans created yet.")
    else:
        print(f"{'ID':<4} | {'User':<15} | {'Type':<9} | {'Title':<22} | {'Budget':<10} | {'Est. Total':<10}")
        print("-" * 80)
        for r in rows:
            user_name = (r[1] or "Unknown")[:14]
            title = (r[3] or "")[:20]
            print(f"{r[0]:<4} | {user_name:<15} | {r[2]:<9} | {title:<22} | Rs.{r[4]:<7.0f} | Rs.{r[5]:<7.0f}")
    conn.close()

def show_saved():
    conn = get_connection()
    cur = conn.cursor()
    print_separator("Saved Recommendations")
    cur.execute("""
        SELECT s.id, u.name, s.item_name, s.item_category, s.platform, s.estimated_price
        FROM saved_recommendations s
        LEFT JOIN users u ON s.user_id = u.id
        ORDER BY s.id DESC
    """)
    rows = cur.fetchall()
    
    if not rows:
        print("No saved items found.")
    else:
        print(f"{'ID':<4} | {'User':<15} | {'Platform':<10} | {'Category':<15} | {'Item Name':<25} | {'Price'}")
        print("-" * 85)
        for r in rows:
            user_name = (r[1] or "Unknown")[:14]
            platform = (r[4] or "General")[:9]
            category = (r[3] or "Misc")[:14]
            item = (r[2] or "")[:24]
            price = f"Rs.{r[5]:.0f}" if r[5] else "N/A"
            print(f"{r[0]:<4} | {user_name:<15} | {platform:<10} | {category:<15} | {item:<25} | {price}")
    conn.close()

if __name__ == "__main__":
    args = sys.argv[1:]
    
    if "--users" in args:
        show_users()
    elif "--plans" in args:
        show_plans()
    elif "--saved" in args:
        show_saved()
    elif "--summary" in args:
        show_summary()
    else:
        # Default: show everything in a clean dashboard
        show_summary()
        show_users()
        show_plans()
        show_saved()
        print("\n[+] To filter by specific section, run:")
        print("    python inspect_db.py --users")
        print("    python inspect_db.py --plans")
        print("    python inspect_db.py --saved\n")
