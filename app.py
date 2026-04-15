import os, time, sys, re, random
from flask import Flask, render_template, request, jsonify
from collections import Counter, defaultdict

# 外部化した辞書データをインポート
try:
    from dictionary import DICTIONARY_MASTER
except ImportError:
    DICTIONARY_MASTER = {"country": ["ニホン"], "capital": ["トウキョウ"]}

sys.setrecursionlimit(10000)
app = Flask(__name__)

# --- 定数・マッピング ---
KANA_LIST = (
    "アイウエオ" "カキクケコ" "ガギグゲゴ" "サシスセソ" "ザジズゼゾ"
    "タチツテト" "ダヂヅデド" "ナニヌネノ" "ハヒフヘホ" "バビブベボ"
    "パピプペポ" "マミムメモ" "ヤユヨ" "ラリルレロ" "ワン"
)
SMALL_TO_LARGE = {"ァ": "ア", "ィ": "イ", "ゥ": "ウ", "ェ": "エ", "ォ": "オ", "ッ": "ツ", "ャ": "ヤ", "ュ": "ユ", "ョ": "ヨ", "ヮ": "ワ"}
DAKU_MAP = {"カ":"ガ", "キ":"ギ", "ク":"グ", "ケ":"ゲ", "コ":"ゴ", "サ":"ザ", "シ":"ジ", "ス":"ズ", "セ":"ゼ", "ソ":"ゾ", "タ":"ダ", "チ":"ヂ", "ツ":"ヅ", "テ":"デ", "ト":"ド", "ハ":"バ", "ヒ":"ビ", "フ":"ブ", "ヘ":"ベ", "ホ":"ボ"}
HANDAKU_MAP = {"ハ":"パ", "ヒ":"ピ", "フ":"プ", "ヘ":"ペ", "ホ":"ポ"}

REV_DAKU = {v: k for k, v in DAKU_MAP.items()}
REV_HANDAKU = {v: k for k, v in HANDAKU_MAP.items()}

# --- ユーティリティ ---
def to_katakana(text):
    if not text: return ""
    return "".join([chr(ord(c) + 96) if 0x3041 <= ord(c) <= 0x3096 else c for c in text])

def get_base_char(c, unify_small=False, unify_daku=False, unify_handaku=False):
    res = SMALL_TO_LARGE.get(c, c) if unify_small else c
    if unify_daku: res = REV_DAKU.get(res, res)
    if unify_handaku: res = REV_HANDAKU.get(res, res)
    return res

def get_clean_char(w, pos="head", offset=0, unify_s=False, unify_d=False, unify_h=False):
    text = w.replace("ー", "")
    if not text: return ""
    try:
        idx = offset if pos == "head" else -(1 + offset)
        char = text[idx]
        return get_base_char(char, unify_s, unify_d, unify_h)
    except IndexError: return ""

def shift_kana(char, n):
    if char not in KANA_LIST: return char
    return KANA_LIST[(KANA_LIST.index(char) + n) % len(KANA_LIST)]

def get_variants(char, allow_daku, allow_handaku, unify=False):
    base = SMALL_TO_LARGE.get(char, char) if unify else char
    variants = {base}
    if allow_daku:
        for k, v in DAKU_MAP.items():
            if base == k: variants.add(v)
            if base == v: variants.add(k)
    if allow_handaku:
        for k, v in HANDAKU_MAP.items():
            if base == k: variants.add(v)
            if base == v: variants.add(k)
    return variants

@app.route('/')
def index(): return render_template('index.html')

@app.route('/get_dictionary')
def get_dictionary(): return jsonify(DICTIONARY_MASTER)

