-- Add reminder settings for appointment notifications

-- Reminder settings per user (doctors/admins can configure for their patients)
CREATE TABLE IF NOT EXISTS reminder_settings (
    setting_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,

    -- Email settings
    email_enabled BOOLEAN DEFAULT TRUE,
    email_hours_before JSONB DEFAULT '[24, 3]'::jsonb, -- Array of hours: 24h and 3h before

    -- WhatsApp settings
    whatsapp_enabled BOOLEAN DEFAULT FALSE,
    whatsapp_hours_before JSONB DEFAULT '[24]'::jsonb, -- Array of hours: 24h before

    -- Global settings
    auto_send_enabled BOOLEAN DEFAULT TRUE, -- Enable automatic sending
    send_on_days JSONB DEFAULT '["mon", "tue", "wed", "thu", "fri", "sat", "sun"]'::jsonb, -- Days to send
    quiet_hours_start TIME DEFAULT '22:00:00', -- Don't send after this time
    quiet_hours_end TIME DEFAULT '08:00:00', -- Don't send before this time

    -- SMTP/Email configuration (optional override)
    smtp_host VARCHAR(255),
    smtp_port INTEGER,
    smtp_user VARCHAR(255),
    smtp_password VARCHAR(255),
    from_email VARCHAR(255),
    from_name VARCHAR(255),

    -- Twilio/WhatsApp configuration (optional override)
    twilio_account_sid VARCHAR(255),
    twilio_auth_token VARCHAR(255),
    twilio_whatsapp_number VARCHAR(50),

    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(user_id)
);

-- Reminder logs to track sent reminders
CREATE TABLE IF NOT EXISTS reminder_logs (
    log_id SERIAL PRIMARY KEY,
    appointment_id INTEGER REFERENCES appointments(appointment_id) ON DELETE CASCADE,
    patient_id INTEGER REFERENCES patients(patient_id) ON DELETE CASCADE,

    -- Reminder details
    reminder_type VARCHAR(20) NOT NULL, -- 'email' or 'whatsapp'
    hours_before INTEGER NOT NULL,

    -- Status
    status VARCHAR(20) NOT NULL, -- 'pending', 'sent', 'failed'
    sent_at TIMESTAMP,
    error_message TEXT,

    -- Recipient info
    recipient_email VARCHAR(255),
    recipient_phone VARCHAR(50),

    -- Message content (for debugging)
    message_content TEXT,

    -- Audit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Index for efficient queries
    INDEX idx_reminder_logs_appointment (appointment_id),
    INDEX idx_reminder_logs_status (status),
    INDEX idx_reminder_logs_sent_at (sent_at)
);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_reminder_settings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_reminder_settings_updated_at
    BEFORE UPDATE ON reminder_settings
    FOR EACH ROW
    EXECUTE FUNCTION update_reminder_settings_updated_at();

-- Insert default settings for existing users (admins and doctors)
INSERT INTO reminder_settings (
    user_id,
    email_enabled,
    email_hours_before,
    whatsapp_enabled,
    whatsapp_hours_before,
    auto_send_enabled
)
SELECT
    user_id,
    TRUE,
    '[24, 3]'::jsonb,
    FALSE,
    '[24]'::jsonb,
    TRUE
FROM users
WHERE role IN ('admin', 'doctor')
ON CONFLICT (user_id) DO NOTHING;

-- Add default global settings (clinic-wide)
INSERT INTO reminder_settings (
    user_id,
    email_enabled,
    email_hours_before,
    whatsapp_enabled,
    whatsapp_hours_before,
    auto_send_enabled,
    smtp_host,
    smtp_port,
    from_name
)
SELECT
    1, -- Admin user ID
    TRUE,
    '[72, 24, 3]'::jsonb, -- 3 days, 1 day, 3 hours before
    TRUE,
    '[24, 3]'::jsonb, -- 1 day, 3 hours before
    TRUE,
    'smtp.gmail.com',
    587,
    'Clínica Bienestar'
ON CONFLICT (user_id) DO UPDATE SET
    email_hours_before = EXCLUDED.email_hours_before,
    whatsapp_hours_before = EXCLUDED.whatsapp_hours_before;
