import base64
import binascii
import hashlib
import re
from urllib.parse import urlparse


# 头像序列化辅助：历史原因头像以 base64 data URL 存储在 users.avatar 列，
# 单个可达 ~865KB。若在列表接口（广场/评论）中直接内联，一页 JSON 会膨胀到数 MB，
# 是广场加载缓慢的根因。此处统一改为返回短 URL，由 /user/avatar/<uid> 端点按需输出图片。

DEFAULT_AVATAR_URL = "https://api.xinyundao.com/default_avatar.png"
AVATAR_MAX_BYTES = int(1.4 * 1024 * 1024)
_ALLOWED_DATA_URL_MIMES = {"image/jpeg", "image/png", "image/webp"}
_DATA_URL_RE = re.compile(
    r"^data:(?P<mime>image/(?:jpeg|png|webp));base64,(?P<payload>[^,]+)$",
    re.IGNORECASE,
)
_UNSAFE_URL_CHARS_RE = re.compile(r"[\s<>'\"]")


def public_avatar_url(user):
    """返回可直接用于 <img src> 的头像地址。

    - base64 data URL -> 指向头像端点的短 URL（带 v 参数做缓存失效）
    - 普通 http(s) URL 或空值 -> 原样返回
    """
    avatar = getattr(user, "avatar", None) or ""
    if avatar.startswith("data:"):
        # /api/v1 前缀与前端请求约定一致（开发走 Vite 代理、生产走 nginx）
        return f"/api/v1/user/avatar/{user.id}?v={avatar_cache_version(avatar)}"
    return avatar


def avatar_or_default(user):
    return public_avatar_url(user) or DEFAULT_AVATAR_URL


def _looks_like_image(mime, payload):
    if mime == "image/jpeg":
        return payload.startswith(b"\xff\xd8\xff")
    if mime == "image/png":
        return payload.startswith(b"\x89PNG\r\n\x1a\n")
    if mime == "image/webp":
        return payload.startswith(b"RIFF") and payload[8:12] == b"WEBP"
    return False


def decode_avatar_data_url(avatar):
    """解析并校验头像 data URL，返回 (mime, bytes)。"""
    match = _DATA_URL_RE.match(avatar)
    if not match:
        raise ValueError("头像 dataURL 格式不正确")

    mime = match.group("mime").lower()
    if mime not in _ALLOWED_DATA_URL_MIMES:
        raise ValueError("头像仅支持 JPEG、PNG 或 WebP 图片")

    try:
        payload = base64.b64decode(match.group("payload"), validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("头像 base64 数据无效") from exc

    if len(payload) > AVATAR_MAX_BYTES:
        raise ValueError("头像不能超过 1.4MB，请压缩后重试")
    if not _looks_like_image(mime, payload):
        raise ValueError("头像图片内容无效")
    return mime, payload


def avatar_cache_version(avatar):
    if not avatar:
        return "0"
    return hashlib.sha256(avatar.encode("utf-8")).hexdigest()[:16]


def _validate_avatar_url(avatar):
    if len(avatar) > 2048:
        raise ValueError("头像 URL 长度不能超过2048个字符")
    if _UNSAFE_URL_CHARS_RE.search(avatar):
        raise ValueError("头像 URL 格式不正确")

    parsed = urlparse(avatar)
    if parsed.scheme:
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("头像 URL 格式不正确")
        return

    if avatar.startswith("//"):
        raise ValueError("头像 URL 格式不正确")
    if avatar.startswith("/") or not avatar.startswith("data:"):
        return

    raise ValueError("头像 URL 格式不正确")


def normalize_avatar_input(value):
    """统一头像入参：允许空值、图片 data URL、http(s) URL 或相对路径。"""
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError("头像格式无效")

    avatar = value.strip()
    if not avatar:
        return ""
    if avatar.startswith("data:"):
        decode_avatar_data_url(avatar)
    else:
        _validate_avatar_url(avatar)
    return avatar
