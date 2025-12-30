"""
WhatsApp Service
Handles WhatsApp message sending via Twilio API for appointment reminders
"""
import os
from datetime import datetime


class WhatsAppService:
    """Service for sending WhatsApp messages via Twilio"""

    def __init__(self):
        """Initialize WhatsApp service with Twilio configuration"""
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID', '')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN', '')
        self.from_number = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')  # Twilio Sandbox
        self.enabled = bool(self.account_sid and self.auth_token)

    def _get_twilio_client(self):
        """Get Twilio client"""
        if not self.enabled:
            print("⚠️ Twilio not configured. Set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN")
            return None

        try:
            from twilio.rest import Client
            return Client(self.account_sid, self.auth_token)
        except ImportError:
            print("⚠️ Twilio library not installed. Run: pip install twilio")
            return None
        except Exception as e:
            print(f"⚠️ Error creating Twilio client: {str(e)}")
            return None

    def send_whatsapp_message(self, to_number, message):
        """
        Send WhatsApp message via Twilio

        Args:
            to_number: Recipient phone number (format: +593991234567)
            message: Message content (plain text)

        Returns:
            bool: True if sent successfully, False otherwise
        """
        client = self._get_twilio_client()
        if not client:
            print(f"📱 [DEMO MODE] WhatsApp to {to_number}:")
            print(f"    {message}")
            return False

        try:
            # Format phone number for WhatsApp
            if not to_number.startswith('whatsapp:'):
                to_number = f"whatsapp:{to_number}"

            # Send message
            message_obj = client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )

            print(f"✅ WhatsApp sent successfully to {to_number}")
            print(f"   Message SID: {message_obj.sid}")
            return True

        except Exception as e:
            print(f"❌ Error sending WhatsApp: {str(e)}")
            return False

    def get_appointment_reminder_message(self, appointment_data, hours_before=24):
        """
        Get WhatsApp message template for appointment reminder

        Args:
            appointment_data: Dictionary with appointment information
            hours_before: Hours before appointment for reminder timing

        Returns:
            str: WhatsApp message content
        """
        patient_name = appointment_data.get('patient_name', 'Paciente')
        doctor_name = appointment_data.get('doctor_name', 'Doctor')
        appointment_date = appointment_data.get('appointment_date')
        appointment_time = appointment_data.get('appointment_time')
        reason = appointment_data.get('reason', 'Consulta médica')
        clinic_address = appointment_data.get('clinic_address', 'Av. Principal 123, Quito')
        clinic_phone = appointment_data.get('clinic_phone', '02-123-4567')

        # Parse datetime if string
        if isinstance(appointment_date, str):
            try:
                dt = datetime.fromisoformat(appointment_date.replace('Z', '+00:00'))
                appointment_date = dt.strftime('%d/%m/%Y')
                appointment_time = dt.strftime('%H:%M')
            except:
                pass

        # Determine reminder timing text
        if hours_before == 24:
            timing_text = "mañana"
        elif hours_before < 24:
            timing_text = f"en {hours_before} horas"
        else:
            days = hours_before // 24
            timing_text = f"en {days} día{'s' if days > 1 else ''}"

        message = f"""🏥 *Clínica Bienestar*
_Recordatorio de Cita Médica_

Hola *{patient_name}*,

Le recordamos que tiene una cita médica programada *{timing_text}*.

📅 *Fecha:* {appointment_date}
⏰ *Hora:* {appointment_time}
👨‍⚕️ *Doctor:* Dr. {doctor_name}
📋 *Motivo:* {reason}

⚠️ *Importante:*
• Llegue 10 minutos antes
• Traiga su cédula de identidad
• Si no puede asistir, avísenos

📍 *Ubicación:* {clinic_address}
📞 *Teléfono:* {clinic_phone}

_Gracias por confiar en Clínica Bienestar_

---
_Este es un recordatorio automático_
"""

        return message

    def send_appointment_reminder(self, to_number, appointment_data, hours_before=24):
        """
        Send appointment reminder via WhatsApp

        Args:
            to_number: Patient phone number (format: +593991234567)
            appointment_data: Dictionary with appointment information
            hours_before: Hours before appointment

        Returns:
            bool: True if sent successfully
        """
        message = self.get_appointment_reminder_message(appointment_data, hours_before)
        return self.send_whatsapp_message(to_number, message)

    def send_bulk_reminders(self, reminders_list):
        """
        Send multiple WhatsApp reminders

        Args:
            reminders_list: List of dictionaries with 'to_number' and 'appointment_data'

        Returns:
            dict: Statistics of sent/failed messages
        """
        stats = {
            'total': len(reminders_list),
            'sent': 0,
            'failed': 0
        }

        for reminder in reminders_list:
            to_number = reminder.get('to_number')
            appointment_data = reminder.get('appointment_data')
            hours_before = reminder.get('hours_before', 24)

            if self.send_appointment_reminder(to_number, appointment_data, hours_before):
                stats['sent'] += 1
            else:
                stats['failed'] += 1

        return stats
