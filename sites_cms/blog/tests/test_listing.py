import pytest
from django.urls import reverse
from wagtail.admin.menu import admin_menu

from blog.models import (
    Author,
    BlogPageGroup,
    Category,
    Group,
)

pytestmark = pytest.mark.django_db

URL = reverse("blog_posts:index")


def listed(client, **params):
    response = client.get(URL, params)
    assert response.status_code == 200
    return {page.title for page in response.context["object_list"]}


@pytest.fixture
def posts(make_post):
    jane = Author.objects.create(name="Jane")
    ubuntu = Category.objects.create(name="Ubuntu tech blog")
    ai = Group.objects.create(name="AI")
    make_post(
        "Kubeflow release",
        author=jane,
        categories=[ubuntu],
        group_links=[BlogPageGroup(group=ai)],
    )
    make_post("MAAS draft", live=False)
    return {"jane": jane, "ubuntu": ubuntu, "ai": ai}


def test_listing_shows_every_post_with_its_columns(admin_client, posts):
    response = admin_client.get(URL)
    html = response.content.decode()
    assert listed(admin_client) == {"Kubeflow release", "MAAS draft"}
    for heading in ["Title", "Status", "Author", "Updated"]:
        assert heading in html
    assert "Jane" in html


def test_filter_by_live_status(admin_client, posts):
    assert listed(admin_client, status="draft") == {"MAAS draft"}
    assert listed(admin_client, status="live") == {"Kubeflow release"}


def test_filter_by_category(admin_client, posts):
    category = posts["ubuntu"].pk
    assert listed(admin_client, category=category) == {"Kubeflow release"}


def test_filter_by_group(admin_client, posts):
    assert listed(admin_client, group=posts["ai"].pk) == {"Kubeflow release"}


def test_filter_by_author(admin_client, posts):
    assert listed(admin_client, author=posts["jane"].pk) == {
        "Kubeflow release"
    }


def test_search_by_title(admin_client, posts):
    assert listed(admin_client, q="kubeflow") == {"Kubeflow release"}


def test_search_and_filter_together(admin_client, posts):
    assert listed(admin_client, q="maas", status="live") == set()
    assert listed(admin_client, q="kubeflow", group=posts["ai"].pk) == {
        "Kubeflow release"
    }


def test_blog_posts_is_first_in_the_blog_menu(admin_client):
    request = admin_client.get("/admin/").wsgi_request
    menu = {
        item.label: item for item in admin_menu.menu_items_for_request(request)
    }
    assert "Blog posts" not in menu
    blog_items = menu["Blog"].menu.menu_items_for_request(request)
    assert [item.label for item in blog_items] == [
        "Blog posts",
        "Authors",
        "Categories",
        "Groups",
        "Tags",
    ]
