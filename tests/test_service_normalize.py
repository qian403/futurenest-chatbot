import re

# 直接從 service 匯入要測的函式與正則（不需啟動 Django）
from backend.apps.rag.service import normalize_chinese_numbers, CHINESE_ARTICLE_PATTERN, parse_chinese_num


def test_parse_chinese_num_basic():
    assert parse_chinese_num('一') == 1
    assert parse_chinese_num('九') == 9
    assert parse_chinese_num('十') == 10
    assert parse_chinese_num('十一') == 11
    assert parse_chinese_num('二十') == 20
    assert parse_chinese_num('二十三') == 23
    assert parse_chinese_num('零') == 0  # 未支援，回 0


def test_normalize_chinese_numbers_keeps_digits():
    s = '請解釋第12條與第  20 條'
    out = normalize_chinese_numbers(s)
    assert '第12條' in out
    assert '第20條' in out


def test_normalize_chinese_numbers_chinese_to_arabic():
    s = '請說明第十一條 及 第 二 十 三 條'
    out = normalize_chinese_numbers(s)
    # 確認中文轉阿拉伯數字
    assert '第11條' in out
    assert '第23條' in out


def test_article_regex():
    s = '第7條與第  25 條'
    m = CHINESE_ARTICLE_PATTERN.findall(s)
    assert m == ['7', '25']


