# 头像序列化辅助：历史原因头像以 base64 data URL 存储在 users.avatar 列，
# 单个可达 ~865KB。若在列表接口（广场/评论）中直接内联，一页 JSON 会膨胀到数 MB，
# 是广场加载缓慢的根因。此处统一改为返回短 URL，由 /user/avatar/<uid> 端点按需输出图片。


def public_avatar_url(user):
    """返回可直接用于 <img src> 的头像地址。

    - base64 data URL -> 指向头像端点的短 URL（带 v 参数做缓存失效）
    - 普通 http(s) URL 或空值 -> 原样返回
    """
    avatar = getattr(user, "avatar", None) or ""
    if avatar.startswith("data:"):
        # /api/v1 前缀与前端请求约定一致（开发走 Vite 代理、生产走 nginx）
        return f"/api/v1/user/avatar/{user.id}?v={len(avatar)}"
    return avatar
