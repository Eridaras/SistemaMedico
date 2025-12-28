"""
Google Calendar Integration Module
Handles OAuth 2.0 authentication and bidirectional sync with Google Calendar
"""
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import os
import json
import pickle

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendarService:
    """Google Calendar integration service"""

    def __init__(self, user_id):
        """
        Initialize Google Calendar service for a specific user

        Args:
            user_id: User ID from the database
        """
        self.user_id = user_id
        self.creds = None
        self.service = None
        self.token_path = f'tokens/user_{user_id}_token.pickle'

    def authenticate(self, credentials_path='credentials.json'):
        """
        Authenticate with Google Calendar API using OAuth 2.0

        Args:
            credentials_path: Path to OAuth client credentials JSON file

        Returns:
            bool: True if authentication successful, False otherwise
        """
        # Check if we have valid credentials stored
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                self.creds = pickle.load(token)

        # If there are no (valid) credentials, let the user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {str(e)}")
                    return False
            else:
                if not os.path.exists(credentials_path):
                    print(f"Credentials file not found: {credentials_path}")
                    return False

                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        credentials_path, SCOPES)
                    self.creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Error during OAuth flow: {str(e)}")
                    return False

            # Save the credentials for the next run
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            with open(self.token_path, 'wb') as token:
                pickle.dump(self.creds, token)

        try:
            self.service = build('calendar', 'v3', credentials=self.creds)
            return True
        except Exception as e:
            print(f"Error building calendar service: {str(e)}")
            return False

    def create_event(self, summary, start_time, end_time, description=None, attendees=None):
        """
        Create a new event in Google Calendar

        Args:
            summary: Event title
            start_time: Start datetime (datetime object or ISO format string)
            end_time: End datetime (datetime object or ISO format string)
            description: Event description
            attendees: List of attendee emails

        Returns:
            dict: Created event data including event_id, or None if failed
        """
        if not self.service:
            if not self.authenticate():
                return None

        # Convert datetime objects to ISO format if needed
        if isinstance(start_time, datetime):
            start_time = start_time.isoformat()
        if isinstance(end_time, datetime):
            end_time = end_time.isoformat()

        event = {
            'summary': summary,
            'description': description or '',
            'start': {
                'dateTime': start_time,
                'timeZone': 'America/Guayaquil',  # Ecuador timezone
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'America/Guayaquil',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                    {'method': 'popup', 'minutes': 60},  # 1 hour before
                    {'method': 'popup', 'minutes': 10},  # 10 minutes before
                ],
            },
        }

        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]

        try:
            created_event = self.service.events().insert(
                calendarId='primary',
                body=event,
                sendUpdates='all'  # Send email notifications to attendees
            ).execute()

            return {
                'event_id': created_event.get('id'),
                'link': created_event.get('htmlLink'),
                'status': created_event.get('status')
            }
        except HttpError as error:
            print(f"Error creating Google Calendar event: {error}")
            return None

    def update_event(self, event_id, summary=None, start_time=None, end_time=None,
                    description=None, attendees=None):
        """
        Update an existing Google Calendar event

        Args:
            event_id: Google Calendar event ID
            summary: New event title
            start_time: New start datetime
            end_time: New end datetime
            description: New description
            attendees: New list of attendee emails

        Returns:
            dict: Updated event data, or None if failed
        """
        if not self.service:
            if not self.authenticate():
                return None

        try:
            # Get existing event
            event = self.service.events().get(
                calendarId='primary',
                eventId=event_id
            ).execute()

            # Update fields if provided
            if summary:
                event['summary'] = summary
            if description is not None:
                event['description'] = description
            if start_time:
                if isinstance(start_time, datetime):
                    start_time = start_time.isoformat()
                event['start']['dateTime'] = start_time
            if end_time:
                if isinstance(end_time, datetime):
                    end_time = end_time.isoformat()
                event['end']['dateTime'] = end_time
            if attendees is not None:
                event['attendees'] = [{'email': email} for email in attendees]

            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=event_id,
                body=event,
                sendUpdates='all'
            ).execute()

            return {
                'event_id': updated_event.get('id'),
                'link': updated_event.get('htmlLink'),
                'status': updated_event.get('status')
            }
        except HttpError as error:
            print(f"Error updating Google Calendar event: {error}")
            return None

    def delete_event(self, event_id):
        """
        Delete an event from Google Calendar

        Args:
            event_id: Google Calendar event ID

        Returns:
            bool: True if deleted successfully, False otherwise
        """
        if not self.service:
            if not self.authenticate():
                return False

        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=event_id,
                sendUpdates='all'
            ).execute()
            return True
        except HttpError as error:
            print(f"Error deleting Google Calendar event: {error}")
            return False

    def get_events(self, time_min=None, time_max=None, max_results=100):
        """
        Get events from Google Calendar within a time range

        Args:
            time_min: Start of time range (datetime or ISO string)
            time_max: End of time range (datetime or ISO string)
            max_results: Maximum number of events to return

        Returns:
            list: List of events
        """
        if not self.service:
            if not self.authenticate():
                return []

        if not time_min:
            time_min = datetime.utcnow()
        if isinstance(time_min, datetime):
            time_min = time_min.isoformat() + 'Z'

        if time_max and isinstance(time_max, datetime):
            time_max = time_max.isoformat() + 'Z'

        try:
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            return events_result.get('items', [])
        except HttpError as error:
            print(f"Error getting Google Calendar events: {error}")
            return []

    def sync_appointment_to_calendar(self, appointment_data):
        """
        Sync an appointment from the database to Google Calendar

        Args:
            appointment_data: Dictionary with appointment information
                - appointment_id: int
                - patient_name: str
                - doctor_name: str
                - start_time: datetime or str
                - end_time: datetime or str
                - reason: str
                - patient_email: str (optional)
                - google_event_id: str (optional, for updates)

        Returns:
            str: Google Calendar event ID, or None if failed
        """
        summary = f"Cita: {appointment_data['patient_name']}"
        description = f"""
Paciente: {appointment_data['patient_name']}
Doctor: {appointment_data['doctor_name']}
Motivo: {appointment_data.get('reason', 'No especificado')}
ID de Cita: #{appointment_data['appointment_id']}
        """.strip()

        attendees = []
        if appointment_data.get('patient_email'):
            attendees.append(appointment_data['patient_email'])

        # If event already exists, update it
        if appointment_data.get('google_event_id'):
            result = self.update_event(
                event_id=appointment_data['google_event_id'],
                summary=summary,
                start_time=appointment_data['start_time'],
                end_time=appointment_data['end_time'],
                description=description,
                attendees=attendees
            )
        else:
            # Create new event
            result = self.create_event(
                summary=summary,
                start_time=appointment_data['start_time'],
                end_time=appointment_data['end_time'],
                description=description,
                attendees=attendees
            )

        return result['event_id'] if result else None

    def remove_appointment_from_calendar(self, google_event_id):
        """
        Remove an appointment from Google Calendar

        Args:
            google_event_id: Google Calendar event ID

        Returns:
            bool: True if deleted successfully
        """
        return self.delete_event(google_event_id)


