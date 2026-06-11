import base64
from types import SimpleNamespace

import pytest

from utils import avatar as avatar_utils


JPEG_DATA_URL = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2w=="
PNG_DATA_URL = "data:image/png;base64,iVBORw0KGgpwbmc="
WEBP_DATA_URL = "data:image/webp;base64,UklGRgAAAABXRUJQd2VicA=="


def test_normalize_avatar_input_accepts_supported_image_data_urls():
    assert avatar_utils.normalize_avatar_input(JPEG_DATA_URL) == JPEG_DATA_URL
    assert avatar_utils.normalize_avatar_input(PNG_DATA_URL) == PNG_DATA_URL
    assert avatar_utils.normalize_avatar_input(WEBP_DATA_URL) == WEBP_DATA_URL


def test_normalize_avatar_input_accepts_urls_and_empty_values():
    assert avatar_utils.normalize_avatar_input(None) == ""
    assert avatar_utils.normalize_avatar_input("  ") == ""
    assert avatar_utils.normalize_avatar_input("https://example.com/avatar.png") == "https://example.com/avatar.png"
    assert avatar_utils.normalize_avatar_input("/images/avatar.png") == "/images/avatar.png"
    assert avatar_utils.normalize_avatar_input("avatar.png") == "avatar.png"


@pytest.mark.parametrize(
    "value, message",
    [
        (123, "头像格式无效"),
        ("data:text/html;base64,PGgxPm5vdCBpbWFnZTwvaDE+", "头像 dataURL 格式不正确"),
        ("data:image/jpeg;base64,not-base64", "头像 base64 数据无效"),
        ("data:image/jpeg;base64,cGxhaW4tdGV4dA==", "头像图片内容无效"),
        ("https://example.com/bad avatar.png", "头像 URL 格式不正确"),
        ("ftp://example.com/avatar.png", "头像 URL 格式不正确"),
    ],
)
def test_normalize_avatar_input_rejects_invalid_values(value, message):
    with pytest.raises(ValueError, match=message):
        avatar_utils.normalize_avatar_input(value)


def test_normalize_avatar_input_rejects_oversized_data_url(monkeypatch):
    monkeypatch.setattr(avatar_utils, "AVATAR_MAX_BYTES", 4)
    payload = base64.b64encode(b"\xff\xd8\xffxx").decode("ascii")

    with pytest.raises(ValueError, match="头像不能超过 1.4MB"):
        avatar_utils.normalize_avatar_input(f"data:image/jpeg;base64,{payload}")


def test_public_avatar_url_uses_content_hash_version():
    first = SimpleNamespace(id="u1", avatar="data:image/jpeg;base64,/9j/aaaa")
    second = SimpleNamespace(id="u1", avatar="data:image/jpeg;base64,/9j/bbbb")

    first_url = avatar_utils.public_avatar_url(first)
    second_url = avatar_utils.public_avatar_url(second)

    assert first_url.startswith("/api/v1/user/avatar/u1?v=")
    assert second_url.startswith("/api/v1/user/avatar/u1?v=")
    assert first_url != second_url
