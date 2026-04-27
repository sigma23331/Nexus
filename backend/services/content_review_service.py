import re
from typing import Tuple

_BLOCKED_PATTERNS = [
    (r'傻[逼比]', '***'),
    (r'妈[的逼比]', '***'),
]


def is_content_safe(text: str) -> Tuple[bool, str]:
    """内置规则审核 + 标记需接入第三方 API 的位置。

    返回值 (passed, processed_text)：
      - passed:     是否完全无命中
      - processed:  敏感词被替换后的文本

    第三方审核 API 接入点（二选一或组合）：
      · 位置 A — 在本函数顶部，遇到疑似内容时调第三方接口二次确认
      · 位置 B — 在本函数 return 前，把所有 content 字段统一发给第三方

    以 OpenAI Moderation API 为例的位置 A 写法：
        import openai
        resp = openai.Moderation.create(input=text)
        if resp.results[0].flagged:
            # 打日志、替换或拒绝
            logger.warning(f"moderation flagged: {text[:50]}")
            return False, "内容不符合安全规范"

    以阿里云内容安全为例的位置 B 写法：
        from aliyunsdkcore.client import AcsClient
        client = AcsClient(access_key_id, access_key_secret, "cn-shanghai")
        # 调用 green 服务进行文本审核
        # 返回建议: pass / review / block
    """
    passed = True
    for pattern, replacement in _BLOCKED_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            passed = False
    return passed, text
