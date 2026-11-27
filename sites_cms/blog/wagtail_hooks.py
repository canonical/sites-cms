from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet, SnippetViewSetGroup

from blog.models import Author, Category, Group, Tag
from blog.views import BlogPostListingViewSet


class CategoryViewSet(SnippetViewSet):
    model = Category
    icon = "list-ul"
    list_display = ["name", "slug"]


class GroupViewSet(SnippetViewSet):
    model = Group
    icon = "folder-inverse"
    list_display = ["name", "slug", "parent"]


class TagViewSet(SnippetViewSet):
    model = Tag
    icon = "tag"
    list_display = ["name", "slug"]


class AuthorViewSet(SnippetViewSet):
    model = Author
    icon = "user"
    list_display = ["name", "job_title", "user"]


class BlogMenuGroup(SnippetViewSetGroup):
    menu_label = "Blog"
    menu_icon = "folder-open-inverse"
    items = (
        BlogPostListingViewSet,
        AuthorViewSet,
        CategoryViewSet,
        GroupViewSet,
        TagViewSet,
    )


register_snippet(BlogMenuGroup)
