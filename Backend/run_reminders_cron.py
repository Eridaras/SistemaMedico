"""
Cron Job Script - Automatic Reminder Processing
Execute this script every 30 minutes to send appointment reminders

Usage:
    python run_reminders_cron.py

Cron configuration (Linux/Mac):
    */30 * * * * cd /path/to/backend && python run_reminders_cron.py

Windows Task Scheduler:
    Program: C:\Python311\python.exe
    Arguments: C:\path\to\backend\run_reminders_cron.py
    Start in: C:\path\to\backend
    Trigger: Every 30 minutes
"""
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from common.reminder_manager import ReminderManager


def main():
    """Main cron job execution"""
    print("=" * 70)
    print(f"🔔 Automatic Reminder Processing Started")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    try:
        # Create reminder manager
        manager = ReminderManager()

        # Process all scheduled reminders
        stats = manager.process_scheduled_reminders()

        print()
        print("✅ Processing Complete!")
        print("-" * 70)
        print(f"📊 Statistics:")
        print(f"   Total Processed: {stats['total_processed']}")
        print(f"   📧 Emails Sent: {stats['email_sent']}")
        print(f"   📱 WhatsApp Sent: {stats['whatsapp_sent']}")
        print(f"   ❌ Failed: {stats['failed']}")
        print("=" * 70)

        # Exit code 0 for success
        sys.exit(0)

    except Exception as e:
        print()
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print("=" * 70)

        # Exit code 1 for error
        sys.exit(1)


if __name__ == '__main__':
    main()
