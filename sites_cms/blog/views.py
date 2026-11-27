from django import forms
from django_filters import (
    ChoiceFilter,
    ModelChoiceFilter,
    ModelMultipleChoiceFilter,
)
from wagtail.admin.filters import WagtailFilterSet
from wagtail.admin.ui.tables import Column, DateColumn
from wagtail.admin.ui.tables.pages import (
    BulkActionsColumn,
    PageStatusColumn,
    PageTitleColumn,
)
from wagtail.admin.viewsets.pages import PageListingViewSet

from blog.models import Author, BlogPage, Category, Group


def posts_matching(queryset, **lookup):
    # A pk subquery keeps related filters working alongside search.
    return queryset.filter(
        pk__in=BlogPage.objects.filter(**lookup).values("pk")
    )


class BlogPostFilterSet(WagtailFilterSet):
    status = ChoiceFilter(
        label="Status",
        choices=[("live", "Live"), ("draft", "Draft")],
        method="filter_status",
        widget=forms.RadioSelect,
        empty_label="All",
    )
    category = ModelMultipleChoiceFilter(
        label="Category",
        queryset=Category.objects.all(),
        method="filter_category",
        widget=forms.CheckboxSelectMultiple,
    )
    group = ModelChoiceFilter(
        label="Group", queryset=Group.objects.all(), method="filter_group"
    )
    author = ModelChoiceFilter(
        label="Author", queryset=Author.objects.all(), method="filter_author"
    )

    class Meta:
        model = BlogPage
        fields = []

    def filter_status(self, queryset, name, value):
        return queryset.filter(live=value == "live")

    def filter_category(self, queryset, name, value):
        if not value:
            return queryset
        return posts_matching(queryset, categories__in=value)

    def filter_group(self, queryset, name, value):
        return posts_matching(queryset, group_links__group=value)

    def filter_author(self, queryset, name, value):
        return posts_matching(queryset, author=value)


class BlogPostListingViewSet(PageListingViewSet):
    model = BlogPage
    name = "blog_posts"
    icon = "doc-full"
    menu_label = "Blog posts"
    filterset_class = BlogPostFilterSet
    columns = [
        BulkActionsColumn("bulk_actions"),
        PageTitleColumn(
            "title", label="Title", sort_key="title", classname="title"
        ),
        PageStatusColumn("status", label="Status", sort_key="live"),
        Column("author", label="Author"),
        DateColumn(
            "latest_revision_created_at",
            label="Updated",
            sort_key="latest_revision_created_at",
        ),
    ]
