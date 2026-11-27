from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

from blog.models import link_authors


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def link_authors_to_new_user(sender, instance, created, raw=False, **kwargs):
    if created and not raw:
        link_authors(instance)


@receiver(user_logged_in)
def link_authors_on_sign_in(sender, user, **kwargs):
    # Catches emails changed after the account was created.
    link_authors(user)
