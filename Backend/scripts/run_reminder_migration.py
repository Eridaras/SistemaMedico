"""
Run Reminder Settings Migration
Creates reminder_settings and reminder_logs tables
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.database import db


def run_migration():
    """Run the reminder settings migration"""

    print("🔧 Running Reminder Settings Migration...")
    print("=" * 60)

    try:
        with db.get_cursor(commit=True) as cursor:
            # Read the SQL migration file
            sql_file = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                'add_reminder_settings.sql'
            )

            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()

            # Execute the migration
            cursor.execute(sql_content)

            print("✅ Migration completed successfully!")
            print()
            print("Tables created:")
            print("  - reminder_settings")
            print("  - reminder_logs")
            print()
            print("Default settings created for existing users:")

            # Show created settings
            cursor.execute("""
                SELECT
                    rs.user_id,
                    u.full_name,
                    u.role,
                    rs.email_enabled,
                    rs.whatsapp_enabled,
                    rs.auto_send_enabled
                FROM reminder_settings rs
                JOIN users u ON rs.user_id = u.user_id
                ORDER BY u.role, u.full_name
            """)

            settings = cursor.fetchall()

            if settings:
                print()
                print("User Settings:")
                print("-" * 60)
                for setting in settings:
                    email_status = "✅" if setting['email_enabled'] else "❌"
                    whatsapp_status = "✅" if setting['whatsapp_enabled'] else "❌"
                    auto_status = "✅" if setting['auto_send_enabled'] else "❌"

                    print(f"  {setting['full_name']} ({setting['role']})")
                    print(f"    Email: {email_status}  WhatsApp: {whatsapp_status}  Auto: {auto_status}")
            else:
                print("  No users found (tables created successfully)")

            print()
            print("=" * 60)
            print("🎉 Migration complete! You can now:")
            print("  1. Start notifications_service: python notifications_service/app.py")
            print("  2. Configure SMTP settings in .env")
            print("  3. Configure Twilio settings in .env")
            print("  4. Test the reminder system")

    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    run_migration()
