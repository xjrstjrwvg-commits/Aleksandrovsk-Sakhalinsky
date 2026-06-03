import os
import time
import sys
import re
import random
from collections import defaultdict, Counter
from flask import Flask, render_template, request, jsonify

# 外部化した辞書データをインポート
try:
    from dictionary import DICTIONARY_MASTER
except ImportError:
    # 辞書ファイルがない場合のエラー回避（デバッグ用）
    DICTIONARY_MASTER = {"country": ["ニホン"], "capital": ["トウキョウ"]}

sys.setrecursionlimit(10000)
app = Flask(__name__)

# --- 定数・マッピング ---
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

# 50音インデックス（高速化用）
KANA_INDEX = {c: i for i, c in enumerate(KANA_LIST)}


# --- ユーティリティ ---
def to_katakana(text: str) -> str:
    if not text:
        return ""
    return "".join(
        [chr(ord(c) + 96) if 0x3041 <= ord(c) <= 0x3096 else c for c in text]
    )


def get_base_char(c, unify_small=False, unify_daku=False, unify_handaku=False):
    res = SMALL_TO_LARGE.get(c, c) if unify_small else c
    if unify_daku:
        res = REV_DAKU.get(res, res)
    if unify_handaku:
        res = REV_HANDAKU.get(res, res)
    return res


def get_clean_char(w, pos="head", offset=0, unify_s=False, unify_d=False, unify_h=False):
    text = w.replace("ー", "")
    if not text:
        return ""
    try:
        idx = offset if pos == "head" else -(1 + offset)
        char = text[idx]
        return get_base_char(char, unify_s, unify_d, unify_h)
    except IndexError:
        return ""


def shift_kana_fast(char, n):
    if char not in KANA_INDEX:
        return char
    return KANA_LIST[(KANA_INDEX[char] + n) % len(KANA_LIST)]


def get_variants(char, allow_daku, allow_handaku, unify=False):
    base = SMALL_TO_LARGE.get(char, char) if unify else char
    variants = {base}
    if allow_daku:
        for k, v in DAKU_MAP.items():
            if base == k:
                variants.add(v)
            if base == v:
                variants.add(k)
    if allow_handaku:
        for k, v in HANDAKU_MAP.items():
            if base == k:
                variants.add(v)
            if base == v:
                variants.add(k)
    return variants


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/get_dictionary")
def get_dictionary():
    return jsonify(DICTIONARY_MASTER)


