from django.db import migrations


def remove_welcome_page(apps, schema_editor):
    """Delete the "Welcome to your new Wagtail site!" page.

    Wagtail creates it, and a site pointing at it, in its own first data
    migration. This service has no public pages, so neither is wanted. The
    site row goes with the page.
    """
    ContentType = apps.get_model("contenttypes.ContentType")
    Page = apps.get_model("wagtailcore.Page")

    page_type = ContentType.objects.filter(
        app_label="wagtailcore", model="page"
    ).first()
    if page_type is None:
        return
    deleted, _ = Page.objects.filter(
        content_type=page_type, slug="home", depth=2
    ).delete()
    if deleted:
        # Keep the tree's child count right for the root page.
        Page.objects.filter(depth=1).update(numchild=0)


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("contenttypes", "0002_remove_content_type_name"),
        ("wagtailcore", "0098_apitoken"),
    ]

    operations = [
        migrations.RunPython(remove_welcome_page, migrations.RunPython.noop),
    ]
