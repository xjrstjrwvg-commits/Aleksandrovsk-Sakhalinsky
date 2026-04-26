import os, time, sys, re, math, random, traceback
from flask import Flask, render_template, request, jsonify
from collections import Counter, defaultdict

try:
    from dictionary import DICTIONARY_MASTER
except ImportError:
    # 辞書ファイルがない場合のテスト用データ
    DICTIONARY_MASTER = {
        "country": ["ニホン", "イタリア", "アメリカ", "ドイツ", "オーストラリア", "オーストリア", "ブラジル"],
        "capital": ["トウキョウ", "ローマ", "ベルリン"]
    }

sys.setrecursionlimit(20000)
app = Flask(__name__)

# --- 極・専用順番表 (全75文字) ---
KANA_ORDER = (
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
    "ッ": "ツ", "ャ": "ヤ", "ュ": "ユ", "ョ": "ヨ", "ヮ": "ワ",
    "ヵ": "カ", "ヶ": "ケ"
}

def to_kana(text):
    if not text: return ""
    return "".join([chr(ord(c) + 96) if 0x3041 <= ord(c) <= 0x3096 else c for c in str(text)]).replace("ー", "")

def get_base_char(c):
    return SMALL_TO_LARGE.get(c, c)

def get_clean_char(w, pos="tail", offset=0):
    text = to_kana(w)
    if not text: return None
    try:
        # 物理オフセットの計算
        idx = offset if pos == "head" else -(1 + offset)
        if 0 <= (idx if idx >= 0 else len(text) + idx) < len(text):
            return get_base_char(text[idx])
        return None
    except: return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_dictionary')
def get_dict():
    return jsonify(DICTIONARY_MASTER)

@app.route('/search', methods=['POST'])
def search():
    try:
        d = request.get_json()
        if not d: return jsonify({"error": "Invalid request"}), 400

        max_len = int(d.get('max_len', 5))
        ks_abs = int(d.get('ks_abs', 0))
        p_shift = int(d.get('p_shift', 0))
        limit_x = int(d.get('limit_x', 100))
        timeout_val = int(d.get('timeout_val', 15))
        early_stop = d.get('early_stop', True)
        
        def split_input(key):
            raw = d.get(key, "")
            return [to_kana(x.strip()) for x in re.split('[、,]', raw) if x.strip()]

        mc_raw_list = split_input('must_char')
        sc_req = to_kana(d.get('sc', ""))
        ec_req = to_kana(d.get('ec', ""))
        exc_chars = set([get_base_char(c) for c in split_input('exc')])

        # 1. 辞書構築とフィルタリング
        all_cats = d.get('categories', ["country", "capital"])
        raw_pool = []
        for cat in all_cats:
            raw_pool.extend(DICTIONARY_MASTER.get(cat, []))
        raw_pool = list(set(raw_pool))

        red_words, blue_words = set(d.get('red_words', [])), set(d.get('blue_words', []))
        
        # 共役排除
        if d.get('exclude_conjugate'):
            edge_map = defaultdict(list)
            for w in raw_pool:
                h, t = get_clean_char(w, "head", 0), get_clean_char(w, "tail", 0)
                if h and t: edge_map[(h, t)].append(w)
            for ws in edge_map.values():
                if len(ws) > 1: red_words.update(ws)

        word_pool = []
        for w in raw_pool:
            if w in red_words: continue
            w_norm = "".join([get_base_char(c) for c in to_kana(w)])
            if exc_chars and not set(w_norm).isdisjoint(exc_chars): continue
            word_pool.append(w)

        head_idx = defaultdict(list)
        for w in word_pool:
            h = get_clean_char(w, "head", 0)
            if h: head_idx[h].append(w)

        results = []
        start_time = time.time()

        # 2. 探索ロジック
        def solve(path, used_chars, current_total_len):
            if time.time() - start_time > timeout_val or (early_stop and len(results) >= limit_x): return
            
            if len(path) == max_len:
                full_norm = "".join([get_base_char(c) for c in "".join([to_kana(w) for w in path])])
                # 制約判定
                if ec_req and get_clean_char(path[-1], "tail", 0) != get_base_char(ec_req): return
                if blue_words and not blue_words.issubset(set(path)): return
                if d.get('target_total') and current_total_len != int(d.get('target_total')): return
                
                for m in mc_raw_list:
                    parts = m.split(':')
                    char_part = parts[0]
                    target = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 1
                    actual = full_norm.count(get_base_char(to_kana(char_part)))
                    if d.get('once_constraint'):
                        if actual != target: return
                    else:
                        if actual < target: return
                
                # 正順
                mo_list = split_input('must_order')
                if mo_list:
                    curr = 0
                    for c in mo_list:
                        curr = full_norm.find(get_base_char(c), curr)
                        if curr == -1: return
                        curr += 1

                results.append(list(path))
                return

            tail_char = get_clean_char(path[-1], "tail", p_shift)
            if not tail_char: return
            
            # ずらし計算
            if tail_char in KANA_ORDER:
                idx = KANA_ORDER.index(tail_char)
                next_start = KANA_ORDER[(idx + ks_abs) % len(KANA_ORDER)]
            else:
                next_start = tail_char

            for nxt in head_idx.get(next_start, []):
                if nxt in path: continue
                nxt_kana = to_kana(nxt)
                if d.get('char_limit_mode') and not set(nxt_kana).isdisjoint(used_chars): continue
                solve(path + [nxt], used_chars | set(nxt_kana), current_total_len + len(nxt))

        # 3. 実行
        sw = to_kana(d.get('start_word', ""))
        starts = [sw] if sw in word_pool else word_pool
        for w in starts:
            if sc_req and get_clean_char(w, "head", 0) != get_base_char(sc_req): continue
            solve([w], set(to_kana(w)), len(w))

        # ソート
        sort_mode = d.get('sort_mode', 'default')
        if sort_mode == 'len_asc': results.sort(key=lambda x: (len("".join(x)), x))
        elif sort_mode == 'len_desc': results.sort(key=lambda x: (len("".join(x)), x), reverse=True)
        elif sort_mode == 'random': random.shuffle(results)
        else: results.sort()

        # スコア計算 (0件ガード)
        sol_c = len(results)
        if sol_c == 0:
            return jsonify({"routes": [], "count": 0, "score": 0})

        score = int((max_len**2) * (10 / math.sqrt(sol_c + 1)) * (1 + abs(p_shift)*0.5) * (1 + abs(ks_abs)*0.2))
        if d.get('char_limit_mode'): score *= 5

        return jsonify({"routes": results, "count": sol_c, "score": score})

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