@app.route("/search", methods=["POST"])
def search():
    d = request.json or {}

    # --- パラメータ取得 ---
    timeout = int(d.get("timeout", 15))
    limit = int(d.get("limit", 1500))
    limit_en = d.get("limit_enabled", True)

    max_len = int(d.get("max_len", 5))
    p_shift = int(d.get("pos_shift", 0))

    use_shift = d.get("use_shift", False)
    ks_val = int(d.get("ks_abs", 1))
    s_mode = d.get("shift_mode", "abs")

    u_small = d.get("unify_small", False)
    u_daku = d.get("allow_daku", False)
    u_handaku = d.get("allow_handaku", False)
    scope = d.get("unify_scope", "all")

    conn_s = (u_small and scope in ["all", "conn"])
    conn_d = (u_daku and scope in ["all", "conn"])
    conn_h = (u_handaku and scope in ["all", "conn"])

    filt_s = (u_small and scope in ["all", "filter"])
    filt_d = (u_daku and scope in ["all", "filter"])
    filt_h = (u_handaku and scope in ["all", "filter"])

    len_mode = d.get("len_mode", "free")

    raw_valid = to_katakana(d.get("valid_chars", ""))
    valid_chars = (
        set(raw_valid.replace("、", "").replace(",", "")) if raw_valid else None
    )

    red_words = set(d.get("red_words", []))
    blue_words = set(d.get("blue_words", []))

    asc = [
        get_clean_char(c.strip(), "head", 0, filt_s, filt_d, filt_h)
        for c in re.split("[、,]", to_katakana(d.get("all_start_char", "")))
        if c.strip()
    ]
    aec = [
        get_clean_char(c.strip(), "head", 0, filt_s, filt_d, filt_h)
        for c in re.split("[、,]", to_katakana(d.get("all_end_char", "")))
        if c.strip()
    ]
    ex_list = [
        get_base_char(c.strip(), filt_s, filt_d, filt_h)
        for c in re.split("[、,]", to_katakana(d.get("exclude_chars", "")))
        if c.strip()
    ]
    bs_list = [
        get_base_char(c.strip(), filt_s, filt_d, filt_h)
        for c in re.split("[、,]", to_katakana(d.get("ban_start_chars", "")))
        if c.strip()
    ]
    must_chars = [
        get_base_char(c, filt_s, filt_d, filt_h)
        for c in re.split("[、,]", to_katakana(d.get("must_char", "")))
        if c
    ]

    start_word = to_katakana(d.get("start_word", ""))
    start_char = get_clean_char(
        to_katakana(d.get("start_char", "")), "head", 0, filt_s, filt_d, filt_h
    )
    end_char = get_clean_char(
        to_katakana(d.get("end_char", "")), "head", 0, filt_s, filt_d, filt_h
    )

    # --- 辞書プール構築 ---
    raw_pool = []
    for cat in d.get("categories", ["country"]):
        raw_pool.extend(DICTIONARY_MASTER.get(cat, []))
    raw_pool = list(set(raw_pool))

    # --- 前処理フィルタ（高速化） ---
    temp_pool = []
    for w in raw_pool:
        if w in red_words:
            continue

        # valid_chars フィルタ
        if valid_chars:
            if not all(
                get_base_char(c, filt_s, filt_d, filt_h) in valid_chars
                for c in w.replace("ー", "")
            ):
                continue

        h_char = get_clean_char(w, "head", 0, filt_s, filt_d, filt_h)
        t_char = get_clean_char(w, "tail", 0, filt_s, filt_d, filt_h)

        if asc and h_char not in asc:
            continue
        if aec and t_char not in aec:
            continue

        norm_w = "".join([get_base_char(c, filt_s, filt_d, filt_h) for c in w])
        if any(ex in norm_w for ex in ex_list):
            continue
        if any(h_char == bs for bs in bs_list):
            continue

        temp_pool.append(w)

    # start_char が指定されていて start_word がない場合、開始候補をさらに絞る
    if start_char and not start_word:
        temp_pool = [
            w
            for w in temp_pool
            if get_clean_char(w, "head", 0, filt_s, filt_d, filt_h) == start_char
        ]

    # end_char が指定されている場合、終端候補を事前に絞る
    if end_char:
        end_variants_filter = get_variants(end_char, u_daku, u_handaku, filt_s)
        temp_pool = [
            w
            for w in temp_pool
            if get_clean_char(w, "tail", 0, filt_s, filt_d, filt_h)
            in end_variants_filter
        ]

    # 共役排除
    if d.get("exclude_conjugate"):
        pair_map = defaultdict(list)
        for w in temp_pool:
            ch = get_clean_char(w, "head", 0, conn_s, conn_d, conn_h)
            ct = get_clean_char(w, "tail", 0, conn_s, conn_d, conn_h)
            pair_map[f"{ch}_{ct}"].append(w)
        word_pool = []
        for words in pair_map.values():
            if len(words) == 1:
                word_pool.append(words[0])
    else:
        word_pool = temp_pool

    # --- キャッシュ構築（高速化） ---
    head_index = defaultdict(list)
    tail_index = defaultdict(list)
    head_cache = {}
    tail_cache = {}
    clean_cache = {}
    char_sets = {}

    for w in word_pool:
        h_conn = get_clean_char(w, "head", 0, conn_s, conn_d, conn_h)
        t_conn = get_clean_char(w, "tail", 0, conn_s, conn_d, conn_h)
        head_cache[w] = h_conn
        tail_cache[w] = t_conn
        head_index[h_conn].append(w)
        tail_index[t_conn].append(w)

        clean_cache[w] = w.replace("ー", "")
        char_sets[w] = set(
            get_base_char(c, filt_s, filt_d, filt_h) for c in w.replace("ー", "")
        )

    results = []
    start_time = time.time()

    target_total_len = int(d["target_total_len"]) if d.get("target_total_len") else None
    once_constraint = d.get("once_constraint", False)

    # group_constraints / choice_constraints は現状フロント未連携のため、ここでは常に True 扱い
    def check_list(_lst):
        return True

    # --- DFS 本体（高速化版） ---
    def solve(path, current_total_len, used_chars):
        # タイムアウト / 件数制限
        if time.time() - start_time > timeout:
            return
        if limit_en and len(results) >= limit:
            return

        # ttl の前倒し枝刈り
        if target_total_len is not None and current_total_len > target_total_len:
            return

        # 文字数構成（diff）の途中チェック
        if len_mode == "diff" and len(path) > 1:
            lens = [len(x) for x in path]
            if len(lens) != len(set(lens)):
                return

        # 完成判定
        if len(path) == max_len:
            if len_mode == "same" and len(set(len(x) for x in path)) > 1:
                return

            path_set = set(path)
            if not blue_words.issubset(path_set):
                return

            norm_t = "".join(
                [
                    get_base_char(c, filt_s, filt_d, filt_h)
                    for c in "".join(path).replace("ー", "")
                ]
            )

            if not (check_list(d.get("group_constraints", [])) and check_list(d.get("choice_constraints", []))):
                return

            if must_chars:
                for mc in must_chars:
                    cnt = norm_t.count(mc)
                    if cnt < 1:
                        return
                    if once_constraint and cnt != 1:
                        return

            if target_total_len is not None and current_total_len != target_total_len:
                return

            if end_char:
                last_tail = tail_cache[path[-1]]
                end_variants = get_variants(end_char, u_daku, u_handaku, conn_s)
                if last_tail not in end_variants:
                    return

            results.append(list(path))
            return

        # 残り手数で ttl に届かない場合の簡易枝刈り（最小長を 1 と仮定）
        if target_total_len is not None:
            remaining_steps = max_len - len(path)
            if current_total_len + remaining_steps > target_total_len:
                # まだ超えていないので OK（厳密な下限は計算しない）
                pass

        is_odd = (len(path) % 2 != 0)
        last_word = path[-1]
        last_word_clean = clean_cache[last_word]

        base_offsets = [p_shift]
        if d.get("auto_recovery"):
            base_offsets += list(range(p_shift + 1, len(last_word_clean)))

        for off in base_offsets:
            src = get_clean_char(
                last_word,
                ("tail" if not d.get("round_trip") or is_odd else "head"),
                off,
                conn_s,
                conn_d,
                conn_h,
            )
            if not src:
                continue

            # 50音ずらし
            raw_ts = set()
            if use_shift:
                if s_mode == "abs":
                    raw_ts.add(shift_kana_fast(src, abs(ks_val)))
                    raw_ts.add(shift_kana_fast(src, -abs(ks_val)))
                else:
                    raw_ts.add(shift_kana_fast(src, ks_val))
            else:
                raw_ts.add(src)

            targets = set()
            for rt in raw_ts:
                targets.update(get_variants(rt, u_daku, u_handaku, conn_s))

            found = False
            for tc in targets:
                cands = (
                    tail_index[tc]
                    if (d.get("round_trip") and is_odd)
                    else head_index[tc]
                )
                for nxt in cands:
                    if nxt in path:
                        continue

                    # 文字集合重複禁止（高速化版）
                    if d.get("char_limit_mode"):
                        if not char_sets[nxt].isdisjoint(used_chars):
                            continue

                    new_used = used_chars | char_sets[nxt]
                    solve(path + [nxt], current_total_len + len(nxt), new_used)
                    found = True
            if found:
                break

    # --- 探索開始 ---
    starts = [start_word] if start_word and start_word in word_pool else word_pool

    for w in sorted(starts):
        if not start_word and start_char:
            if get_clean_char(w, "head", 0, filt_s, filt_d, filt_h) != start_char:
                continue
        initial_used = char_sets[w].copy() if d.get("char_limit_mode") else set()
        solve([w], len(w), initial_used)

    # --- ソート ---
    sm = d.get("sort_mode", "default")
    if sm == "kana":
        results.sort()
    elif sm == "len_asc":
        results.sort(key=lambda x: len("".join(x)))
    elif sm == "len_desc":
        results.sort(key=lambda x: len("".join(x)), reverse=True)
    elif sm == "random":
        random.shuffle(results)

    return jsonify({"routes": results, "count": len(results)})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
```
