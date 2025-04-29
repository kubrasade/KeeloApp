from core.enums import MatchingStatus
from .enums import NotificationType
from notifications.tasks import send_notification_email 

class NotificationService:
    @staticmethod
    def send_matching_status_notification(matching, old_status, new_status):
        from notifications.models import Notification
        
        if new_status == MatchingStatus.ACCEPTED:
            Notification.objects.create(
                user=matching.client.user,
                title="Match Approved",
                message=f"Your match with {matching.dietitian.user.get_full_name()} has been approved.",
                notification_type=NotificationType.MATCHING_ACCEPTED
            )
            send_notification_email.delay(
                matching.client.user.email,
                "Your Match Has Been Approved",
                f"Your match with {matching.dietitian.user.get_full_name()} has been approved. You can now start your journey together!"
            )

        elif new_status == MatchingStatus.REJECTED:
            Notification.objects.create(
                user=matching.client.user,
                title="Match Rejected",
                message=f"Your match request with {matching.dietitian.user.get_full_name()} has been rejected.",
                notification_type=NotificationType.MATCHING_REJECTED
            )
            send_notification_email.delay(
                matching.client.user.email,
                "Your Match Request Has Been Rejected",
                f"Unfortunately, your match request with {matching.dietitian.user.get_full_name()} has been rejected. You can try connecting with another dietitian."
            )

        elif new_status == MatchingStatus.ENDED:
            Notification.objects.create(
                user=matching.client.user,
                title="Match Ended",
                message=f"Your match with {matching.dietitian.user.get_full_name()} has ended.",
                notification_type=NotificationType.MATCHING_ENDED
            )
            send_notification_email.delay(
                matching.client.user.email,
                "Your Match Has Ended",
                f"Your match with {matching.dietitian.user.get_full_name()} has ended. You can find a new dietitian through the platform."
            )

    @staticmethod
    def send_review_notification(review):
        from notifications.models import Notification
        
        Notification.objects.create(
            user=review.matching.dietitian.user,
            title="New Review Received",
            message=f"{review.matching.client.user.get_full_name()} has submitted a new review for you.",
            notification_type=NotificationType.NEW_REVIEW
        )

        send_notification_email.delay(
            review.matching.dietitian.user.email,
            "You Received a New Review",
            f"{review.matching.client.user.get_full_name()} has submitted a new review for you. Please log in to the platform to view the details."
        )