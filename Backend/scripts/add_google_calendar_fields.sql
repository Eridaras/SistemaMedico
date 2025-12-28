-- Add Google Calendar integration fields to appointments table

-- Add google_event_id column to store the Google Calendar event ID
ALTER TABLE appointments ADD COLUMN IF NOT EXISTS google_event_id VARCHAR(255);

-- Add sync_enabled column to users table to control who has Calendar sync enabled
ALTER TABLE users ADD COLUMN IF NOT EXISTS google_calendar_sync BOOLEAN DEFAULT FALSE;

-- Add index for faster lookups
CREATE INDEX IF NOT EXISTS idx_appointments_google_event_id ON appointments(google_event_id);

-- Add notification preferences table
CREATE TABLE IF NOT EXISTS notification_preferences (
    preference_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    low_stock_notifications BOOLEAN DEFAULT TRUE,
    appointment_reminders BOOLEAN DEFAULT TRUE,
    daily_summary_enabled BOOLEAN DEFAULT TRUE,
    summary_time TIME DEFAULT '08:00:00',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Add notification_logs table to track sent notifications
CREATE TABLE IF NOT EXISTS notification_logs (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL, -- 'low_stock', 'appointment_reminder', 'daily_summary'
    title VARCHAR(255) NOT NULL,
    message TEXT,
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    metadata JSONB -- Store additional data like product_id, appointment_id, etc.
);

-- Create index for notification queries
CREATE INDEX IF NOT EXISTS idx_notification_logs_user_id ON notification_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_notification_logs_sent_at ON notification_logs(sent_at);
CREATE INDEX IF NOT EXISTS idx_notification_logs_type ON notification_logs(notification_type);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_notification_preferences_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_notification_preferences_updated_at
    BEFORE UPDATE ON notification_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_notification_preferences_updated_at();

-- Insert default notification preferences for existing users
INSERT INTO notification_preferences (user_id, low_stock_notifications, appointment_reminders, daily_summary_enabled)
SELECT user_id, TRUE, TRUE, TRUE
FROM users
WHERE role IN ('admin', 'doctor')
ON CONFLICT (user_id) DO NOTHING;
