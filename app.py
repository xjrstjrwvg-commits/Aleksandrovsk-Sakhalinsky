import os, time, sys, re, random
from flask import Flask, render_template, request, jsonify
from collections import Counter, defaultdict
# 外部化した辞書データをインポート
from dictionary import DICTIONARY_MASTER

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

# --- ユーティリティ ---
def to_katakana(text):
    if not text: return ""
    return "".join([chr(ord(c) + 96) if 0x3041 <= ord(c) <= 0x3096 else c for c in text])

def get_clean_char(w, pos="head", offset=0, unify=False):
    # 長音を除去して判定対象にする
    text = w.replace("ー", "")
    if not text: return ""
    try:
        # pos="tail" の場合、末尾(0)から数えて offset 分手前を取得
        # offset=2 の場合、末尾から3番目の文字 text[-3] を指す
        idx = offset if pos == "head" else -(1 + offset)
        char = text[idx]
        return SMALL_TO_LARGE.get(char, char) if unify else char
    except IndexError:
        # 文字数が足りない（例：2文字の単語で offset=2 を指定）場合は空を返す
        return ""

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
    max_len, p_shift, use_shift, ks_val, s_mode = int(d.get('max_len', 5)), int(d.get('pos_shift', 0)), d.get('use_shift', False), int(d.get('ks_abs', 1)), d.get('shift_mode', 'abs')
    allow_daku, allow_handaku, unify_small = d.get('allow_daku', False), d.get('allow_handaku', False), d.get('unify_small', False)
    u_scope = d.get('unify_scope', 'all')
    u_conn = unify_small and u_scope in ['all', 'conn']
    u_filt = unify_small and u_scope in ['all', 'filter']
    
    red_words, blue_words = set(d.get('red_words', [])), set(d.get('blue_words', []))
    asc = [get_clean_char(c.strip(), "head", 0, u_filt) for c in re.split('[、,]', to_katakana(d.get('all_start_char', ""))) if c.strip()]
    aec = [get_clean_char(c.strip(), "head", 0, u_filt) for c in re.split('[、,]', to_katakana(d.get('all_end_char', ""))) if c.strip()]
    ex_list = [SMALL_TO_LARGE.get(c.strip(), c.strip()) if u_filt else c.strip() for c in re.split('[、,]', to_katakana(d.get('exclude_chars', ""))) if c.strip()]
    bs_list = [SMALL_TO_LARGE.get(c.strip(), c.strip()) if u_filt else c.strip() for c in re.split('[、,]', to_katakana(d.get('ban_start_chars', ""))) if c.strip()]
    must_chars = [SMALL_TO_LARGE.get(c, c) if u_filt else c for c in re.split('[、,]', to_katakana(d.get('must_char', ""))) if c]
    
    start_word = to_katakana(d.get('start_word', ""))
    start_char = get_clean_char(to_katakana(d.get('start_char', "")), "head", 0, u_filt)
    end_char = get_clean_char(to_katakana(d.get('end_char', "")), "head", 0, u_filt)

    raw_pool = []
    for cat in d.get('categories', ["country"]): raw_pool.extend(DICTIONARY_MASTER.get(cat, []))
    raw_pool = list(set(raw_pool))

    conjugates = set()
    if d.get('exclude_conjugate'):
        combo_c = Counter()
        w_to_combo = {}
        for w in raw_pool:
            c = (get_clean_char(w, "head", 0, u_filt), get_clean_char(w, "tail", 0, u_filt))
            combo_c[c] += 1
            w_to_combo[w] = c
        conjugates = {w for w, c in w_to_combo.items() if combo_c[c] > 1}

    word_pool = []
    for w in raw_pool:
        if w in red_words or w in conjugates: continue
        if asc and get_clean_char(w, "head", 0, u_filt) not in asc: continue
        if aec and get_clean_char(w, "tail", 0, u_filt) not in aec: continue
        norm_w = "".join([SMALL_TO_LARGE.get(c, c) for c in w]) if u_filt else w
        if any(ex in norm_w for ex in ex_list): continue
        if any(get_clean_char(w, "head", 0, u_filt) == bs for bs in bs_list): continue
        word_pool.append(w)
    
    word_pool = list(set(word_pool))
    head_index, tail_index = defaultdict(list), defaultdict(list)
    for w in word_pool:
        head_index[get_clean_char(w, "head", 0, u_conn)].append(w)
        tail_index[get_clean_char(w, "tail", 0, u_conn)].append(w)

    results, start_time = [], time.time()

    def solve(path, current_total_len):
        if time.time() - start_time > timeout or (limit_en and len(results) >= limit): return
        if len(path) == max_len:
            path_set = set(path)
            if not blue_words.issubset(path_set): return
            full_t = "".join(path)
            norm_t = "".join([SMALL_TO_LARGE.get(c, c) for c in full_t]) if u_filt else full_t

            def check_list(lst):
                for group in lst:
                    target_cnt, g_shift, items = 1, 0, []
                    for itm in group:
                        if ':' in itm:
                            ps = itm.split(':')
                            if ps[0].upper() == 'S': g_shift = int(ps[1])
                            else: target_cnt = int(ps[1] if ps[1].isdigit() else ps[0])
                        else: items.append(itm)
                    total = 0
                    for it in items:
                        shifted = "".join([shift_kana(c, g_shift) for c in it])
                        norm_it = "".join([SMALL_TO_LARGE.get(c, c) for c in shifted]) if u_filt else shifted
                        total += norm_t.count(norm_it)
                    if (d.get('exclusive_choice') and total != target_cnt) or (not d.get('exclusive_choice') and total < target_cnt): return False
                return True

            if not check_list(d.get('group_constraints', [])): return
            if not check_list(d.get('choice_constraints', [])): return
            if must_chars:
                if d.get('once_constraint'):
                    if not all(norm_t.count(mc) == 1 for mc in must_chars): return
                elif not all(mc in norm_t for mc in must_chars): return
            if d.get('target_total_len') and current_total_len != int(d['target_total_len']): return
            if end_char and get_clean_char(path[-1], "tail", 0, u_conn) not in get_variants(end_char, allow_daku, allow_handaku, u_conn): return
            results.append(list(path))
            return
        
        is_odd = (len(path) % 2 != 0)
        # 物理ずらしのロジック: p_shift 分だけ手前から抽出。足りなければ空文字となりループ終了（打ち切り）
        base_offsets = [p_shift] + ([i for i in range(p_shift+1, len(path[-1].replace("ー","")))] if d.get('auto_recovery') else [])
        
        for off in base_offsets:
            if d.get('round_trip'):
                src = get_clean_char(path[-1], "tail" if is_odd else "head", off, u_conn)
            else:
                src = get_clean_char(path[-1], "tail", off, u_conn)
            
            # get_clean_char で文字が取れなかった場合（打ち切り条件）、次のオフセットへ行くか探索終了
            if not src: continue

            raw_ts = {shift_kana(src, ks_val if s_mode!='abs' else abs(ks_val)), shift_kana(src, -abs(ks_val)) if s_mode=='abs' else src} if use_shift else {src}
            targets = set()
            for rt in raw_ts: targets.update(get_variants(rt, allow_daku, allow_handaku, u_conn))
            found = False
            for tc in targets:
                cands = (tail_index if (d.get('round_trip') and is_odd) else head_index).get(tc, [])
                for nxt in cands:
                    if nxt in path: continue
                    if d.get('char_limit_mode'):
                        p_txt = "".join([SMALL_TO_LARGE.get(c,c) for c in "".join(path)]) if u_filt else "".join(path)
                        n_txt = "".join([SMALL_TO_LARGE.get(c,c) for c in nxt]) if u_filt else nxt
                        if not set(p_txt).isdisjoint(set(n_txt)): continue
                    found = True
                    solve(path + [nxt], current_total_len + len(nxt))
            if found: break

    starts = [start_word] if start_word in word_pool else word_pool
    for w in sorted(starts):
        if not start_word and start_char and get_clean_char(w, "head", 0, u_filt) != start_char: continue
        solve([w], len(w))
    
    sm = d.get('sort_mode', 'default')
    if sm == 'kana': results.sort()
    elif sm == 'len_asc': results.sort(key=lambda x: len("".join(x)))
    elif sm == 'len_desc': results.sort(key=lambda x: len("".join(x)), reverse=True)
    elif sm == 'random': random.shuffle(results)
    return jsonify({"routes": results, "count": len(results)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
