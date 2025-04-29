from django.db import models 

class NotificationType(models.IntegerChoices):
        MATCHING_ACCEPTED= 1, "Matching Accepted"
        MATCHING_REJECTED= 2, "Matching Rejected"
        MATCHING_ENDED= 3, "Matching Ended"
        NEW_REVIEW= 4, "New Review"
    