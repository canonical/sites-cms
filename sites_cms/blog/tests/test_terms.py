import pytest
from django.core.exceptions import ValidationError
from django.urls import reverse

from blog.models import Category, Group, Tag

pytestmark = pytest.mark.django_db


def test_slug_is_made_from_the_name():
    assert Tag.objects.create(name="Data platform").slug == "data-platform"


def test_an_entered_slug_is_kept():
    assert Tag.objects.create(name="Data platform", slug="dp").slug == "dp"


def test_renaming_keeps_the_slug():
    tag = Tag.objects.create(name="MAAS")
    tag.name = "Metal as a Service"
    tag.save()
    tag.refresh_from_db()
    assert tag.slug == "maas"


def test_duplicate_slug_is_refused_with_a_message():
    Tag.objects.create(name="MAAS", slug="maas")
    with pytest.raises(ValidationError) as error:
        Tag(name="Other", slug="maas").full_clean()
    assert error.value.message_dict["slug"] == ["This slug is already in use."]


def test_duplicate_slug_made_from_the_name_is_refused():
    Tag.objects.create(name="MAAS")
    with pytest.raises(ValidationError) as error:
        Tag(name="maas").full_clean()
    assert "slug" in error.value.message_dict


def test_same_slug_is_allowed_in_different_kinds():
    Category.objects.create(name="Community", slug="community")
    Group.objects.create(name="Community", slug="community")
    Tag(name="Community", slug="community").full_clean()


def test_names_need_not_be_unique():
    Group.objects.create(name="Networking", slug="networking")
    Group(name="Networking", slug="networking-2").full_clean()


def test_non_ascii_slugs_are_accepted():
    tag = Tag(name="中文 博客")
    tag.full_clean()
    tag.save()
    assert tag.slug == "中文-博客"


def test_a_name_with_no_slug_characters_needs_a_slug():
    with pytest.raises(ValidationError) as error:
        Tag(name="!!!").full_clean()
    assert "slug" in error.value.message_dict


def test_group_can_have_a_parent():
    ai = Group.objects.create(name="AI")
    kubeflow = Group(name="Kubeflow", parent=ai)
    kubeflow.full_clean()
    kubeflow.save()
    assert list(ai.children.all()) == [kubeflow]


def test_group_cannot_be_its_own_parent():
    group = Group.objects.create(name="AI")
    group.parent = group
    with pytest.raises(ValidationError) as error:
        group.full_clean()
    assert "loop" in error.value.message_dict["parent"][0]


def test_group_parent_loop_is_refused():
    ai = Group.objects.create(name="AI")
    kubeflow = Group.objects.create(name="Kubeflow", parent=ai)
    ai.parent = kubeflow
    with pytest.raises(ValidationError) as error:
        ai.full_clean()
    assert "loop" in error.value.message_dict["parent"][0]


@pytest.mark.parametrize("model", ["category", "group", "tag"])
def test_snippet_admin_views_load(admin_client, model):
    index_url = reverse(f"wagtailsnippets_blog_{model}:list")
    add_url = reverse(f"wagtailsnippets_blog_{model}:add")
    assert admin_client.get(index_url).status_code == 200
    assert admin_client.get(add_url).status_code == 200


def test_snippet_listing_searches_name_and_slug(admin_client):
    Tag.objects.create(name="Metal as a Service", slug="maas")
    Tag.objects.create(name="Juju")
    url = reverse("wagtailsnippets_blog_tag:list")
    by_name = admin_client.get(url, {"q": "metal"}).context["object_list"]
    by_slug = admin_client.get(url, {"q": "maas"}).context["object_list"]
    assert [tag.slug for tag in by_name] == ["maas"]
    assert [tag.slug for tag in by_slug] == ["maas"]


def test_add_form_refuses_a_duplicate_slug(admin_client):
    Tag.objects.create(name="MAAS")
    url = reverse("wagtailsnippets_blog_tag:add")
    response = admin_client.post(url, {"name": "MAAS", "slug": ""})
    assert response.status_code == 200
    assert "This slug is already in use." in response.content.decode()
    assert Tag.objects.count() == 1


def test_tag_chooser_searches_many_tags(admin_client):
    Tag.objects.bulk_create(
        Tag(name=f"Tag {n}", slug=f"tag-{n}") for n in range(60)
    )
    Tag.objects.create(name="Kubeflow")
    url = reverse("wagtailsnippetchoosers_blog_tag:choose_results")
    response = admin_client.get(url, {"q": "kubef"})
    assert [tag.name for tag in response.context["results"]] == ["Kubeflow"]
