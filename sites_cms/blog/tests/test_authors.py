import pytest
from django.contrib.auth import get_user_model
from django.db.models import ProtectedError
from django.urls import reverse
from wagtail.models import Revision

from blog.models import Author

pytestmark = pytest.mark.django_db

User = get_user_model()


def make_user(username, email):
    return User.objects.create_user(username, email, "password")


def test_author_needs_no_account_or_email():
    author = Author.objects.create(name="Canonical")
    assert author.slug == "canonical"
    assert author.user is None


def test_author_fields_are_stored():
    author = Author.objects.create(
        name="Jane Doe",
        job_title="Engineer",
        bio="Writes about MAAS.",
        email="jane@example.com",
    )
    author.refresh_from_db()
    assert (author.job_title, author.bio) == ("Engineer", "Writes about MAAS.")


def test_author_snippet_views_load(admin_client):
    author = Author.objects.create(name="Jane Doe")
    for url in [
        reverse("wagtailsnippets_blog_author:list"),
        reverse("wagtailsnippets_blog_author:add"),
        reverse("wagtailsnippets_blog_author:edit", args=[author.pk]),
    ]:
        assert admin_client.get(url).status_code == 200


def test_saving_an_author_links_the_matching_user_ignoring_case():
    user = make_user("jane", "Jane.Doe@canonical.com")
    author = Author.objects.create(name="Jane", email="jane.doe@canonical.com")
    assert author.user == user


def test_creating_a_user_links_every_matching_author():
    first = Author.objects.create(name="Jane", email="jane@canonical.com")
    second = Author.objects.create(name="J. Doe", email="JANE@canonical.com")
    user = make_user("jane", "jane@canonical.com")
    first.refresh_from_db()
    second.refresh_from_db()
    assert first.user == user
    assert second.user == user


def test_signing_in_links_authors_after_an_email_change(client):
    user = make_user("jane", "old@canonical.com")
    author = Author.objects.create(name="Jane", email="jane@canonical.com")
    # A queryset update, so no save signal fires.
    User.objects.filter(pk=user.pk).update(email="jane@canonical.com")
    user.refresh_from_db()
    assert Author.objects.get(pk=author.pk).user is None
    client.force_login(user)
    assert Author.objects.get(pk=author.pk).user == user


def test_automatic_linking_never_replaces_a_link(client):
    user_a = make_user("a", "a@canonical.com")
    author = Author.objects.create(
        name="Jane", email="jane@canonical.com", user=user_a
    )
    user_b = make_user("b", "jane@canonical.com")
    client.force_login(user_b)
    author.save()
    author.refresh_from_db()
    assert author.user == user_a


def test_linking_gives_unowned_posts_to_the_user(make_post):
    author = Author.objects.create(name="Jane", email="jane@canonical.com")
    other = make_user("other", "other@canonical.com")
    unowned = [make_post(f"Post {n}", author=author) for n in range(2)]
    owned = make_post("Owned", author=author, owner=other)
    revisions = Revision.objects.count()

    user = make_user("jane", "jane@canonical.com")

    for post in unowned:
        post.refresh_from_db()
        assert post.owner == user
    owned.refresh_from_db()
    assert owned.owner == other
    assert Revision.objects.count() == revisions


def test_linking_by_hand_gives_unowned_posts_to_the_user(make_post):
    author = Author.objects.create(name="Jane", email="personal@gmail.com")
    post = make_post("Post", author=author)
    user = make_user("jane", "jane@canonical.com")
    author.user = user
    author.save()
    post.refresh_from_db()
    assert post.owner == user


def test_byline_comes_from_the_author_not_the_account(make_post):
    user = User.objects.create_user(
        "jane",
        "jane@canonical.com",
        "password",
        first_name="J.",
        last_name="Doe",
    )
    author = Author.objects.create(name="Jane Doe", user=user)
    post = make_post("Post", author=author)
    assert str(post.author) == "Jane Doe"


def test_an_author_with_posts_cannot_be_deleted(make_post):
    author = Author.objects.create(name="Jane")
    make_post("Post", author=author)
    with pytest.raises(ProtectedError):
        author.delete()
