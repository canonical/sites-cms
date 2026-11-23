from wagtail.documents import get_document_model
from wagtail.images import get_image_model

from assets.models import CmsDocument, CmsImage, CmsRendition


def test_wagtail_uses_the_project_image_model():
    assert get_image_model() is CmsImage
    assert CmsImage.get_rendition_model() is CmsRendition


def test_wagtail_uses_the_project_document_model():
    assert get_document_model() is CmsDocument


def test_image_upload_page_loads(admin_client):
    response = admin_client.get("/admin/images/add/")
    assert response.status_code == 200


def test_document_upload_page_loads(admin_client):
    response = admin_client.get("/admin/documents/add/")
    assert response.status_code == 200
