from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.admin.panels import (
    FieldPanel,
    MultiFieldPanel,
    MultipleChooserPanel,
)
from wagtail.blocks import RawHTMLBlock, RichTextBlock
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.fields import StreamField
from wagtail.models import Orderable, Page
from wagtail.search import index

RICH_TEXT_FEATURES = [
    "h2",
    "h3",
    "h4",
    "bold",
    "italic",
    "link",
    "ol",
    "ul",
    "blockquote",
    "hr",
    "code",
    "superscript",
    "subscript",
    "image",
    "embed",
]

BODY_BLOCKS = [
    (
        "rich_text",
        RichTextBlock(features=RICH_TEXT_FEATURES, label="Rich text"),
    ),
    ("table", TableBlock(label="Table")),
    (
        "html",
        RawHTMLBlock(
            label="HTML (advanced)",
            help_text="Stored exactly as written. Use only for content "
            "rich text cannot hold.",
        ),
    ),
]


class NamedWithSlug(index.Indexed, models.Model):
    """A name plus a unique slug that is made from the name when blank.

    The slug is never remade on rename: websites filter on it.
    """

    name = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=255,
        unique=True,
        allow_unicode=True,
        blank=True,
        error_messages={"unique": "This slug is already in use."},
        help_text="Used in web addresses. Made from the name if left "
        "blank. Renaming does not change it.",
    )

    search_fields = [
        index.SearchField("name"),
        index.AutocompleteField("name"),
        index.AutocompleteField("slug"),
    ]

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.fill_slug()
        super().save(*args, **kwargs)

    def fill_slug(self):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)

    def clean(self):
        super().clean()
        # Filled here too, so the form's unique check sees the real slug.
        self.fill_slug()
        if not self.slug:
            raise ValidationError(
                {"slug": "A slug could not be made from the name. Enter one."}
            )


class BlogTerm(NamedWithSlug):
    description = models.TextField(blank=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("description"),
    ]

    class Meta(NamedWithSlug.Meta):
        abstract = True


class Category(BlogTerm):
    class Meta(BlogTerm.Meta):
        verbose_name_plural = "categories"


class Group(BlogTerm):
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )

    panels = BlogTerm.panels + [FieldPanel("parent")]

    def clean(self):
        super().clean()
        seen = set()
        ancestor = self.parent
        while ancestor is not None and ancestor.pk not in seen:
            if ancestor is self or (self.pk and ancestor.pk == self.pk):
                raise ValidationError(
                    {
                        "parent": "A group cannot be inside itself. "
                        "This parent would create a loop."
                    }
                )
            seen.add(ancestor.pk)
            ancestor = ancestor.parent


class Tag(BlogTerm):
    pass


class Author(NamedWithSlug):
    """A byline. Separate from user accounts, linked to one by email."""

    job_title = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    photo = models.ForeignKey(
        settings.WAGTAILIMAGES_IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    # Not unique: one person may have had several WordPress accounts.
    email = models.EmailField(blank=True, db_index=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="authors",
        verbose_name="linked account",
        help_text="Filled automatically when the emails match.",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("job_title"),
        FieldPanel("bio"),
        FieldPanel("photo"),
        FieldPanel("email"),
        FieldPanel("user"),
    ]

    def save(self, *args, **kwargs):
        if self.user_id is None and self.email:
            self.user = (
                get_user_model()
                .objects.filter(email__iexact=self.email)
                .order_by("pk")
                .first()
            )
        super().save(*args, **kwargs)
        if self.user_id is not None:
            # A queryset update, so no page revision is created.
            BlogPage.objects.filter(author=self, owner__isnull=True).update(
                owner=self.user
            )


def link_authors(user):
    """Link unlinked authors with the user's email to the user."""
    if not user.email:
        return
    unlinked = Author.objects.filter(
        user__isnull=True, email__iexact=user.email
    )
    for author in unlinked:
        author.user = user
        author.save(update_fields=["user"])


class BlogIndexPage(Page):
    max_count = 1
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["blog.BlogPage"]
    # Nothing to show: the index only holds the posts.
    preview_modes = []

    class Meta:
        verbose_name = "blog index"


def get_blog_index():
    """Return the blog index, creating it under the root if missing."""
    blog_index = BlogIndexPage.objects.first()
    if blog_index is None:
        blog_index = BlogIndexPage(title="Blog", slug="blog")
        Page.get_first_root_node().add_child(instance=blog_index)
    return blog_index


class BlogPage(Page):
    excerpt = models.TextField(blank=True)
    body = StreamField(BODY_BLOCKS, blank=True)
    featured_image = models.ForeignKey(
        settings.WAGTAILIMAGES_IMAGE_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    author = models.ForeignKey(
        Author,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="posts",
    )
    publish_date = models.DateTimeField(
        default=timezone.now,
        help_text="The date shown on the post. Can be in the past.",
    )
    featured = models.BooleanField(
        default=False,
        help_text="Show in the featured panels on the websites.",
    )
    categories = ParentalManyToManyField(
        Category, blank=True, related_name="posts"
    )

    parent_page_types = ["blog.BlogIndexPage"]
    subpage_types = []

    content_panels = Page.content_panels + [
        FieldPanel("excerpt"),
        FieldPanel("featured_image"),
        FieldPanel("body"),
        MultiFieldPanel(
            [
                FieldPanel("author"),
                FieldPanel("publish_date"),
                FieldPanel("featured"),
            ],
            heading="Byline",
        ),
        FieldPanel("categories", widget=forms.CheckboxSelectMultiple),
        MultipleChooserPanel(
            "group_links", label="Groups", chooser_field_name="group"
        ),
        MultipleChooserPanel(
            "tag_links", label="Tags", chooser_field_name="tag"
        ),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("excerpt"),
        index.SearchField("body"),
    ]

    class Meta:
        verbose_name = "blog post"


class BlogPageGroup(Orderable):
    page = ParentalKey(
        BlogPage, on_delete=models.CASCADE, related_name="group_links"
    )
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="post_links"
    )

    panels = [FieldPanel("group")]


class BlogPageTag(Orderable):
    page = ParentalKey(
        BlogPage, on_delete=models.CASCADE, related_name="tag_links"
    )
    tag = models.ForeignKey(
        Tag, on_delete=models.CASCADE, related_name="post_links"
    )

    panels = [FieldPanel("tag")]
