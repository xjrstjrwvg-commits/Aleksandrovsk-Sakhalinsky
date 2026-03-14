import os, time, sys, re
from flask import Flask, render_template, request, jsonify
from collections import Counter, defaultdict

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

# --- 辞書データ ---
DICTIONARY_MASTER = {
    "country": [
        "アイスランド", "アイルランド", "アゼルバイジャン", "アフガニスタン", "アメリカ", 
        "アラブシュチョウコクレンポウ", "アルジェリア", "アルゼンチン", "アルバニア", "アルメニア", 
        "アンゴラ", "アンティグアバーブーダ", "アンドラ", "イエメン", "イギリス", "イスラエル", 
        "イタリア", "イラク", "イラン", "インド", "インドネシア", "ウガンダ", "ウクライナ", 
        "ウズベキスタン", "ウルグアイ", "エクアドル", "エジプト", "エストニア", "エスワティニ", 
        "エチオピア", "エリトリア", "エルサルバドル", "オーストラリア", "オーストリア", "オマーン", 
        "オランダ", "ガーナ", "カーボベルデ", "ガイアナ", "カザフスタン", "カタール", "カナダ", 
        "ガボン", "カメルーン", "ガンビア", "カンボジア", "キタマケドニア", "ギニア", "ギニアビサウ", 
        "キプロス", "キューバ", "ギリシャ", "キリバス", "キルギス", "グアテマラ", "クウェート", 
        "クックショトウ", "グレナダ", "クロアチア", "ケニア", "コートジボワール", "コスタリカ", 
        "コソボ", "コモロ", "コロンビア", "コンゴキョウワコク", "コンゴミンシュキョウワコク", 
        "サウジアラビア", "サモア", "サントメプリンシペ", "ザンビア", "サンマリノ", "シエラレオネ", 
        "ジブチ", "ジャマイカ", "ジョージア", "シリア", "シンガポール", "ジンバブエ", "スイス", 
        "スウェーデン", "スーダン", "スペイン", "スリナム", "スリランカ", "スロバキア", "スロベニア", 
        "セーシェル", "セキドウギニア", "セネガル", "セルビア", "セントクリストファーネービス", 
        "セントビンセントグレナディーンショトウ", "セントルシア", "ソマリア", "ソロモンショトウ", 
        "タイ", "ダイカンミンコク", "タジキスタン", "タンザニア", "チェコ", "チャド", "チュウオウアフリカ", 
        "チュウカジンミンキョウワコク", "チュニジア", "チョウセンミンシュシュギジンミンキョウワコク", 
        "チリ", "ツバル", "デンマーク", "ドイツ", "トーゴ", "ドミニカキョウワコク", "ドミニカコク", 
        "トリニダードトバゴ", "トルクメニスタン", "トルコ", "トンガ", "ナイジェリア", "ナウル", 
        "ナミビア", "ニウエ", "ニカラグア", "ニジェール", "ニホン", "ニュージーランド", "ネパール", 
        "ノルウェー", "バーレーン", "ハイチ", "パキスタン", "バチカンシコク", "パナマ", "バヌアツ", 
        "バハマ", "パプアニューギニア", "パラオ", "パラグアイ", "バルバドス", "ハンガリー", 
        "バングラデシュ", "ヒガシティモール", "フィジー", "フィリピン", "フィンランド", "ブータン", 
        "ブラジル", "フランス", "ブルガリア", "ブルキナファソ", "ブルネイ", "ブルンジ", "ベトナム", 
        "ベナン", "ベネズエラ", "ベラルーシ", "ベリーズ", "ペルー", "ベルギー", "ポーランド", 
        "ボスニアヘルツェゴビナ", "ボツワナ", "ボリビア", "ポルトガル", "ホンジュラス", 
        "マーシャルショトウ", "マダガスカル", "マラウイ", "マリ", "マルタ", "マレーシア", 
        "ミクロネシアレンポウ", "ミナミアフリカキョウワコク", "ミナミスーダン", "ミャンマー", 
        "メキシコ", "モーリシャス", "モーリタニア", "モザンビーク", "モナコ", "モルディブ", 
        "モルドバ", "モロッコ", "モンゴル", "モンテネグロ", "ヨルダン", "ラオス", "ラトビア", 
        "リトアニア", "リビア", "リヒテンシュタイン", "リベリア", "ルーマニア", "ルクセンブルク", 
        "ルワンダ", "レソト", "レバノン", "ロシア"
    ],
    "capital": [
        "アクラ", "アシガバット", "アスタナ", "アスマラ", "アスンシオン", "アディスアベバ", 
        "アテネ", "アバルア", "アピア", "アブジャ", "アブダビ", "アムステルダム", "アルジェ", 
        "アロフィ", "アンカラ", "アンタナナリボ", "アンドララベリャ", "アンマン", "イスラマバード", 
        "ウィーン", "ウィントフック", "ウェリントン", "ウランバートル", "エルサレム", "エレバン", 
        "オスロ", "オタワ", "カイロ", "カストリーズ", "カトマンズ", "カブール", "カラカス", 
        "カンパラ", "キーウ", "キガリ", "キシナウ", "ギテガ", "キト", "キャンベラ", "キングスタウン", 
        "キングストン", "キンシャサ", "グアテマラシティ", "クアラリンプール", "クウェート", 
        "コナクリ", "コペンハーゲン", "ザグレブ", "サヌア", "サラエボ", "サンサルバドル", 
        "サンティアゴ", "サントドミンゴ", "サントメ", "サンホセ", "サンマリノ", "ジブチ", 
        "ジャカルタ", "ジュバ", "ジョージタウン", "シンガポール", "スコピエ", "ストックホルム", 
        "スバ", "スリジャヤワルダナプラコッテ", "セントジョージズ", "セントジョンズ", "ソウル", 
        "ソフィア", "ダカール", "タシケント", "ダッカ", "ダブリン", "ダマスカス", "タラワ", 
        "タリン", "チュニス", "ティラナ", "ディリ", "ティンプー", "テグシガルパ", "テヘラン", 
        "デリー", "トウキョウ", "ドゥシャンベ", "ドーハ", "ドドマ", "トビリシ", "トリポリ", 
        "ナイロビ", "ナッソー", "ニアメ", "ニコシア", "ヌアクショット", "ヌクアロファ", "ネピドー", 
        "バクー", "バグダッド", "バセテール", "パナマシティ", "バチカン", "ハノイ", "ハバナ", 
        "ハボローネ", "バマコ", "パラマリボ", "ハラレ", "パリ", "パリキール", "ハルツーム", 
        "バレッタ", "バンギ", "バンコク", "バンジュール", "バンダルスリブガワン", "ビエンチャン", 
        "ビクトリア", "ビサウ", "ビシュケク", "ピョンヤン", "ビリニュス", "ファドゥーツ", 
        "ブエノスアイレス", "ブカレスト", "ブダペスト", "フナフティ", "プノンペン", "プライア", 
        "ブラザビル", "ブラジリア", "ブラチスラバ", "プラハ", "フリータウン", "プリシュティナ", 
        "ブリッジタウン", "ブリュッセル", "プレトリア", "ベイルート", "ベオグラード", "ペキン", 
        "ヘルシンキ", "ベルモパン", "ベルリン", "ベルン", "ポートオブスペイン", "ポートビラ", 
        "ポートモレスビー", "ポートルイス", "ボゴタ", "ポドゴリツァ", "ホニアラ", "ポルトープランス", 
        "ポルトノボ", "マジュロ", "マスカット", "マセル", "マドリード", "マナーマ", "マナグア", 
        "マニラ", "マプト", "マラボ", "マルキョク", "マレ", "ミンスク", "ムババーネ", "メキシコシティ", 
        "モガディシュ", "モスクワ", "モナコ", "モロニ", "モンテビデオ", "モンロビア", "ヤウンデ", 
        "ヤムスクロ", "ヤレン", "ラパス", "ラバト", "リーブルビル", "リガ", "リスボン", "リマ", 
        "リヤド", "リュブリャナ", "リロングウェ", "ルアンダ", "ルクセンブルク", "ルサカ", 
        "レイキャビク", "ローマ", "ロゾー", "ロメ", "ロンドン", "ワガドゥグー", "ワシントンディーシー", 
        "ワルシャワ", "ンジャメナ"
    ]
}

