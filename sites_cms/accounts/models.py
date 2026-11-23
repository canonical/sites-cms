from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """The project's own user model.

    Django cannot swap the user model cleanly once tables exist, so it is
    here from the first migration. People will sign in with their company
    email, so every account needs one and no two accounts may share it.
    """

    email = models.EmailField("email address", unique=True)
