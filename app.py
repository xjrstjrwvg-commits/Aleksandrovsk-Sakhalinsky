import os, time, sys, re, math, random
from flask import Flask, render_template, request, jsonify
from collections import Counter, defaultdict

# 辞書データのインポート
try:
    from dictionary import DICTIONARY_MASTER
except ImportError:
    DICTIONARY_MASTER = {"country": ["ニホン", "イタリア", "アメリカ", "ドイツ"], "capital": ["トウキョウ", "ローマ"]}

sys.setrecursionlimit(20000)
app = Flask(__name__)

# --- 正規化用マッピング（独立分離） ---
SMALL_TO_LARGE = {"ァ": "ア", "ィ": "イ", "ゥ": "ウ", "ェ": "エ", "ォ": "オ", "ッ": "ツ", "ャ": "ヤ", "ュ": "ユ", "ョ": "ヨ", "ヮ": "ワ"}
DAKU_MAP = {"ガ":"カ", "ギ":"キ", "グ":"ク", "ゲ":"ケ", "ゴ":"コ", "ザ":"サ", "ジ":"シ", "ズ":"ス", "ゼ":"セ", "ゾ":"ソ", "ダ":"タ", "ヂ":"チ", "ヅ":"ツ", "デ":"テ", "ド":"ト", "バ":"ハ", "ビ":"ヒ", "ブ":"フ", "ベ":"ヘ", "ボ":"ホ"}
HANDAKU_MAP = {"パ":"ハ", "ピ":"ヒ", "プ":"フ", "ペ":"ヘ", "ポ":"ホ"}

def to_kana(text):
    if not text: return ""
    return "".join([chr(ord(c) + 96) if 0x3041 <= ord(c) <= 0x3096 else c for c in str(text)])

def get_base_char(c, unify_s=False, unify_d=False, unify_h=False):
    res = c
    if unify_s: res = SMALL_TO_LARGE.get(res, res)
    if unify_d: res = DAKU_MAP.get(res, res)
    if unify_h: res = HANDAKU_MAP.get(res, res)
    return res

def get_clean_char(w, pos="tail", offset=0, unify_s=False, unify_d=False, unify_h=False):
    text = to_kana(w).replace("ー", "")
    if not text or len(text) <= offset: return None
    try:
        idx = offset if pos == "head" else -(1 + offset)
        return get_base_char(text[idx], unify_s, unify_d, unify_h)
    except IndexError: return None

@app.route('/')
def index(): return render_template('index.html')

@app.route('/get_dictionary')
def get_dict(): return jsonify(DICTIONARY_MASTER)

