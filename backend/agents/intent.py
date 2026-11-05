"""对话意图和购物需求的轻量解析。"""
import re


def classify_intent(message: str) -> str:
    text = message.strip().lower()
    if any(term in text for term in ("对比", "比较", "区别", "compare", "difference", " vs ")):
        return "compare"
    if any(term in text for term in ("推荐", "适合", "suggest", "recommend", "best")):
        return "recommend"
    if any(term in text for term in ("搜索", "找", "购买", "买", "search", "find", "looking for")):
        return "search"
    if any(term in text for term in ("怎么样", "如何", "质量", "参数", "支持", "多少钱", "what is", "how", "review")):
        return "qa"
    return "chat"


def parse_budget(message: str):
    patterns = (
        r"(?:预算|budget)\s*[:：]?\s*(?:不超过|不高于|under|up to)?\s*[¥￥$]?\s*(\d+(?:\.\d+)?)",
        r"(?:不超过|不高于|under|below|less than)\s*[¥￥$]?\s*(\d+(?:\.\d+)?)",
        r"[¥￥$]?\s*(\d+(?:\.\d+)?)\s*(?:元|块|人民币|yuan)?\s*(?:以内|以下|之内)",
    )
    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


def search_terms(message: str) -> list[str]:
    text = message.lower()
    text = re.sub(r"(?:预算|budget)\s*[:：]?\s*(?:不超过|不高于|under|up to)?\s*[¥￥$]?\s*\d+(?:\.\d+)?", " ", text)
    text = re.sub(r"[¥￥$]?\s*\d+(?:\.\d+)?\s*(?:元|块|人民币|yuan)?\s*(?:以内|以下|之内)", " ", text)
    text = re.sub(r"(?:不超过|不高于|under|below|less than)\s*[¥￥$]?\s*\d+(?:\.\d+)?", " ", text)
    for word in ("推荐", "帮我", "想找", "寻找", "适合", "一款", "一个", "请问", "怎么样", "对比", "比较", "差异", "区别", "有没有", "商品", "产品", "的", "我", "想", "买", "找", "和", "与"):
        text = text.replace(word, " ")
    terms = []
    for part in re.findall(r"[a-z]+|[\u4e00-\u9fff]+", text):
        if part in {"recommend", "suggest", "find", "looking", "for", "the", "under", "and", "compare", "best"}:
            continue
        if re.fullmatch(r"[\u4e00-\u9fff]+", part) and len(part) > 2:
            terms.extend(part[i:i + 2] for i in range(len(part) - 1))
        else:
            terms.append(part)
    return list(dict.fromkeys(term for term in terms if len(term) >= 2))[:20]
