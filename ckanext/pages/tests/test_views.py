import base64
import io

import pytest

from ckan.plugins import toolkit
from ckan.tests import factories, helpers

# 1x1 transparent PNG
PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)


def _create_page(user, **kwargs):
    data = {"name": "page_name", "title": "Page Title", "content": "Content"}
    data.update(kwargs)
    if data.get("page_type") == "blog":
        data.setdefault("publish_date", "2024-01-01")
    helpers.call_action("ckanext_pages_update", {"user": user["name"]}, **data)


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestDelete:

    @pytest.mark.parametrize("page_type, endpoint, index_url", [
        ("page", "pages.delete", "/pages"),
        ("blog", "pages.blog_delete", "/blog"),
    ])
    def test_delete_redirects_to_index(self, app, page_type, endpoint, index_url):
        user = factories.Sysadmin()
        _create_page(user, page_type=page_type)

        response = app.post(
            toolkit.url_for(endpoint, page="page_name"),
            extra_environ={"REMOTE_USER": user["name"]},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location.endswith(index_url)
        assert helpers.call_action("ckanext_pages_show", {}, page="page_name") is None

    @pytest.mark.parametrize("page_type, endpoint, edit_url", [
        ("page", "pages.delete", "/pages_edit/page_name"),
        ("blog", "pages.blog_delete", "/blog_edit/page_name"),
    ])
    def test_cancel_redirects_to_edit(self, app, page_type, endpoint, edit_url):
        user = factories.Sysadmin()
        _create_page(user, page_type=page_type)

        response = app.post(
            toolkit.url_for(endpoint, page="page_name", cancel=1),
            extra_environ={"REMOTE_USER": user["name"]},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location.endswith(edit_url)
        assert helpers.call_action("ckanext_pages_show", {}, page="page_name")

    @pytest.mark.parametrize("group_type", ["organization", "group"])
    def test_group_delete_redirects_to_index(self, app, group_type):
        user = factories.Sysadmin()
        factory = factories.Organization if group_type == "organization" else factories.Group
        group = factory()
        _create_page(user, org_id=group["id"], page="page_name")

        response = app.post(
            toolkit.url_for(
                "pages.{}_pages_delete".format(group_type), id=group["name"], page="page_name"),
            extra_environ={"REMOTE_USER": user["name"]},
            follow_redirects=False,
        )

        assert response.status_code == 302
        assert response.location.endswith("/{}/pages/{}".format(group_type, group["name"]))


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestUpload:

    @pytest.fixture(autouse=True)
    def storage_path(self, ckan_config, monkeypatch, tmpdir):
        monkeypatch.setitem(ckan_config, "ckan.storage_path", str(tmpdir))

    def _upload(self, app, content, filename):
        user = factories.Sysadmin()
        return app.post(
            toolkit.url_for("pages.upload"),
            data={"upload": (io.BytesIO(content), filename)},
            extra_environ={"REMOTE_USER": user["name"]},
        )

    def test_upload_image(self, app):
        response = self._upload(app, PNG, "test.png")

        assert response.status_code == 200
        assert response.json["uploaded"] == 1
        assert "/uploads/page_images/" in response.json["url"]
        assert response.json["url"].endswith("test.png")

    def test_upload_non_image_is_rejected(self, app):
        response = self._upload(app, b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n", "test.pdf")

        assert response.status_code == 200
        assert response.json["uploaded"] == 0
        assert "Unsupported upload type" in response.json["error"]["message"]

    @pytest.mark.ckan_config("ckan.upload.page_images.types", "")
    @pytest.mark.ckan_config("ckan.upload.page_images.mimetypes", "")
    def test_upload_disabled_by_config(self, app):
        response = self._upload(app, PNG, "test.png")

        assert response.json["uploaded"] == 0
        assert "No uploads allowed" in response.json["error"]["message"]
