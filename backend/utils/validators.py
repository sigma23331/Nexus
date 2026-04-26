def parse_page_limit(args, default_page=1, default_limit=10, max_limit=50):
    page_raw = args.get("page", default_page)
    limit_raw = args.get("limit", default_limit)

    try:
        page = int(page_raw)
        limit = int(limit_raw)
    except (TypeError, ValueError):
        raise ValueError("page 和 limit 必须为整数")

    if page < 1 or limit < 1 or limit > max_limit:
        raise ValueError(f"page 不能小于1，limit 范围 1-{max_limit}")

    return page, limit


def require_fields(data, fields):
    if not isinstance(data, dict):
        raise ValueError("请求体必须是有效的JSON")
    for field in fields:
        if field not in data or (isinstance(data[field], str) and not data[field].strip()):
            raise ValueError(f"{field} 字段不能为空")


def validate_enum(value, allowed, field_name):
    if value not in allowed:
        allowed_text = " | ".join(allowed)
        raise ValueError(f"{field_name} 必须为 {allowed_text}")
