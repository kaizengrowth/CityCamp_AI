import logging
from datetime import datetime, timedelta
from typing import List, Optional

from app.models.meeting import Meeting
from app.models.notification import Notification
from app.models.user import User
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for managing notifications
    Used by the scraper to send meeting alerts
    """

    def __init__(self, db: Session):
        self.db = db

    async def send_meeting_notification(
        self, meeting: Meeting, notification_type: str = "meeting_alert"
    ) -> int:
        """
        Send notifications to users about a new meeting
        Returns the number of notifications created
        """
        try:
            # Get all users who want meeting notifications
            users = (
                self.db.query(User)
                .filter(User.notification_preferences.op("->>")("meetings") == "true")
                .all()
            )

            if not users:
                logger.info("No users have meeting notifications enabled")
                return 0

            notifications_created = 0

            for user in users:
                notification = Notification(
                    user_id=user.id,
                    meeting_id=meeting.id,
                    title=f"New Meeting: {meeting.title}",
                    message=self._create_meeting_message(meeting),
                    notification_type=notification_type,
                    priority="normal",
                    send_email=True,  # Default to email notifications
                    send_sms=False,  # SMS opt-in required
                    send_push=False,  # Push notifications not implemented yet
                )

                self.db.add(notification)
                notifications_created += 1

            self.db.commit()
            logger.info(
                f"Created {notifications_created} meeting notifications "
                f"for meeting {meeting.id}"
            )
            return notifications_created

        except Exception as e:
            logger.error(f"Error sending meeting notifications: {str(e)}")
            self.db.rollback()
            return 0

    async def send_bulk_notifications(
        self, meetings: List[Meeting], notification_type: str = "meeting_alert"
    ) -> int:
        """
        Send notifications for multiple meetings
        Returns total notifications created
        """
        total_notifications = 0

        for meeting in meetings:
            count = await self.send_meeting_notification(meeting, notification_type)
            total_notifications += count

        return total_notifications

    def _create_meeting_message(self, meeting: Meeting) -> str:
        """Create a formatted message for meeting notifications"""
        message_parts = [
            f"A new meeting has been scheduled: {meeting.title}",
            f"Date: {meeting.meeting_date.strftime('%B %d, %Y at %I:%M %p')}",
        ]

        if meeting.location:
            message_parts.append(f"Location: {meeting.location}")

        if meeting.agenda_url:
            message_parts.append(f"Agenda: {meeting.agenda_url}")

        message_parts.append(
            "Log in to CityCamp AI to view more details and set your preferences."
        )

        return "\n\n".join(message_parts)

    async def mark_notification_sent(
        self, notification_id: int, channel: str = "email"
    ) -> bool:
        """
        Mark a notification as sent via a specific channel
        """
        try:
            notification = (
                self.db.query(Notification)
                .filter(Notification.id == notification_id)
                .first()
            )

            if not notification:
                return False

            now = datetime.utcnow()

            if channel == "email":
                notification.email_sent = True
                notification.email_sent_at = now
            elif channel == "sms":
                notification.sms_sent = True
                notification.sms_sent_at = now
            elif channel == "push":
                notification.push_sent = True
                notification.push_sent_at = now

            if not notification.sent_at:
                notification.sent_at = now

            self.db.commit()
            return True

        except Exception as e:
            logger.error(f"Error marking notification as sent: {str(e)}")
            self.db.rollback()
            return False

    async def get_pending_notifications(self) -> List[Notification]:
        """
        Get notifications that need to be sent
        """
        try:
            notifications = (
                self.db.query(Notification)
                .filter(
                    Notification.sent_at.is_(None),
                    Notification.scheduled_for <= datetime.utcnow(),
                )
                .all()
            )

            return notifications

        except Exception as e:
            logger.error(f"Error getting pending notifications: {str(e)}")
            return []

    async def cleanup_old_notifications(
        self, days_old: int = 30, user_id: Optional[int] = None
    ) -> int:
        """
        Clean up old notifications to keep the database tidy
        Returns number of notifications deleted
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            query = self.db.query(Notification).filter(
                Notification.opened.is_(True),
                Notification.created_at < cutoff_date,
            )
            if user_id is not None:
                query = query.filter(Notification.user_id == user_id)
            deleted_count = query.delete()
            self.db.commit()
            logger.info(f"Cleaned up {deleted_count} old notifications")
            return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up notifications: {str(e)}")
            self.db.rollback()
            return 0