@app.route('/search', methods=['POST'])
def search():
    d = request.json
    timeout, limit, limit_en = int(d.get('timeout', 15)), int(d.get('limit', 1500)), d.get('limit_enabled', True)
    max_len, p_shift = int(d.get('max_len', 5)), int(d.get('pos_shift', 0))
    use_shift, ks_val, s_mode = d.get('use_shift', False), int(d.get('ks_abs', 1)), d.get('shift_mode', 'abs')
    
    u_small, u_daku, u_handaku = d.get('unify_small', False), d.get('allow_daku', False), d.get('allow_handaku', False)
    scope = d.get('unify_scope', 'all')
    
    conn_s, conn_d, conn_h = (u_small and scope in ['all', 'conn']), (u_daku and scope in ['all', 'conn']), (u_handaku and scope in ['all', 'conn'])
    filt_s, filt_d, filt_h = (u_small and scope in ['all', 'filter']), (u_daku and scope in ['all', 'filter']), (u_handaku and scope in ['all', 'filter'])

    len_mode = d.get('len_mode', 'free')
    raw_valid = to_katakana(d.get('valid_chars', ""))
    valid_chars = set(raw_valid.replace("、", "").replace(",", "")) if raw_valid else None

    red_words, blue_words = set(d.get('red_words', [])), set(d.get('blue_words', []))
    asc = [get_clean_char(c.strip(), "head", 0, filt_s, filt_d, filt_h) for c in re.split('[、,]', to_katakana(d.get('all_start_char', ""))) if c.strip()]
    aec = [get_clean_char(c.strip(), "head", 0, filt_s, filt_d, filt_h) for c in re.split('[、,]', to_katakana(d.get('all_end_char', ""))) if c.strip()]
    ex_list = [get_base_char(c.strip(), filt_s, filt_d, filt_h) for c in re.split('[、,]', to_katakana(d.get('exclude_chars', ""))) if c.strip()]
    bs_list = [get_base_char(c.strip(), filt_s, filt_d, filt_h) for c in re.split('[、,]', to_katakana(d.get('ban_start_chars', ""))) if c.strip()]
    must_chars = [get_base_char(c, filt_s, filt_d, filt_h) for c in re.split('[、,]', to_katakana(d.get('must_char', ""))) if c]
    
    start_word = to_katakana(d.get('start_word', ""))
    start_char = get_clean_char(to_katakana(d.get('start_char', "")), "head", 0, filt_s, filt_d, filt_h)
    end_char = get_clean_char(to_katakana(d.get('end_char', "")), "head", 0, filt_s, filt_d, filt_h)

    raw_pool = []
    for cat in d.get('categories', ["country"]): raw_pool.extend(DICTIONARY_MASTER.get(cat, []))
    raw_pool = list(set(raw_pool))

    word_pool = []
    for w in raw_pool:
        if w in red_words: continue
        # 餡式必須がONの場合、2文字以下の単語（餡がないもの）を禁止
        if d.get('ansiki_mode') and len(w.replace("ー", "")) <= 2: continue
        if valid_chars and not all(get_base_char(c, filt_s, filt_d, filt_h) in valid_chars for c in w.replace("ー", "")): continue
        h_char = get_clean_char(w, "head", 0, filt_s, filt_d, filt_h)
        t_char = get_clean_char(w, "tail", 0, filt_s, filt_d, filt_h)
        if asc and h_char not in asc: continue
        if aec and t_char not in aec: continue
        norm_w = "".join([get_base_char(c, filt_s, filt_d, filt_h) for c in w])
        if any(ex in norm_w for ex in ex_list): continue
        if any(h_char == bs for bs in bs_list): continue
        word_pool.append(w)

    head_index = defaultdict(list)
    for w in word_pool:
        head_index[get_clean_char(w, "head", 0, conn_s, conn_d, conn_h)].append(w)

    results, start_time = [], time.time()

    def solve(path, current_total_len):
        if time.time() - start_time > timeout or (limit_en and len(results) >= limit): return
        
        if len(path) == max_len:
            path_set = set(path)
            if not blue_words.issubset(path_set): return
            results.append(list(path))
            return
        
        # 次の単語の候補を選定
        if d.get('ansiki_mode'):
            # 餡式必須モード：しりとりを無視し、プール全体を候補とする
            cands = word_pool
        else:
            # 通常モード：しりとり接続
            src = get_clean_char(path[-1], "tail", p_shift, conn_s, conn_d, conn_h)
            if not src: return
            targets = get_variants(src, u_daku, u_handaku, conn_s)
            cands = []
            for tc in targets:
                cands.extend(head_index.get(tc, []))

        for nxt in cands:
            if nxt in path: continue
            
            # 共通ルール：餡（中間文字）の包含チェック
            if d.get('ansiki_mode'):
                prev_clean = path[-1].replace("ー", "")
                # 最初と最後を除いた文字（餡）を抽出
                middle_chars = [get_base_char(c, filt_s, filt_d, filt_h) for c in prev_clean[1:-1]]
                nxt_norm = "".join([get_base_char(c, filt_s, filt_d, filt_h) for c in nxt])
                if not all(nxt_norm.count(mc) >= 1 for mc in middle_chars):
                    continue

            # 文字重複制限
            if d.get('char_limit_mode'):
                p_txt = "".join([get_base_char(c, filt_s, filt_d, filt_h) for c in "".join(path)])
                n_txt = "".join([get_base_char(c, filt_s, filt_d, filt_h) for c in nxt])
                if not set(p_txt).isdisjoint(set(n_txt)): continue
            
            solve(path + [nxt], current_total_len + len(nxt))

    starts = [start_word] if start_word in word_pool else word_pool
    for w in sorted(starts):
        if not start_word and start_char and get_clean_char(w, "head", 0, filt_s, filt_d, filt_h) != start_char: continue
        solve([w], len(w))
    
    return jsonify({"routes": results, "count": len(results)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
