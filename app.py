import os, time, sys, re, math, random
from flask import Flask, render_template, request, jsonify
from collections import defaultdict

try:
    from dictionary import DICTIONARY_MASTER
except ImportError:
    DICTIONARY_MASTER = {
        "country": ["ニホン", "イタリア", "アメリカ", "ドイツ", "オーストラリア", "オーストリア", "ブラジル"],
        "capital": ["トウキョウ", "ローマ", "ベルリン"]
    }

sys.setrecursionlimit(20000)
app = Flask(__name__)

# --- ずらししりとり基本順番表 (全75文字) ---
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

# 小文字から大文字への変換マップ
SMALL_TO_LARGE = {
    "ァ": "ア", "ィ": "イ", "ゥ": "ウ", "ェ": "エ", "ォ": "オ",
    "ッ": "ツ", "ャ": "ヤ", "ュ": "ユ", "ョ": "ヨ", "ヮ": "ワ",
    "ヵ": "カ", "ヶ": "ケ"
}

def to_kana(text):
    if not text: return ""
    # ひらがなをカタカナに、長音「ー」を除去
    return "".join([chr(ord(c) + 96) if 0x3041 <= ord(c) <= 0x3096 else c for c in str(text)]).replace("ー", "")

def get_base_char(c):
    # 小文字を大文字に正規化
    return SMALL_TO_LARGE.get(c, c)

def get_clean_char(w, pos="tail", offset=0):
    text = to_kana(w)
    if not text or len(text) <= abs(offset): return None
    try:
        # 物理オフセット適用 (headなら前から、tailなら後ろから)
        idx = offset if pos == "head" else -(1 + offset)
        return get_base_char(text[idx])
    except IndexError: return None

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
        max_len = int(d.get('max_len', 5))
        ks_abs = int(d.get('ks_abs', 0))
        p_shift = int(d.get('p_shift', 0))
        limit_x = int(d.get('limit_x', 100))
        timeout_val = int(d.get('timeout_val', 15))
        early_stop = d.get('early_stop', True)
        char_limit_mode = d.get('char_limit_mode', True)
        
        # 1. 辞書構築とフィルタリング
        all_cats = d.get('categories', ["country", "capital"])
        raw_pool = []
        for cat in all_cats:
            raw_pool.extend(DICTIONARY_MASTER.get(cat, []))
        raw_pool = list(set(raw_pool))

        red_words = set(d.get('red_words', []))
        
        # 【共役排除ルール】
        # 開始字・終了字のペアが共通する単語が存在する場合、そのペアに属する単語をすべて除外
        if d.get('exclude_conjugate'):
            edge_map = defaultdict(list)
            for w in raw_pool:
                h = get_clean_char(w, "head", 0)
                t = get_clean_char(w, "tail", 0)
                if h and t:
                    edge_map[(h, t)].append(w)
            for key, words in edge_map.items():
                if len(words) > 1:
                    red_words.update(words)

        word_pool = [w for w in raw_pool if w not in red_words]
        
        # インデックス構築 (開始文字 -> [単語リスト])
        head_idx = defaultdict(list)
        for w in word_pool:
            h = get_clean_char(w, "head", 0)
            if h: head_idx[h].append(w)

        results = []
        start_time = time.time()

        # 2. 探索エンジン (再帰)
        def solve(path, used_chars):
            # タイムアウトと最大件数チェック
            if time.time() - start_time > timeout_val: return
            if early_stop and len(results) >= limit_x: return

            # 目標連鎖数に到達
            if len(path) == max_len:
                results.append(list(path))
                return

            # 前の単語の末尾から、次の開始文字を計算 (物理/ずらし適用)
            last_word = path[-1]
            tail_char = get_clean_char(last_word, "tail", p_shift)
            
            if not tail_char: return
            
            # ずらししりとりルール適用
            if tail_char in KANA_ORDER:
                curr_idx = KANA_ORDER.index(tail_char)
                # 全75文字でループ計算 (「ン」の次は「ア」)
                target_idx = (curr_idx + ks_abs) % len(KANA_ORDER)
                next_start = KANA_ORDER[target_idx]
            else:
                next_start = tail_char

            # 次の単語候補を探索
            for nxt in head_idx.get(next_start, []):
                # 単語重複禁止
                if nxt in path: continue
                
                nxt_kana = to_kana(nxt)
                # 【重複禁止ルール】一文字でも既出文字があれば除外
                if char_limit_mode:
                    if not set(nxt_kana).isdisjoint(used_chars):
                        continue
                
                solve(path + [nxt], used_chars | set(nxt_kana))

        # 開始
        sw = to_kana(d.get('start_word', ""))
        starts = [sw] if sw in word_pool else word_pool
        
        for w in starts:
            # 初期単語の全文字をused_charsに入れて開始
            solve([w], set(to_kana(w)))

        return jsonify({"routes": results, "count": len(results)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
