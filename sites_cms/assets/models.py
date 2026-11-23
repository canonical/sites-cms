"""The project's own image and document models.

They add nothing to Wagtail's yet. They exist so fields can be added later
with an ordinary migration, which is not possible once uploads have been
made against Wagtail's built-in models.
"""

from django.db import models
from wagtail.documents.models import AbstractDocument, Document
from wagtail.images.models import AbstractImage, AbstractRendition, Image


class CmsImage(AbstractImage):
    admin_form_fields = Image.admin_form_fields

    class Meta(AbstractImage.Meta):
        verbose_name = "image"
        verbose_name_plural = "images"
        permissions = [
            ("choose_image", "Can choose image"),
        ]


class CmsRendition(AbstractRendition):
    """A resized copy of an image, made by Wagtail when one is needed."""

    image = models.ForeignKey(
        CmsImage, related_name="renditions", on_delete=models.CASCADE
    )

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)


class CmsDocument(AbstractDocument):
    admin_form_fields = Document.admin_form_fields

    class Meta(AbstractDocument.Meta):
        permissions = [
            ("choose_document", "Can choose document"),
        ]
