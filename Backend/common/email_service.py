"""
Email Service
Handles email sending with HTML templates for appointment reminders
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from datetime import datetime
import os


class EmailService:
    """Service for sending emails with templates"""

    def __init__(self):
        """Initialize email service with SMTP configuration"""
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_user = os.getenv('SMTP_USER', '')
        self.smtp_password = os.getenv('SMTP_PASSWORD', '')
        self.from_email = os.getenv('FROM_EMAIL', self.smtp_user)
        self.from_name = os.getenv('FROM_NAME', 'Clínica Bienestar')

    def _get_smtp_connection(self):
        """Get SMTP connection"""
        try:
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            server.starttls()
            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)
            return server
        except Exception as e:
            print(f"Error connecting to SMTP server: {str(e)}")
            return None

    def send_email(self, to_email, subject, html_content, text_content=None):
        """
        Send email with HTML content

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text fallback (optional)

        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email

            # Plain text version (fallback)
            if text_content:
                part1 = MIMEText(text_content, 'plain')
                msg.attach(part1)

            # HTML version
            part2 = MIMEText(html_content, 'html')
            msg.attach(part2)

            # Send email
            server = self._get_smtp_connection()
            if not server:
                return False

            server.sendmail(self.from_email, to_email, msg.as_string())
            server.quit()

            print(f"✅ Email sent successfully to {to_email}")
            return True

        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")
            return False

    def get_appointment_reminder_template(self, appointment_data, hours_before=24):
        """
        Get HTML template for appointment reminder

        Args:
            appointment_data: Dictionary with appointment information
            hours_before: Hours before appointment for reminder timing

        Returns:
            tuple: (html_content, text_content)
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
                appointment_date = dt.strftime('%d de %B de %Y')
                appointment_time = dt.strftime('%H:%M')
            except:
                pass

        # Determine reminder timing text
        timing_text = "mañana" if hours_before == 24 else f"en {hours_before} horas"

        html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recordatorio de Cita Médica</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td align="center" style="padding: 40px 0;">
                <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">

                    <!-- Header -->
                    <tr>
                        <td style="padding: 40px 40px 20px 40px; background: linear-gradient(135deg, #197fe6 0%, #1565c0 100%); border-radius: 8px 8px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: 600; text-align: center;">
                                🏥 Clínica Bienestar
                            </h1>
                            <p style="margin: 10px 0 0 0; color: #e3f2fd; font-size: 14px; text-align: center;">
                                Sistema de Gestión Médica
                            </p>
                        </td>
                    </tr>

                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 40px;">
                            <h2 style="margin: 0 0 20px 0; color: #197fe6; font-size: 24px; font-weight: 600;">
                                📅 Recordatorio de Cita
                            </h2>

                            <p style="margin: 0 0 20px 0; color: #333333; font-size: 16px; line-height: 1.6;">
                                Hola <strong>{patient_name}</strong>,
                            </p>

                            <p style="margin: 0 0 30px 0; color: #555555; font-size: 16px; line-height: 1.6;">
                                Le recordamos que tiene una cita médica programada <strong>{timing_text}</strong>.
                            </p>

                            <!-- Appointment Details Card -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 30px;">
                                <tr>
                                    <td style="padding: 25px;">
                                        <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                            <tr>
                                                <td style="padding: 8px 0; color: #666666; font-size: 14px;">
                                                    <strong>📆 Fecha:</strong>
                                                </td>
                                                <td style="padding: 8px 0; color: #333333; font-size: 14px; text-align: right;">
                                                    {appointment_date}
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; color: #666666; font-size: 14px;">
                                                    <strong>⏰ Hora:</strong>
                                                </td>
                                                <td style="padding: 8px 0; color: #333333; font-size: 14px; text-align: right;">
                                                    {appointment_time}
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; color: #666666; font-size: 14px;">
                                                    <strong>👨‍⚕️ Doctor:</strong>
                                                </td>
                                                <td style="padding: 8px 0; color: #333333; font-size: 14px; text-align: right;">
                                                    Dr. {doctor_name}
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; color: #666666; font-size: 14px;">
                                                    <strong>📋 Motivo:</strong>
                                                </td>
                                                <td style="padding: 8px 0; color: #333333; font-size: 14px; text-align: right;">
                                                    {reason}
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>

                            <!-- Important Notes -->
                            <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin-bottom: 30px; border-radius: 4px;">
                                <p style="margin: 0; color: #856404; font-size: 14px; line-height: 1.6;">
                                    <strong>⚠️ Importante:</strong><br>
                                    • Por favor, llegue 10 minutos antes de su cita<br>
                                    • Traiga su cédula de identidad<br>
                                    • Si no puede asistir, avísenos con anticipación
                                </p>
                            </div>

                            <!-- Contact Information -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
                                <tr>
                                    <td style="padding: 15px; background-color: #e3f2fd; border-radius: 8px;">
                                        <p style="margin: 0 0 10px 0; color: #1976d2; font-size: 16px; font-weight: 600;">
                                            📍 Ubicación
                                        </p>
                                        <p style="margin: 0 0 8px 0; color: #555555; font-size: 14px;">
                                            {clinic_address}
                                        </p>
                                        <p style="margin: 0; color: #555555; font-size: 14px;">
                                            📞 {clinic_phone}
                                        </p>
                                    </td>
                                </tr>
                            </table>

                            <!-- Action Button -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse; margin: 30px 0;">
                                <tr>
                                    <td align="center">
                                        <a href="tel:{clinic_phone.replace('-', '')}" style="display: inline-block; padding: 14px 40px; background-color: #197fe6; color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 16px; font-weight: 600;">
                                            📞 Llamar para Confirmar
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 40px; background-color: #f8f9fa; border-radius: 0 0 8px 8px; border-top: 1px solid #e0e0e0;">
                            <p style="margin: 0 0 10px 0; color: #666666; font-size: 14px; text-align: center;">
                                Gracias por confiar en <strong>Clínica Bienestar</strong>
                            </p>
                            <p style="margin: 0; color: #999999; font-size: 12px; text-align: center;">
                                Este es un recordatorio automático. Por favor, no responda a este correo.
                            </p>
                            <p style="margin: 10px 0 0 0; color: #999999; font-size: 12px; text-align: center;">
                                © 2025 Clínica Bienestar. Todos los derechos reservados.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """

        text_content = f"""
RECORDATORIO DE CITA MÉDICA - Clínica Bienestar

Hola {patient_name},

Le recordamos que tiene una cita médica programada {timing_text}.

DETALLES DE LA CITA:
📆 Fecha: {appointment_date}
⏰ Hora: {appointment_time}
👨‍⚕️ Doctor: Dr. {doctor_name}
📋 Motivo: {reason}

IMPORTANTE:
• Por favor, llegue 10 minutos antes de su cita
• Traiga su cédula de identidad
• Si no puede asistir, avísenos con anticipación

UBICACIÓN:
📍 {clinic_address}
📞 {clinic_phone}

Gracias por confiar en Clínica Bienestar.

---
Este es un recordatorio automático. Por favor, no responda a este correo.
© 2025 Clínica Bienestar. Todos los derechos reservados.
        """

        return html_content, text_content

    def send_appointment_reminder(self, to_email, appointment_data, hours_before=24):
        """
        Send appointment reminder email

        Args:
            to_email: Patient email address
            appointment_data: Dictionary with appointment information
            hours_before: Hours before appointment

        Returns:
            bool: True if sent successfully
        """
        html_content, text_content = self.get_appointment_reminder_template(
            appointment_data,
            hours_before
        )

        subject = f"🔔 Recordatorio: Cita Médica - {appointment_data.get('appointment_date', 'Próximamente')}"

        return self.send_email(to_email, subject, html_content, text_content)
