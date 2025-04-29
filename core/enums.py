from django.db import models

class UserType(models.IntegerChoices):
    DIETITIAN = 1, 'Dietitian'
    CLIENT = 2, 'Client'
    ADMIN = 3, 'Admin'

class Gender(models.IntegerChoices):
    MALE = 1, 'Male'
    FEMALE = 2, 'Female'
    OTHER = 3, 'Other'

class Status(models.IntegerChoices):
    ACTIVE = 1, 'Active'
    PASSIVE = 2, 'Passive'
    PENDING = 3, 'Pending'
    DELETED = 4, 'Deleted'

class VerificationStatus(models.IntegerChoices):
    PENDING = 1, 'Pending'
    VERIFIED = 2, 'Verified'
    REJECTED = 3, 'Rejected'

class MatchingStatus(models.IntegerChoices):
    PENDING = 1, 'Pending'
    ACCEPTED = 2, 'Accepted'
    REJECTED = 3, 'Rejected'
    ENDED = 4, 'Ended'

class ReviewStatus(models.IntegerChoices):
    PENDING = 1, 'Pending'
    ACCEPTED = 2, 'Accepted'
    REJECTED = 3, 'Rejected'

class Difficulty_Type(models.IntegerChoices):
    EASY= 1, "Easy"
    MEDIUM= 2, "Medium"
    HARD= 3, "Hard"

class Day_Choices(models.IntegerChoices):
    MONDAY= 1, "Monday"
    TUESDAY=2 , "Tuesday"
    WEDNESDAY= 3, "Wednesday"
    THURSDAY=4, "Thursday"
    FRIDAY=5, "Friday"
    SATURDAY=6, "Saturday"
    SUNDAY=7, "Sunday"
