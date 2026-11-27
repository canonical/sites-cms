from datetime import UTC, datetime

import pytest
from django.core.exceptions import ValidationError
from wagtail.images.tests.utils import get_test_image_file
from wagtail.models import Page

from assets.models import CmsImage
from blog.models import (
    RICH_TEXT_FEATURES,
    Author,
    BlogIndexPage,
    BlogPage,
    BlogPageGroup,
    BlogPageTag,
    Category,
    Group,
    Tag,
    get_blog_index,
)

pytestmark = pytest.mark.django_db

BUTTON = (
    '<a class="p-button--positive" '
    'href="https://ubuntu.com/download">Download</a>'
)


def test_blog_index_sits_under_the_root_and_holds_only_posts():
    assert BlogIndexPage.allowed_parent_page_models() == [Page]
    assert BlogIndexPage.allowed_subpage_models() == [BlogPage]
    assert BlogPage.allowed_parent_page_models() == [BlogIndexPage]
    assert BlogPage.allowed_subpage_models() == []


def test_get_blog_index_creates_one_index_only():
    first = get_blog_index()
    second = get_blog_index()
    assert first.pk == second.pk
    assert BlogIndexPage.objects.count() == 1
    assert not BlogIndexPage.can_create_at(Page.get_first_root_node())


def test_minimal_post_gets_a_slug_from_the_title(make_post):
    post = make_post("Hello world", live=False)
    assert post.slug == "hello-world"
    assert not post.live


def test_duplicate_post_slug_is_refused(blog_index, make_post):
    make_post("Kubeflow 1.9", slug="kubeflow-1-9")
    post = BlogPage(title="Other", slug="kubeflow-1-9")
    with pytest.raises(ValidationError) as error:
        blog_index.add_child(instance=post)
    assert "slug" in error.value.message_dict


def test_full_post_round_trips(make_post):
    image = CmsImage.objects.create(title="Hero", file=get_test_image_file())
    author = Author.objects.create(name="Jane Doe")
    ubuntu = Category.objects.create(name="Ubuntu tech blog")
    canonical = Category.objects.create(name="Canonical blog")
    group = Group.objects.create(name="AI")
    tag = Tag.objects.create(name="Kubeflow")
    date = datetime(2021, 3, 3, tzinfo=UTC)

    post = make_post(
        "Kubeflow 1.9",
        slug="kubeflow-1-9",
        seo_title="Kubeflow 1.9 is out",
        search_description="What is new in Kubeflow 1.9",
        excerpt="Short summary",
        body=[("html", BUTTON)],
        featured_image=image,
        author=author,
        publish_date=date,
        featured=True,
        categories=[ubuntu, canonical],
        group_links=[BlogPageGroup(group=group)],
        tag_links=[BlogPageTag(tag=tag)],
    )

    saved = BlogPage.objects.get(pk=post.pk)
    assert saved.live
    assert saved.slug == "kubeflow-1-9"
    assert saved.seo_title == "Kubeflow 1.9 is out"
    assert saved.search_description == "What is new in Kubeflow 1.9"
    assert saved.excerpt == "Short summary"
    assert saved.body[0].block_type == "html"
    assert saved.featured_image == image
    assert saved.author == author
    assert saved.publish_date == date
    assert saved.featured
    assert set(saved.categories.all()) == {ubuntu, canonical}
    assert [link.group for link in saved.group_links.all()] == [group]
    assert [link.tag for link in saved.tag_links.all()] == [tag]


def test_new_post_is_not_featured_and_dated_now(make_post):
    post = make_post("Post")
    assert not post.featured
    assert post.publish_date is not None


def test_group_and_tag_order_is_kept(make_post):
    security = Group.objects.create(name="Security")
    ai = Group.objects.create(name="AI")
    zebra = Tag.objects.create(name="Zebra")
    apple = Tag.objects.create(name="Apple")
    post = make_post(
        "Post",
        group_links=[BlogPageGroup(group=security), BlogPageGroup(group=ai)],
        tag_links=[BlogPageTag(tag=zebra), BlogPageTag(tag=apple)],
    )
    saved = BlogPage.objects.get(pk=post.pk)
    assert [link.group for link in saved.group_links.all()] == [security, ai]
    assert [link.tag for link in saved.tag_links.all()] == [zebra, apple]


def test_deleting_a_term_keeps_the_post(make_post):
    category = Category.objects.create(name="Ubuntu tech blog")
    group = Group.objects.create(name="AI")
    tag = Tag.objects.create(name="MAAS")
    post = make_post(
        "Post",
        categories=[category],
        group_links=[BlogPageGroup(group=group)],
        tag_links=[BlogPageTag(tag=tag)],
    )
    category.delete()
    group.delete()
    tag.delete()
    saved = BlogPage.objects.get(pk=post.pk)
    assert not saved.categories.exists()
    assert not saved.group_links.exists()
    assert not saved.tag_links.exists()


def test_deleting_the_featured_image_keeps_the_post(make_post):
    image = CmsImage.objects.create(title="Hero", file=get_test_image_file())
    post = make_post("Post", featured_image=image)
    image.delete()
    assert BlogPage.objects.get(pk=post.pk).featured_image is None


def test_body_offers_only_three_built_in_blocks():
    blocks = BlogPage.body.field.stream_block.child_blocks
    assert {name: block.label for name, block in blocks.items()} == {
        "rich_text": "Rich text",
        "table": "Table",
        "html": "HTML (advanced)",
    }
    assert blocks["rich_text"].features == RICH_TEXT_FEATURES


def test_html_block_keeps_markup_as_written(make_post):
    post = make_post("Post", body=[("html", BUTTON)])
    saved = BlogPage.objects.get(pk=post.pk)
    assert str(saved.body[0].value) == BUTTON
    assert saved.body[0].render() == BUTTON


def test_every_block_type_saves_and_previews(make_post):
    table = {
        "data": [["Release", "Date"], ["24.04", "April 2024"]],
        "first_row_is_table_header": True,
        "first_col_is_header": False,
        "table_caption": "",
    }
    post = make_post(
        "Post",
        body=[
            ("rich_text", "<h2>Heading</h2><p>Some <b>bold</b> text</p>"),
            ("table", table),
            ("html", BUTTON),
        ],
    )
    saved = BlogPage.objects.get(pk=post.pk)
    response = saved.make_preview_request()
    html = response.render().content.decode()
    assert response.status_code == 200
    assert "<h2>Heading</h2>" in html
    assert "April 2024" in html
    assert BUTTON in html


def test_search_finds_a_word_from_the_body(make_post):
    make_post(
        "Post",
        excerpt="Short",
        body=[("rich_text", "<p>Confidential computing</p>")],
    )
    make_post("Other")
    results = BlogPage.objects.search("confidential")
    assert [post.title for post in results] == ["Post"]
