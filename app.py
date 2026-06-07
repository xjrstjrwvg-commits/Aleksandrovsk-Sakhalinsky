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


def get_clean_char(w: str, pos="head", offset=0, unify_small=False, unify_daku=False, unify_handaku=False):
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
#  Reset（完全同期版）
# =========================
@app.route("/reset", methods=["POST"])
def reset():
    """
    index.html 側では localStorage を削除してリロードする。
    サーバー側では特に保持している状態はないので OK を返すだけ。
    """
    return jsonify({"status": "ok"})


# =========================
#  探索ルート（開始字バグ修正済み）
# =========================
@app.route("/search", methods=["POST"])
def search():
    data = request.json or {}

    timeout_enabled = data.get("timeout_enabled", True)
    timeout_sec = int(data.get("timeout", 15)) if timeout_enabled else None
    limit_enabled = data.get("limit_enabled", True)
    limit_count = int(data.get("limit", 1500))
    max_len = int(data.get("max_len", 5))

    pos_shift = int(data.get("pos_shift", 0))
    use_shift = data.get("use_shift", False)
    ks_abs = int(data.get("ks_abs", 1))
    shift_mode = data.get("shift_mode", "abs")

    unify_small = data.get("unify_small", False)
    allow_daku = data.get("allow_daku", False)
    allow_handaku = data.get("allow_handaku", False)

    len_mode = data.get("len_mode", "free")
    display_mode = data.get("display_mode", "normal")
    sort_mode = data.get("sort_mode", "default")
    early_cut = (display_mode == "early") and limit_enabled

    target_total_len = (
        int(data["target_total_len"]) if data.get("target_total_len") else None
    )

    raw_valid = to_katakana(data.get("valid_chars", ""))
    valid_chars = (
        {get_base_char(c, unify_small, allow_daku, allow_handaku)
         for c in raw_valid if c.strip()}
        if raw_valid else None
    )

    red_words = set(data.get("red_words", []))
    blue_words = set(data.get("blue_words", []))

    asc = [
        get_clean_char(c, "head", 0, unify_small, allow_daku, allow_handaku)
        for c in re.split("[,、]", to_katakana(data.get("all_start_char", "")))
        if c.strip()
    ]
    aec = [
        get_clean_char(c, "head", 0, unify_small, allow_daku, allow_handaku)
        for c in re.split("[,、]", to_katakana(data.get("all_end_char", "")))
        if c.strip()
    ]

    exc = [
        get_base_char(c, unify_small, allow_daku, allow_handaku)
        for c in re.split("[,、]", to_katakana(data.get("exclude_chars", "")))
        if c.strip()
    ]
    bsc = [
        get_base_char(c, unify_small, allow_daku, allow_handaku)
        for c in re.split("[,、]", to_katakana(data.get("ban_start_chars", "")))
        if c.strip()
    ]

    must_chars = parse_must_chars(
        data.get("must_char", ""),
        unify_small,
        allow_daku,
        allow_handaku,
    )

    start_word = to_katakana(data.get("start_word", ""))
    start_char = get_clean_char(
        to_katakana(data.get("start_char", "")),
        "head", 0,
        unify_small, allow_daku, allow_handaku
    )
    end_char = get_clean_char(
        to_katakana(data.get("end_char", "")),
        "head", 0,
        unify_small, allow_daku, allow_handaku
    )

    raw_words = []
    for cat in data.get("categories", ["country"]):
        raw_words += DICTIONARY_MASTER.get(cat, [])
    raw_words = list(set(raw_words))

    pool = []
    for w in raw_words:
        if w in red_words:
            continue

        if valid_chars:
            if any(
                get_base_char(c, unify_small, allow_daku, allow_handaku)
                not in valid_chars
                for c in w.replace("ー", "")
            ):
                continue

        h = get_clean_char(w, "head", 0, unify_small, allow_daku, allow_handaku)
        t = get_clean_char(w, "tail", 0, unify_small, allow_daku, allow_handaku)

        if asc and h not in asc:
            continue
        if aec and t not in aec:
            continue

        if any(
            e in "".join(get_base_char(c, unify_small, allow_daku, allow_handaku)
                         for c in w)
            for e in exc
        ):
            continue

        if h in bsc:
            continue

        pool.append(w)

    # ★ 修正：開始字フィルタ（濁点・小文字対応）
    if start_char and not start_word:
        sc_variants = get_variants(start_char, allow_daku, allow_handaku, unify_small)
        pool = [
            w for w in pool
            if get_clean_char(w, "head", 0, unify_small, allow_daku, allow_handaku)
               in sc_variants
        ]

    if end_char:
        ev = get_variants(end_char, allow_daku, allow_handaku, unify_small)
        pool = [
            w for w in pool
            if get_clean_char(w, "tail", 0, unify_small, allow_daku, allow_handaku)
            in ev
        ]

    if data.get("exclude_conjugate"):
        mp = defaultdict(list)
        for w in pool:
            h = get_clean_char(w, "head", 0, unify_small, allow_daku, allow_handaku)
            t = get_clean_char(w, "tail", 0, unify_small, allow_daku, allow_handaku)
            mp[f"{h}_{t}"].append(w)
        pool = [v[0] for v in mp.values()]

    head_map = defaultdict(list)
    tail_map = defaultdict(list)
    head_char = {}
    tail_char = {}
    clean_cache = {}
    char_sets = {}

    for w in pool:
        h = get_clean_char(w, "head", 0, unify_small, allow_daku, allow_handaku)
        t = get_clean_char(w, "tail", 0, unify_small, allow_daku, allow_handaku)
        head_char[w] = h
        tail_char[w] = t
        head_map[h].append(w)
        tail_map[t].append(w)

        c = w.replace("ー", "")
        clean_cache[w] = c
        char_sets[w] = {
            get_base_char(x, unify_small, allow_daku, allow_handaku)
            for x in c
        }

    results = []
    start_time = time.time()

    def timeout_check():
        return timeout_sec is not None and (time.time() - start_time) > timeout_sec

    def must_ok(s):
        for ch, mn, exact, exn in must_chars:
            cnt = s.count(ch)
            if exact:
                if cnt != exn:
                    return False
            else:
                if cnt < mn:
                    return False
        return True

    def solve(path, total_len, used_chars):
        if timeout_check():
            return
        if early_cut and len(results) >= limit_count:
            return
        if target_total_len and total_len > target_total_len:
            return

        if len_mode == "diff" and len(path) > 1:
            L = [len(x) for x in path]
            if len(L) != len(set(L)):
                return

        if len(path) == max_len:
            if len_mode == "same":
                L = [len(x) for x in path]
                if len(set(L)) > 1:
                    return

            norm = "".join(
                get_base_char(c, unify_small, allow_daku, allow_handaku)
                for c in "".join(path).replace("ー", "")
            )
            if not must_ok(norm):
                return

            if target_total_len and total_len != target_total_len:
                return

            if end_char:
                if tail_char[path[-1]] not in get_variants(end_char, allow_daku, allow_handaku, unify_small):
                    return

            results.append(path[:])
            return

        last = path[-1]
        cl = clean_cache[last]
        is_odd = len(path) % 2 != 0

        offsets = [pos_shift]
        if data.get("auto_recovery"):
            offsets += list(range(pos_shift + 1, len(cl)))

        for off in offsets:
            src = get_clean_char(
                last,
                "tail" if not data.get("round_trip") or is_odd else "head",
                off,
                unify_small, allow_daku, allow_handaku
            )
            if not src:
                continue

            raw_targets = set()
            if use_shift:
                if shift_mode == "abs":
                    raw_targets.add(shift_kana_fast(src, abs(ks_abs)))
                    raw_targets.add(shift_kana_fast(src, -abs(ks_abs)))
                else:
                    raw_targets.add(shift_kana_fast(src, ks_abs))
            else:
                raw_targets.add(src)

            targets = set()
            for r in raw_targets:
                targets |= get_variants(r, allow_daku, allow_handaku, unify_small)

            found = False
            for t in targets:
                cands = (
                    tail_map[t]
                    if data.get("round_trip") and is_odd
                    else head_map[t]
                )
                for nx in cands:
                    if nx in path:
                        continue
                    if data.get("char_limit_mode") and not char_sets[nx].isdisjoint(used_chars):
                        continue
                    solve(
                        path + [nx],
                        total_len + len(nx),
                        used_chars | char_sets[nx]
                    )
                    found = True
            if found:
                break

    starts = [start_word] if start_word and start_word in pool else pool

    for w in sorted(starts):
        if start_char and not start_word:
            if get_clean_char(w, "head", 0, unify_small, allow_daku, allow_handaku) not in get_variants(start_char, allow_daku, allow_handaku, unify_small):
                continue
        solve(
            [w],
            len(w),
            char_sets[w].copy() if data.get("char_limit_mode") else set()
        )
        if early_cut and len(results) >= limit_count:
            break
        if timeout_check():
            break

    if sort_mode == "kana":
        results.sort()
    elif sort_mode == "len_asc":
        results.sort(key=lambda x: len("".join(x)))
    elif sort_mode == "len_desc":
        results.sort(key=lambda x: len("".join(x)), reverse=True)
    elif sort_mode == "random":
        random.shuffle(results)

    if limit_enabled and len(results) > limit_count:
        results = results[:limit_count]

    return jsonify({"routes": results, "count": len(results)})


# =========================
#  メイン
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
