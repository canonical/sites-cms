import pytest

from blog.models import BlogPage, get_blog_index


@pytest.fixture
def blog_index(db):
    return get_blog_index()


@pytest.fixture
def make_post(blog_index):
    def make(title, live=True, **fields):
        post = BlogPage(title=title, live=live, **fields)
        blog_index.add_child(instance=post)
        revision = post.save_revision()
        if live:
            revision.publish()
        return post

    return make