class CalendarSyncManager:
    """Manages bidirectional sync between database and Google Calendar"""

    @staticmethod
    def sync_appointment_create(appointment_id, doctor_id):
        """
        Sync a newly created appointment to Google Calendar

        Args:
            appointment_id: Database appointment ID
            doctor_id: Doctor's user ID

        Returns:
            str: Google event ID or None
        """
        from common.database import db

        # Get appointment details
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT
                    a.appointment_id,
                    a.start_time,
                    a.end_time,
                    a.reason,
                    p.first_name || ' ' || p.last_name as patient_name,
                    p.email as patient_email,
                    u.full_name as doctor_name
                FROM appointments a
                LEFT JOIN patients p ON a.patient_id = p.patient_id
                LEFT JOIN users u ON a.doctor_id = u.user_id
                WHERE a.appointment_id = %s
            """, (appointment_id,))

            appointment = cursor.fetchone()
            if not appointment:
                return None

        # Create Google Calendar service for doctor
        calendar_service = GoogleCalendarService(doctor_id)

        # Sync to Google Calendar
        google_event_id = calendar_service.sync_appointment_to_calendar(appointment)

        if google_event_id:
            # Store Google event ID in database
            with db.get_cursor(commit=True) as cursor:
                cursor.execute("""
                    UPDATE appointments
                    SET google_event_id = %s
                    WHERE appointment_id = %s
                """, (google_event_id, appointment_id))

        return google_event_id

    @staticmethod
    def sync_appointment_update(appointment_id, doctor_id):
        """
        Sync appointment updates to Google Calendar

        Args:
            appointment_id: Database appointment ID
            doctor_id: Doctor's user ID

        Returns:
            bool: True if synced successfully
        """
        from common.database import db

        # Get appointment details including Google event ID
        with db.get_cursor() as cursor:
            cursor.execute("""
                SELECT
                    a.appointment_id,
                    a.start_time,
                    a.end_time,
                    a.reason,
                    a.google_event_id,
                    p.first_name || ' ' || p.last_name as patient_name,
                    p.email as patient_email,
                    u.full_name as doctor_name
                FROM appointments a
                LEFT JOIN patients p ON a.patient_id = p.patient_id
                LEFT JOIN users u ON a.doctor_id = u.user_id
                WHERE a.appointment_id = %s
            """, (appointment_id,))

            appointment = cursor.fetchone()
            if not appointment:
                return False

        calendar_service = GoogleCalendarService(doctor_id)

        # Sync to Google Calendar
        google_event_id = calendar_service.sync_appointment_to_calendar(appointment)

        return google_event_id is not None

    @staticmethod
    def sync_appointment_delete(appointment_id, doctor_id, google_event_id):
        """
        Remove appointment from Google Calendar

        Args:
            appointment_id: Database appointment ID
            doctor_id: Doctor's user ID
            google_event_id: Google Calendar event ID

        Returns:
            bool: True if deleted successfully
        """
        if not google_event_id:
            return True  # Nothing to delete

        calendar_service = GoogleCalendarService(doctor_id)
        return calendar_service.remove_appointment_from_calendar(google_event_id)
