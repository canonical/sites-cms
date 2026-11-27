"""Sample blog content for local review. Safe to run more than once."""

from datetime import timedelta

from django.utils import timezone

from blog.models import (
    Author,
    BlogPage,
    BlogPageGroup,
    BlogPageTag,
    Category,
    Group,
    Tag,
    get_blog_index,
)
from core.management.commands.create_local_admin import EMAIL as ADMIN_EMAIL

CATEGORIES = {
    "ubuntu-tech-blog": "Ubuntu tech blog",
    "canonical-blog": "Canonical blog",
    "articles": "Articles",
}
# slug: (name, parent slug)
GROUPS = {
    "ai": ("AI", None),
    "kubeflow": ("Kubeflow", "ai"),
    "security": ("Security", None),
    "networking": ("Networking", None),
}
TAGS = {
    "maas": "MAAS",
    "juju": "Juju",
    "kubeflow": "Kubeflow",
    "kubernetes": "Kubernetes",
    "openstack": "OpenStack",
    "snap": "Snap",
    "iot": "IoT",
    "desktop": "Desktop",
    "ubuntu-24-04": "Ubuntu 24.04",
    "confidential-computing": "Confidential computing",
}
# slug: (name, email, job title)
AUTHORS = {
    "local-admin": ("Local Admin", ADMIN_EMAIL, "Web team"),
    "jane-doe": ("Jane Doe", "jane.doe@example.com", "Product manager"),
    "canonical": ("Canonical", "", ""),
}

TABLE = {
    "data": [
        ["Release", "Supported until"],
        ["22.04 LTS", "April 2027"],
        ["24.04 LTS", "April 2029"],
    ],
    "first_row_is_table_header": True,
    "first_col_is_header": False,
    "table_caption": "",
}
BUTTON = (
    '<p><a class="p-button--positive" '
    'href="https://ubuntu.com/download">Download Ubuntu</a></p>'
)
EVERY_BLOCK_BODY = [
    (
        "rich_text",
        "<h2>Rich text</h2>"
        "<p>Text with <b>bold</b>, <i>italic</i>, "
        '<a href="https://ubuntu.com">a link</a>, <code>inline code</code>, '
        "x<sup>2</sup> and H<sub>2</sub>O.</p>"
        "<ul><li>An unordered list</li></ul>"
        "<ol><li>An ordered list</li></ol>"
        "<blockquote>A quote.</blockquote><hr/>",
    ),
    ("table", TABLE),
    ("html", BUTTON),
]


def text(paragraph):
    return [("rich_text", f"<p>{paragraph}</p>")]


def by_slug(model, slug, **defaults):
    return model.objects.get_or_create(slug=slug, defaults=defaults)[0]


def seed_blog(stdout):
    categories = {
        slug: by_slug(Category, slug, name=name)
        for slug, name in CATEGORIES.items()
    }
    groups = {}
    for slug, (name, parent) in GROUPS.items():
        groups[slug] = by_slug(
            Group, slug, name=name, parent=groups.get(parent)
        )
    tags = {slug: by_slug(Tag, slug, name=name) for slug, name in TAGS.items()}
    authors = {
        slug: by_slug(Author, slug, name=name, email=email, job_title=job)
        for slug, (name, email, job) in AUTHORS.items()
    }

    now = timezone.now()
    posts = [
        {
            "title": "Ubuntu 24.04 LTS is here",
            "excerpt": "Shown on two sites, and featured.",
            "body": text("Ubuntu 24.04 LTS is available to download."),
            "author": authors["local-admin"],
            "featured": True,
            "categories": ["ubuntu-tech-blog", "canonical-blog"],
            "groups": ["security"],
            "tags": ["ubuntu-24-04", "desktop"],
        },
        {
            "title": "Getting started with Kubeflow",
            "excerpt": "A live post in a nested group.",
            "body": text("Kubeflow runs machine learning on Kubernetes."),
            "author": authors["jane-doe"],
            "categories": ["ubuntu-tech-blog", "articles"],
            "groups": ["kubeflow", "ai"],
            "tags": ["kubeflow", "kubernetes"],
        },
        {
            "title": "MAAS roadmap",
            "excerpt": "A draft that was never published.",
            "body": text("Plans for the next MAAS release."),
            "author": authors["jane-doe"],
            "categories": ["ubuntu-tech-blog"],
            "groups": ["networking"],
            "tags": ["maas"],
            "live": False,
        },
        {
            "title": "Juju 4.0 is coming",
            "excerpt": "Scheduled to go live in a week.",
            "body": text("Juju 4.0 brings a new controller."),
            "author": authors["local-admin"],
            "categories": ["canonical-blog"],
            "tags": ["juju"],
            "go_live_at": now + timedelta(days=7),
        },
        {
            "title": "Every block type",
            "excerpt": "Uses rich text, a table and an HTML block.",
            "body": EVERY_BLOCK_BODY,
            "author": authors["canonical"],
            "categories": ["ubuntu-tech-blog"],
            "tags": ["snap", "iot"],
        },
        {
            "title": "Confidential computing on the public cloud",
            "excerpt": "A backdated post on canonical.com.",
            "body": text("Confidential computing protects data in use."),
            "author": authors["canonical"],
            "publish_date": now - timedelta(days=900),
            "categories": ["canonical-blog"],
            "groups": ["security"],
            "tags": ["confidential-computing", "openstack"],
        },
    ]

    blog_index = get_blog_index()
    created = 0
    for spec in posts:
        title = spec.pop("title")
        if BlogPage.objects.filter(title=title).exists():
            continue
        live = spec.pop("live", True)
        go_live_at = spec.pop("go_live_at", None)
        post = BlogPage(
            title=title,
            live=live and go_live_at is None,
            go_live_at=go_live_at,
            categories=[categories[s] for s in spec.pop("categories")],
            group_links=[
                BlogPageGroup(group=groups[s]) for s in spec.pop("groups", [])
            ],
            tag_links=[BlogPageTag(tag=tags[s]) for s in spec.pop("tags")],
            **spec,
        )
        blog_index.add_child(instance=post)
        revision = post.save_revision()
        if live:
            # A future go_live_at makes this a scheduled publish.
            revision.publish()
        created += 1

    stdout.write(
        f"Blog: {created} new posts, {BlogPage.objects.count()} in total."
    )