@app.route('/search', methods=['POST'])
def search():
    try:
        d = request.get_json()
        
        max_len = int(d.get('max_len', 5))
        ks_abs = int(d.get('ks_abs', 0))
        p_shift = int(d.get('p_shift', 0))
        limit_x = int(d.get('limit_x', 100))
        timeout_val = int(d.get('timeout_val', 15))
        u_small = d.get('unify_small', False)
        u_daku = d.get('allow_daku', False)
        u_handaku = d.get('allow_handaku', False)
        early_stop = d.get('early_stop', True)
        
        def split_input(key):
            raw = d.get(key, "")
            return [to_kana(x.strip()) for x in re.split('[、,]', raw) if x.strip()]

        mc_raw_list = split_input('must_char')
        sc_req = to_kana(d.get('sc', ""))
        ec_req = to_kana(d.get('ec', ""))
        exc_chars = set([get_base_char(c, u_small, u_daku, u_handaku) for c in split_input('exc')])

        # 1. 辞書構築
        all_cats = d.get('categories', ["country"])
        red_words = set(d.get('red_words', []))
        blue_words = set(d.get('blue_words', []))
        word_pool = []
        all_pool_count = 0
        
        for cat in all_cats:
            pool = DICTIONARY_MASTER.get(cat, [])
            all_pool_count += len(pool)
            for w in pool:
                if w in red_words: continue
                w_norm = "".join([get_base_char(c, u_small, u_daku, u_handaku) for c in to_kana(w)])
                if exc_chars and not set(w_norm).isdisjoint(exc_chars): continue
                if d.get('exclude_conjugate') and get_clean_char(w, "head", 0, u_small, u_daku, u_handaku) == get_clean_char(w, "tail", 0, u_small, u_daku, u_handaku): continue
                word_pool.append(w)
        
        word_pool = sorted(list(set(word_pool)))
        head_idx = defaultdict(list)
        for w in word_pool:
            h = get_clean_char(w, "head", 0, u_small, u_daku, u_handaku)
            if h: head_idx[h].append(w)

        results = []
        start_time = time.time()

        # 2. 探索エンジン
        def solve(path, current_len):
            if time.time() - start_time > timeout_val: return
            if early_stop and len(results) >= limit_x: return

            if len(path) == max_len:
                full_norm = "".join([get_base_char(c, u_small, u_daku, u_handaku) for c in "".join([to_kana(w) for w in path])])
                
                if ec_req and get_clean_char(path[-1], "tail", 0, u_small, u_daku, u_handaku) != get_base_char(ec_req, u_small, u_daku, u_handaku): return
                if blue_words and not blue_words.issubset(set(path)): return
                if d.get('target_total') and current_len != int(d.get('target_total')): return
                
                for m in mc_raw_list:
                    char_part, target = (m.split(':') + ["1"])[:2]
                    target = int(target) if target.isdigit() else 1
                    search_char = get_base_char(to_kana(char_part), u_small, u_daku, u_handaku)
                    actual = full_norm.count(search_char)
                    if d.get('once_constraint'):
                        if actual != target: return
                    else:
                        if actual < target: return

                mo_list = split_input('must_order')
                if mo_list:
                    curr = 0
                    for c in mo_list:
                        curr = full_norm.find(get_base_char(c, u_small, u_daku, u_handaku), curr)
                        if curr == -1: return
                        curr += 1
                
                ec_list = split_input('edge_chars')
                if ec_list:
                    edges = {get_clean_char(w,"head",0,u_small,u_daku,u_handaku) for w in path} | {get_clean_char(w,"tail",0,u_small,u_daku,u_handaku) for w in path}
                    if not set([get_base_char(c, u_small, u_daku, u_handaku) for c in ec_list]).issubset(edges): return

                results.append(list(path))
                return

            src = get_clean_char(path[-1], "tail", p_shift, u_small, u_daku, u_handaku)
            if not src: return
            
            targets = {src}
            KANA_LIST = "アイウエオカキクケコガギグゲゴサシスセソザジズゼゾタチツテトダヂヅデドナニヌネノハヒフヘホバビブベボパピプペポマミムメモヤユヨラリルレロワン"
            if d.get('use_shift') and src in KANA_LIST:
                idx = KANA_LIST.index(src)
                if d.get('shift_mode') == 'abs': targets = {KANA_LIST[(idx+ks_abs)%len(KANA_LIST)], KANA_LIST[(idx-ks_abs)%len(KANA_LIST)]}
                else: targets = {KANA_LIST[(idx+ks_abs)%len(KANA_LIST)]}

            for t in targets:
                for nxt in head_idx.get(t, []):
                    if nxt in path: continue
                    if d.get('len_mode') == 'same' and len(nxt) != len(path): continue
                    if d.get('len_mode') == 'diff' and len(nxt) in [len(x) for x in path]: continue
                    if d.get('char_limit_mode') and not set("".join([to_kana(x) for x in path])).isdisjoint(set(to_kana(nxt))): continue
                    solve(path + [nxt], current_len + len(nxt))

        # 3. 実行
        sw = to_kana(d.get('start_word', ""))
        starts = [sw] if sw in word_pool else word_pool
        for w in starts:
            if sc_req and get_clean_char(w, "head", 0, u_small, u_daku, u_handaku) != get_base_char(sc_req, u_small, u_daku, u_handaku): continue
            if early_stop and len(results) >= limit_x: break
            solve([w], len(w))

        if d.get('sort_mode') == 'len_asc': results.sort(key=lambda x: (len("".join(x)), x))
        elif d.get('sort_mode') == 'len_desc': results.sort(key=lambda x: (len("".join(x)), x), reverse=True)
        elif d.get('sort_mode') == 'random': random.shuffle(results)
        else: results.sort()

        sol_c = len(results)
        Co, So, P = max_len**2, round(10/math.sqrt(sol_c+1), 2), 1+(p_shift*0.5)
        Sh = 1+(math.sqrt(ks_abs)*(2 if d.get('shift_mode')=='abs' else 1)) if d.get('use_shift') else 1
        Ch, L = (5 if d.get('char_limit_mode') else 1), (3 if d.get('len_mode')=='same' else 1.5 if d.get('len_mode')=='diff' else 1)
        Cw, Ex = (1.3 if d.get('rt') else 1), (1.5 if d.get('exclude_conjugate') else 1)
        n_sum = sum([int(m.split(':')[-1]) if ':' in m and m.split(':')[-1].isdigit() else 1 for m in mc_raw_list])
        Mc, On = 1.2**n_sum, (1+0.2*n_sum if d.get('once_constraint') else 1)
        Bl, Ed = 1.3**len(split_input('must_order')), 1.2**len(split_input('edge_chars'))
        Re, Ar = all_pool_count/(len(word_pool)+1), (0.7 if d.get('auto_recovery') else 1)
        Wi = (n_sum-max_len)**2 if (n_sum-max_len)**2 >=1 else 1
        score = int(round(Co*So*P*Sh*Ch*L*Cw*Ex*Mc*On*Bl*Re*Ar*Wi*Ed, 0))

        return jsonify({"routes": results, "count": sol_c, "score": score})
    except Exception as e: return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
