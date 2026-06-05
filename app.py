# app.py — ULTRA ENGINE Pro 完全復元版

import os
import sys
import time
import random
import re
from collections import defaultdict
from flask import Flask, render_template, request, jsonify

# =========================
#  外部辞書
# =========================
try:
    from dictionary import DICTIONARY_MASTER
except ImportError:
    DICTIONARY_MASTER = {
        "country": ["ニホン"],
        "capital": ["トウキョウ"],
        "custom": []
    }

sys.setrecursionlimit(10000)
app = Flask(__name__)

# =========================
#  50音・変換マップ
# =========================
KANA_LIST = (
    "アイウエオ"
    "カキクケコ"
    "ガギグゲゴ"
    "サシスセソ"
    "ザジズゼゾ"
    "タチツテト"
    "ダヂヅデド"
    "ナニヌネノ"
    "ハヒフヘホ"
    "バビブベボ"
    "パピプペポ"
    "マミムメモ"
    "ヤユヨ"
    "ラリルレロ"
    "ワン"
)

SMALL_TO_LARGE = {
    "ァ": "ア", "ィ": "イ", "ゥ": "ウ", "ェ": "エ", "ォ": "オ",
    "ッ": "ツ", "ャ": "ヤ", "ュ": "ユ", "ョ": "ヨ", "ヮ": "ワ"
}

DAKU_MAP = {
    "カ": "ガ", "キ": "ギ", "ク": "グ", "ケ": "ゲ", "コ": "ゴ",
    "サ": "ザ", "シ": "ジ", "ス": "ズ", "セ": "ゼ", "ソ": "ゾ",
    "タ": "ダ", "チ": "ヂ", "ツ": "ヅ", "テ": "デ", "ト": "ド",
    "ハ": "バ", "ヒ": "ビ", "フ": "ブ", "ヘ": "ベ", "ホ": "ボ"
}

HANDAKU_MAP = {
    "ハ": "パ", "ヒ": "ピ", "フ": "プ", "ヘ": "ペ", "ホ": "ポ"
}

REV_DAKU = {v: k for k, v in DAKU_MAP.items()}
REV_HANDAKU = {v: k for k, v in HANDAKU_MAP.items()}
KANA_INDEX = {c: i for i, c in enumerate(KANA_LIST)}

# =========================
#  ユーティリティ
# =========================
def to_katakana(text: str) -> str:
    if not text:
        return ""
    res = []
    for c in text:
        code = ord(c)
        if 0x3041 <= code <= 0x3096:
            res.append(chr(code + 0x60))
        else:
            res.append(c)
    return "".join(res)


def get_base_char(c: str, unify_small=False, unify_daku=False, unify_handaku=False) -> str:
    if not c:
        return ""
    res = SMALL_TO_LARGE.get(c, c) if unify_small else c
    if res == "ェ":
        res = "エ"
    if unify_daku:
        res = REV_DAKU.get(res, res)
    if unify_handaku:
        res = REV_HANDAKU.get(res, res)
    return res


def get_clean_char(
    w: str,
    pos: str = "head",
    offset: int = 0,
    unify_small=False,
    unify_daku=False,
    unify_handaku=False,
) -> str:
    text = w.replace("ー", "")
    if not text:
        return ""
    try:
        idx = offset if pos == "head" else -(1 + offset)
        ch = text[idx]
        return get_base_char(ch, unify_small, unify_daku, unify_handaku)
    except IndexError:
        return ""


def shift_kana_fast(char: str, n: int) -> str:
    if char not in KANA_INDEX:
        return char
    return KANA_LIST[(KANA_INDEX[char] + n) % len(KANA_LIST)]


def get_variants(char: str, allow_daku: bool, allow_handaku: bool, unify_small=False):
    base = SMALL_TO_LARGE.get(char, char) if unify_small else char
    if base == "ェ":
        base = "エ"
    vs = {base}
    if allow_daku:
        for k, v in DAKU_MAP.items():
            if base == k:
                vs.add(v)
            if base == v:
                vs.add(k)
    if allow_handaku:
        for k, v in HANDAKU_MAP.items():
            if base == k:
                vs.add(v)
            if base == v:
                vs.add(k)
    return vs


