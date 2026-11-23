import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from accounts.models import User


def test_the_project_uses_its_own_user_model():
    assert get_user_model() is User


@pytest.mark.django_db
def test_two_accounts_cannot_share_an_email():
    User.objects.create_user("ada", "ada@example.com", "x")
    with pytest.raises(IntegrityError):
        User.objects.create_user("ada2", "ada@example.com", "x")
