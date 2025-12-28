"""
Run Google Calendar migration
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.database import db

def run_migration():
    """Run the Google Calendar fields migration"""

    print("🔄 Starting Google Calendar migration...")

    # Read SQL file
    sql_file = os.path.join(os.path.dirname(__file__), 'add_google_calendar_fields.sql')

    with open(sql_file, 'r', encoding='utf-8') as f:
        sql = f.read()

    # Execute migration
    try:
        with db.get_cursor(commit=True) as cursor:
            cursor.execute(sql)

        print("✅ Google Calendar fields added to database successfully!")
        print("\nAdded:")
        print("  - appointments.google_event_id column")
        print("  - users.google_calendar_sync column")
        print("  - notification_preferences table")
        print("  - notification_logs table")
        print("  - Indexes and triggers")

        return True

    except Exception as e:
        print(f"❌ Error running migration: {str(e)}")
        return False

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