def parse_must_chars(raw: str, unify_small=False, unify_daku=False, unify_handaku=False):
    """
    例:
      "あ,い,う"      → ア,イ,ウ を 1 回以上
      "あ:2,い"       → アは2回以上, イは1回以上
      "あ=2,い=1"     → アはちょうど2回, イはちょうど1回
    """
    if not raw:
        return []

    tokens = re.split("[、,]", to_katakana(raw))
    res = []
    for t in tokens:
        t = t.strip()
        if not t:
            continue
        exact = False
        min_cnt = 1
        exact_cnt = None

        if "=" in t:
            ch, num = t.split("=", 1)
            ch = ch.strip()
            try:
                exact_cnt = int(num.strip())
                exact = True
            except ValueError:
                exact_cnt = 1
        elif ":" in t:
            ch, num = t.split(":", 1)
            ch = ch.strip()
            try:
                min_cnt = int(num.strip())
            except ValueError:
                min_cnt = 1
        else:
            ch = t

        ch = get_base_char(ch, unify_small, unify_daku, unify_handaku)
        res.append((ch, min_cnt, exact, exact_cnt))
    return res


# =========================
#  Flask ルート
# =========================
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_dictionary")
def get_dictionary():
    return jsonify(DICTIONARY_MASTER)


# =========================
#  メイン探索
# =========================
@app.route("/search", methods=["POST"])
def search():
    d = request.json or {}

    # ---- 基本パラメータ ----
    timeout_val = int(d.get("timeout", 15))
    timeout_enabled = d.get("timeout_enabled", True)
    timeout = timeout_val if timeout_enabled else None

    limit = int(d.get("limit", 1500))
    limit_enabled = d.get("limit_enabled", True)

    max_len = int(d.get("max_len", 5))
    pos_shift = int(d.get("pos_shift", 0))

    use_shift = d.get("use_shift", False)
    ks_val = int(d.get("ks_abs", 1))
    shift_mode = d.get("shift_mode", "abs")

    unify_small = d.get("unify_small", False)
    allow_daku = d.get("allow_daku", False)
    allow_handaku = d.get("allow_handaku", False)
    unify_scope = d.get("unify_scope", "all")

    conn_small = unify_small and unify_scope in ["all", "conn"]
    conn_daku = allow_daku and unify_scope in ["all", "conn"]
    conn_handaku = allow_handaku and unify_scope in ["all", "conn"]

    filt_small = unify_small and unify_scope in ["all", "filter"]
    filt_daku = allow_daku and unify_scope in ["all", "filter"]
    filt_handaku = allow_handaku and unify_scope in ["all", "filter"]

    len_mode = d.get("len_mode", "free")  # free / same / diff
    display_mode = d.get("display_mode", "normal")  # normal / realtime / count / early
    sort_mode = d.get("sort_mode", "default")

    # 早期切り上げモード
    early_cut = (display_mode == "early") and limit_enabled

    # 文字数計
    target_total_len = int(d["target_total_len"]) if d.get("target_total_len") else None

    # 文字制限
    raw_valid = to_katakana(d.get("valid_chars", ""))
    valid_chars = None
    if raw_valid:
        valid_chars = set(
            get_base_char(c, filt_small, filt_daku, filt_handaku)
            for c in raw_valid.replace("、", "").replace(",", "")
            if c.strip()
        )

    # 赤・青ワード（辞書マネージャ）
    red_words = set(d.get("red_words", []))
    blue_words = set(d.get("blue_words", []))

    # 全語開始字・終了字
    all_start_chars = [
        get_clean_char(c.strip(), "head", 0, filt_small, filt_daku, filt_handaku)
        for c in re.split("[、,]", to_katakana(d.get("all_start_char", "")))
        if c.strip()
    ]
    all_end_chars = [
        get_clean_char(c.strip(), "head", 0, filt_small, filt_daku, filt_handaku)
        for c in re.split("[、,]", to_katakana(d.get("all_end_char", "")))
        if c.strip()
    ]

    # 使用不可文字・禁止開始文字
    exclude_chars = [
        get_base_char(c.strip(), filt_small, filt_daku, filt_handaku)
        for c in re.split("[、,]", to_katakana(d.get("exclude_chars", "")))
        if c.strip()
    ]
    ban_start_chars = [
        get_base_char(c.strip(), filt_small, filt_daku, filt_handaku)
        for c in re.split("[、,]", to_katakana(d.get("ban_start_chars", "")))
        if c.strip()
    ]

    # 必須文字（複数・回数指定）
    must_char_rules = parse_must_chars(
        d.get("must_char", ""),
        unify_small=filt_small,
        unify_daku=filt_daku,
        unify_handaku=filt_handaku,
    )

    # 開始単語・開始字・終了字（ひらがなOK）
    start_word = to_katakana(d.get("start_word", ""))
    start_char = get_clean_char(
        to_katakana(d.get("start_char", "")),
        "head",
        0,
        filt_small,
        filt_daku,
        filt_handaku,
    )
    end_char = get_clean_char(
        to_katakana(d.get("end_char", "")),
        "head",
        0,
        filt_small,
        filt_daku,
        filt_handaku,
    )

    # ---- 辞書プール構築 ----
    raw_pool = []
    for cat in d.get("categories", ["country"]):
        raw_pool.extend(DICTIONARY_MASTER.get(cat, []))
    raw_pool = list(set(raw_pool))

    temp_pool = []
    for w in raw_pool:
        if w in red_words:
            continue

        # valid_chars チェック
        if valid_chars is not None:
            ok = True
            for c in w.replace("ー", ""):
                bc = get_base_char(c, filt_small, filt_daku, filt_handaku)
                if bc not in valid_chars:
                    ok = False
                    break
            if not ok:
                continue

        h_char = get_clean_char(w, "head", 0, filt_small, filt_daku, filt_handaku)
        t_char = get_clean_char(w, "tail", 0, filt_small, filt_daku, filt_handaku)

        if all_start_chars and h_char not in all_start_chars:
            continue
        if all_end_chars and t_char not in all_end_chars:
            continue

        norm_w = "".join(get_base_char(c, filt_small, filt_daku, filt_handaku) for c in w)
        if any(ex in norm_w for ex in exclude_chars):
            continue
        if any(h_char == bs for bs in ban_start_chars):
            continue

        temp_pool.append(w)

    # 開始字指定がある場合、その開始字のものだけ
    if start_char and not start_word:
        temp_pool = [
            w
            for w in temp_pool
            if get_clean_char(w, "head", 0, filt_small, filt_daku, filt_handaku) == start_char
        ]

    # 終了字指定がある場合、その終了字（濁点・半濁点含む）のものだけ
    if end_char:
        end_variants_filter = get_variants(end_char, allow_daku, allow_handaku, unify_small=filt_small)
        temp_pool = [
            w
            for w in temp_pool
            if get_clean_char(w, "tail", 0, filt_small, filt_daku, filt_handaku) in end_variants_filter
        ]

    # 共役排除（同じ開始・終了ペアが複数ある場合は1つだけ残す）
    if d.get("exclude_conjugate"):
        pair_map = defaultdict(list)
        for w in temp_pool:
            ch = get_clean_char(w, "head", 0, conn_small, conn_daku, conn_handaku)
            ct = get_clean_char(w, "tail", 0, conn_small, conn_daku, conn_handaku)
            pair_map[f"{ch}_{ct}"].append(w)
        word_pool = [words[0] for words in pair_map.values()]
    else:
        word_pool = temp_pool

    # ---- キャッシュ構築 ----
    head_index = defaultdict(list)
    tail_index = defaultdict(list)
    head_cache = {}
    tail_cache = {}
    clean_cache = {}
    char_sets = {}

    for w in word_pool:
        h_conn = get_clean_char(w, "head", 0, conn_small, conn_daku, conn_handaku)
        t_conn = get_clean_char(w, "tail", 0, conn_small, conn_daku, conn_handaku)
        head_cache[w] = h_conn
        tail_cache[w] = t_conn
        head_index[h_conn].append(w)
        tail_index[t_conn].append(w)

        clean = w.replace("ー", "")
        clean_cache[w] = clean
        char_sets[w] = set(get_base_char(c, filt_small, filt_daku, filt_handaku) for c in clean)

    results = []
    start_time = time.time()

    # ---- DFS ----
    def check_timeout():
        if timeout is None:
            return False
        return (time.time() - start_time) > timeout

    def check_must_chars(norm_text: str) -> bool:
        if not must_char_rules:
            return True
        for ch, min_cnt, exact, exact_cnt in must_char_rules:
            cnt = norm_text.count(ch)
            if exact:
                if cnt != (exact_cnt or 0):
                    return False
            else:
                if cnt < min_cnt:
                    return False
        return True

    def solve(path, current_total_len, used_chars):
        # タイムアウト
        if check_timeout():
            return

        # 早期切り上げモード
        if early_cut and len(results) >= limit:
            return

        # 文字数計オーバー
        if target_total_len is not None and current_total_len > target_total_len:
            return

        # 文字数構成制約
        if len_mode == "diff" and len(path) > 1:
            lens = [len(x) for x in path]
            if len(lens) != len(set(lens)):
                return

        # 完成判定
        if len(path) == max_len:
            if len_mode == "same":
                lens = [len(x) for x in path]
                if len(set(lens)) > 1:
                    return

            # 必須文字チェック
            norm_t = "".join(
                get_base_char(c, filt_small, filt_daku, filt_handaku)
                for c in "".join(path).replace("ー", "")
            )
            if not check_must_chars(norm_t):
                return

            # 文字数計
            if target_total_len is not None and current_total_len != target_total_len:
                return

            # 終了字指定
            if end_char:
                last_tail = tail_cache[path[-1]]
                end_variants = get_variants(end_char, allow_daku, allow_handaku, unify_small=conn_small)
                if last_tail not in end_variants:
                    return

            results.append(list(path))
            return

        # 次の接続
        is_odd = (len(path) % 2 != 0)
        last_word = path[-1]
        last_clean = clean_cache[last_word]

        base_offsets = [pos_shift]
        if d.get("auto_recovery"):
            base_offsets += list(range(pos_shift + 1, len(last_clean)))

        for off in base_offsets:
            src = get_clean_char(
                last_word,
                ("tail" if not d.get("round_trip") or is_odd else "head"),
                off,
                conn_small,
                conn_daku,
                conn_handaku,
            )
            if not src:
                continue

            raw_targets = set()
            if use_shift:
                if shift_mode == "abs":
                    raw_targets.add(shift_kana_fast(src, abs(ks_val)))
                    raw_targets.add(shift_kana_fast(src, -abs(ks_val)))
                else:
                    raw_targets.add(shift_kana_fast(src, ks_val))
            else:
                raw_targets.add(src)

            targets = set()
            for rt in raw_targets:
                targets.update(get_variants(rt, allow_daku, allow_handaku, unify_small=conn_small))

            found_any = False
            for tc in targets:
                if d.get("round_trip") and is_odd:
                    cands = tail_index[tc]
                else:
                    cands = head_index[tc]

                for nxt in cands:
                    if nxt in path:
                        continue

                    if d.get("char_limit_mode"):
                        if not char_sets[nxt].isdisjoint(used_chars):
                            continue

                    new_used = used_chars | char_sets[nxt]
                    solve(path + [nxt], current_total_len + len(nxt), new_used)
                    found_any = True

            if found_any:
                break

    # ---- 探索開始 ----
    if start_word and start_word in word_pool:
        starts = [start_word]
    else:
        starts = word_pool

    for w in sorted(starts):
        if start_char and not start_word:
            if get_clean_char(w, "head", 0, filt_small, filt_daku, filt_handaku) != start_char:
                continue
        initial_used = char_sets[w].copy() if d.get("char_limit_mode") else set()
        solve([w], len(w), initial_used)

        if early_cut and len(results) >= limit:
            break

        if timeout is not None and (time.time() - start_time) > timeout:
            break

    # ---- ソート ----
    if sort_mode == "kana":
        results.sort()
    elif sort_mode == "len_asc":
        results.sort(key=lambda x: len("".join(x)))
    elif sort_mode == "len_desc":
        results.sort(key=lambda x: len("".join(x)), reverse=True)
    elif sort_mode == "random":
        random.shuffle(results)

    # limit は「返す件数」の上限としても使う
    if limit_enabled and len(results) > limit:
        results = results[:limit]

    return jsonify({"routes": results, "count": len(results)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