# --- ユーティリティ ---
def to_katakana(text):
    if not text: return ""
    return "".join([chr(ord(c) + 96) if 0x3041 <= ord(c) <= 0x3096 else c for c in text])

def get_clean_char(w, pos="head", offset=0):
    text = w.replace("ー", "")
    if not text: return ""
    try:
        idx = offset if pos == "head" else -(1 + offset)
        char = text[idx]
        return SMALL_TO_LARGE.get(char, char)
    except IndexError: return ""

def shift_kana(char, n):
    if char not in KANA_LIST: return char
    return KANA_LIST[(KANA_LIST.index(char) + n) % len(KANA_LIST)]

def get_variants(char, allow_daku, allow_handaku):
    variants = {char}
    if allow_daku:
        for k, v in DAKU_MAP.items():
            if char == k: variants.add(v)
            if char == v: variants.add(k)
    if allow_handaku:
        for k, v in HANDAKU_MAP.items():
            if char == k: variants.add(v)
            if char == v: variants.add(k)
    return variants

@app.route('/')
def index(): return render_template('index.html')

@app.route('/get_dictionary')
def get_dictionary(): return jsonify(DICTIONARY_MASTER)

@app.route('/search', methods=['POST'])
def search():
    d = request.json
    max_len = int(d.get('max_len', 5))
    pos_shift = int(d.get('pos_shift', 0))
    use_shift = d.get('use_shift', False)
    ks_val = int(d.get('ks_abs', 1))
    shift_mode = d.get('shift_mode', 'abs')
    allow_daku = d.get('allow_daku', False)
    allow_handaku = d.get('allow_handaku', False)
    unify_small = d.get('unify_small', False)
    choice_constraints = d.get('choice_constraints', [])
    exclusive_choice = d.get('exclusive_choice', False)
    auto_recovery = d.get('auto_recovery', False)
    patterns = d.get('patterns', [])
    char_limit_mode = d.get('char_limit_mode', False)

    # --- 辞書状態（赤・青）の取得 ---
    red_words = set(d.get('red_words', []))   # 使用不可
    blue_words = set(d.get('blue_words', [])) # 必須

    exclude_chars = to_katakana(d.get('exclude_chars', ""))
    ex_list = [c.strip() for c in re.split('[、,]', exclude_chars) if c.strip()]
    
    ban_start_chars = to_katakana(d.get('ban_start_chars', ""))
    bs_list = [c.strip() for c in re.split('[、,]', ban_start_chars) if c.strip()]
    
    group_constraints = d.get('group_constraints', [])
    raw_mc = to_katakana(d.get('must_char', ""))
    must_chars = [c for c in re.split('[、,]', raw_mc) if c]
    round_trip = d.get('round_trip', False)
    once_constraint = d.get('once_constraint', False)
    start_word = to_katakana(d.get('start_word', ""))
    start_char = to_katakana(d.get('start_char', ""))
    end_char = to_katakana(d.get('end_char', ""))
    
    selected_cats = d.get('categories', ["country"])
    temp_pool = []
    for cat in selected_cats:
        for w in DICTIONARY_MASTER.get(cat, []):
            # 赤（使用不可）のチェック
            if w in red_words: continue
            
            check_w = "".join([SMALL_TO_LARGE.get(c, c) for c in w]) if unify_small else w
            if any(ex in check_w for ex in ex_list): continue
            
            head_char = get_clean_char(w, "head")
            if any(head_char == bs for bs in bs_list): continue
            
            temp_pool.append(w)
    
    word_pool = list(set(temp_pool))
    head_index = defaultdict(list)
    for w in word_pool:
        head_index[get_clean_char(w, "head")].append(w)

    results = []
    start_time = time.time()

    def solve(path, current_total_len):
        if time.time() - start_time > 15 or len(results) >= 1500: return
        
        if patterns:
            current_idx = len(path)
            current_word = path[-1]
            pos_match = False
            has_pos_constraint = False
            free_patterns = []
            for p in patterns:
                m = re.match(r"^(\d+)(.+)$", p)
                if m:
                    p_num, p_body = m.groups()
                    if int(p_num) == current_idx:
                        has_pos_constraint = True
                        regex = "^" + re.escape(p_body).replace(r"\*", ".*") + "$"
                        if re.match(regex, current_word): pos_match = True
                elif p: free_patterns.append(p)
            if has_pos_constraint and not pos_match: return
            if free_patterns:
                if not any(re.match("^" + re.escape(p).replace(r"\*", ".*") + "$", current_word) for p in free_patterns): return

        full_current = "".join(path)
        if unify_small:
            full_current = "".join([SMALL_TO_LARGE.get(c, c) for c in full_current])

        if len(path) == max_len:
            # 青（必須単語）のチェック
            path_set = set(path)
            if not blue_words.issubset(path_set): return

            for group in group_constraints:
                if not any(target in path_set for target in group if target): return
            
            for choice_group in choice_constraints:
                target_count = 1
                group_shift = 0
                items_to_check = []
                for item in choice_group:
                    if ':' in item:
                        parts = item.split(':')
                        if parts[0].upper() == 'S': group_shift = int(parts[1])
                        elif parts[0].isdigit(): target_count = int(parts[0])
                        elif parts[1].isdigit(): target_count = int(parts[1])
                    else: items_to_check.append(item)

                total_found = 0
                for target in items_to_check:
                    shifted_target = "".join([shift_kana(c, group_shift) for c in target])
                    total_found += full_current.count(shifted_target)

                if exclusive_choice:
                    if total_found != target_count: return
                else:
                    if total_found < target_count: return

            if must_chars:
                if once_constraint:
                    if not all(full_current.count(mc) == 1 for mc in must_chars): return
                else:
                    if not all(mc in full_current for mc in must_chars): return
            
            if d.get('target_total_len') and current_total_len != int(d['target_total_len']): return
            
            last_tail = get_clean_char(path[-1], "tail")
            allowed_ends = get_variants(end_char, allow_daku, allow_handaku) if end_char else set()
            if end_char and last_tail not in allowed_ends: return
            
            results.append(list(path))
            return
        
        is_odd_conn = (len(path) % 2 != 0)
        max_offset = len(path[-1].replace("ー", ""))
        offsets_to_try = range(pos_shift, max_offset) if auto_recovery else [pos_shift]

        found_any = False
        for offset in offsets_to_try:
            src_char = get_clean_char(path[-1], "tail" if not round_trip or is_odd_conn else "head", offset)
            if not src_char: continue
            
            if use_shift and ks_val != 0:
                if shift_mode == 'abs':
                    base_targets = {shift_kana(src_char, abs(ks_val)), shift_kana(src_char, -abs(ks_val))}
                else:
                    base_targets = {shift_kana(src_char, ks_val)}
            else:
                base_targets = {src_char}
            
            all_targets = set()
            for bt in base_targets: all_targets.update(get_variants(bt, allow_daku, allow_handaku))
            
            for tc in all_targets:
                for nxt in head_index.get(tc, []):
                    if nxt not in path:
                        if char_limit_mode:
                            if not set("".join(path)).isdisjoint(set(nxt)): continue
                        found_any = True
                        solve(path + [nxt], current_total_len + len(nxt))
            if found_any: break

    starts = [start_word] if (start_word in word_pool) else word_pool
    for w in sorted(starts):
        if not start_word and start_char and get_clean_char(w, "head") != start_char: continue
        solve([w], len(w))
    return jsonify({"routes": results, "count": len(results)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
