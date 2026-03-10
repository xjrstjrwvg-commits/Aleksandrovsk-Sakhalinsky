import os, time, sys, re
from flask import Flask, render_template, request, jsonify
from collections import Counter, defaultdict

sys.setrecursionlimit(10000)
app = Flask(__name__)

KANA_LIST = "アイウエオカキクケコガギグゲゴサシスセソザジズゼゾタチツテトダヂヅデドナニヌネノハヒフヘホバビブベボパピプペポマミムメモヤユヨラリルレロワン"
SMALL_TO_LARGE = {"ァ": "ア", "ィ": "イ", "ゥ": "ウ", "ェ": "エ", "ォ": "オ", "ッ": "ツ", "ャ": "ヤ", "ュ": "ユ", "ョ": "ヨ", "ヮ": "ワ"}
DAKU_MAP = {"カ":"ガ", "キ":"ギ", "ク":"グ", "ケ":"ゲ", "コ":"ゴ", "サ":"ザ", "シ":"ジ", "ス":"ズ", "セ":"ゼ", "ソ":"ゾ", "タ":"ダ", "チ":"ヂ", "ツ":"ヅ", "テ":"デ", "ト":"ド", "ハ":"バ", "ヒ":"ビ", "フ":"ブ", "ヘ":"ベ", "ホ":"ボ"}
HANDAKU_MAP = {"ハ":"パ", "ヒ":"ピ", "フ":"プ", "ヘ":"ペ", "ホ":"ポ"}

# 辞書データ
DICTIONARY_MASTER = {
    "country": ["アイスランド", "アイルランド", "アゼルバイジャン", "アフガニスタン", "アメリカ", "アラブシュチョウコクレンポウ", "アルジェリア", "アルゼンチン", "アルバニア", "アルメニア", "アンゴラ", "アンティグアバーブーダ", "アンドラ", "イエメン", "イギリス", "イスラエル", "イタリア", "イラク", "イラン", "インド", "インドネシア", "ウガンダ", "ウクライナ", "ウズベキスタン", "ウルグアイ", "エクアドル", "エジプト", "エストニア", "エスワティニ", "エチオピア", "エリトリア", "エルサルバドル", "オーストラリア", "オーストリア", "オマーン", "オランダ", "ガーナ", "カーボベルデ", "ガイアナ", "カザフスタン", "カタール", "カナダ", "ガボン", "カメルーン", "ガンビア", "カンボジア", "キタマケドニア", "ギニア", "ギニアビサウ", "キプロス", "キューバ", "ギリシャ", "キリバス", "キルギス", "グアテマラ", "クウェート", "クックショトウ", "グレナダ", "クロアチア", "ケニア", "コートジボワール", "コスタリカ", "コソボ", "コモロ", "コロンビア", "コンゴキョウワコク", "コンゴミンシュキョウワコク", "サウジアラビア", "サモア", "サントメプリンシペ", "ザンビア", "サンマリノ", "シエラレオネ", "ジブチ", "ジャマイカ", "ジョージア", "シリア", "シンガポール", "ジンバブエ", "スイス", "スウェーデン", "スーダン", "スペイン", "スリナム", "スリランカ", "スロバキア", "スロベニア", "セーシェル", "セキドウギニア", "セネガル", "セルビア", "セントクリストファーネービス", "セントビンセントグレナディーンショトウ", "セントルシア", "ソマリア", "ソロモンショトウ", "タイ", "ダイカンミンコク", "タジキスタン", "タンザニア", "チェコ", "チャド", "チュウオウアフリカ", "チュウカジンミンキョウワコク", "チュニジア", "チョウセンミンシュシュギジンミンキョウワコク", "チリ", "ツバル", "デンマーク", "ドイツ", "トーゴ", "ドミニカキョウワコク", "ドミニカコク", "トリニダードトバゴ", "トルクメニスタン", "トルコ", "トンガ", "ナイジェリア", "ナウル", "ナミビア", "ニウエ", "ニカラグア", "ニジェール", "ニホン", "ニュージーランド", "ネパール", "ノルウェー", "バーレーン", "ハイチ", "パキスタン", "バチカンシコク", "パナマ", "バヌアツ", "バハマ", "パプアニューギニア", "パラオ", "パラグアイ", "バルバドス", "ハンガリー", "バングラデシュ", "ヒガシティモール", "フィジー", "フィリピン", "フィンランド", "ブータン", "ブラジル", "フランス", "ブルガリア", "ブルキナファソ", "ブルネイ", "ブルンジ", "ベトナム", "ベナン", "ベネズエラ", "ベラルーシ", "ベリーズ", "ペルー", "ベルギー", "ポーランド", "ボスニアヘルツェゴビナ", "ボツワナ", "ボリビア", "ポルトガル", "ホンジュラス", "マーシャルショトウ", "マダガスカル", "マラウイ", "マリ", "マルタ", "マレーシア", "ミクロネシアレンポウ", "ミナミアフリカキョウワコク", "ミナミスーダン", "ミャンマー", "メキシコ", "モーリシャス", "モーリタニア", "モザンビーク", "モナコ", "モルディブ", "モルドバ", "モロッコ", "モンゴル", "モンテネグロ", "ヨルダン", "ラオス", "ラトビア", "リトアニア", "リビア", "リヒテンシュタイン", "リベリア", "ルーマニア", "ルクセンブルク", "ルワンダ", "レソト", "レバノン", "ロシア"],
    "capital": ["アクラ", "アシガバット", "アスタナ", "アスマラ", "アスンシオン", "アディスアベバ", "アテネ", "アバルア", "アピア", "アブジャ", "アブダビ", "アムステルダム", "アルジェ", "アロフィ", "アンカラ", "アンタナナリボ", "アンドララベリャ", "アンマン", "イスラマバード", "ウィーン", "ウィントフック", "ウェリントン", "ウランバートル", "エルサレム", "エレバン", "オスロ", "オタワ", "カイロ", "カストリーズ", "カトマンズ", "カブール", "カラカス", "カンパラ", "キーウ", "キガリ", "キシナウ", "ギテガ", "キト", "キャンベラ", "キングスタウン", "キングストン", "キンシャサ", "グアテマラシティ", "クあラルンプール", "クウェート", "コナクリ", "コペンハーゲン", "ザグレブ", "サヌア", "サラエボ", "サンサルバドル", "サンティアゴ", "サントドミンゴ", "サントメ", "サンホセ", "サンマリノ", "ジブチ", "ジャカルタ", "ジュバ", "ジョージタウン", "シンガポール", "スコピエ", "ストックホルム", "スバ", "スリジャヤワルダナプラコッテ", "セントジョージズ", "セントジョンズ", "ソウル", "ソフィア", "ダカール", "タシケント", "ダッカ", "ダぶリン", "ダマスカス", "タラワ", "タリン", "チュニス", "ティラナ", "ディリ", "ティンプー", "テグシガルパ", "テヘラン", "デリー", "トウキョウ", "ドゥシャンベ", "ドーハ", "ドドマ", "トビリシ", "トリポリ", "ナイロビ", "ナッソー", "ニアメ", "ニコシア", "ヌアクショット", "ヌクアロファ", "ネピドー", "バクー", "バグダッド", "バセテール", "パナマシティ", "バチカン", "ハノイ", "ハバナ", "ハボローネ", "バマコ", "パラマリボ", "ハラレ", "パリ", "パリキール", "ハルツーム", "バレッタ", "バンギ", "バンコク", "バンジュール", "バンダルスリブガワン", "ビエンチャン", "ビクトリア", "ビサウ", "ビシュケク", "ピョンヤン", "ビリニュス", "ファドゥーツ", "ブエノスアイレス", "ブカレスト", "ブダペスト", "フナフティ", "プノンペン", "プライア", "ブラザビル", "ブラジリア", "ブラチスラバ", "プラハ", "フリータウン", "プリシュティナ", "ブリッジタウン", "ブリュッセル", "プレトリア", "ベイルート", "ベオグラード", "ペキン", "ヘルシンキ", "ベルモパン", "ベルリン", "ベルン", "ポートオブスペイン", "ポートビラ", "ポートモレスビー", "ポートルイス", "ボゴタ", "ポドゴリツァ", "ホニアラ", "ポルトープランス", "ポルトノボ", "マジュロ", "マスカット", "マセル", "マドリード", "マナーマ", "マナグア", "マニラ", "マプト", "マラボ", "マルキョク", "マレ", "ミンスク", "ムババーネ", "メキシコシティ", "モガディシュ", "モスクワ", "モナコ", "モロニ", "モンテビデオ", "モンロビア", "ヤウンデ", "ヤムスクロ", "ヤレン", "ラパス", "ラバト", "リーブルビル", "リガ", "リスボン", "リマ", "リヤド", "リュブリャナ", "リロングウェ", "ルアンダ", "ルクセンブルク", "ルサカ", "レイキャビク", "ローマ", "ロゾー", "ロメ", "ロンドン", "ワガドゥグー", "ワシントンディーシー", "ワルシャワ", "ンジャメナ"]
}

def to_katakana(text):
    if not text: return ""
    return "".join([chr(ord(c) + 96) if 0x3041 <= ord(c) <= 0x3096 else c for c in text])

def get_clean_char(w, pos="head", offset=0):
    text = w.replace("ー", "")
    if not text: return ""
    try:
        char = text[offset] if pos == "head" else text[-(1+offset)]
        return SMALL_TO_LARGE.get(char, char)
    except IndexError: return ""

def get_variants(char, allow_daku, allow_handaku):
    variants = {char}
    if allow_daku:
        for k, v in DAKU_MAP.items():
            if char == k: variants.add(v); break
            if char == v: variants.add(k); break
    if allow_handaku:
        for k, v in HANDAKU_MAP.items():
            if char == k: variants.add(v); break
            if char == v: variants.add(k); break
    return variants

@app.route('/')
def index(): return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    d = request.json
    max_len = int(d.get('max_len', 3))
    pos_shift = int(d.get('pos_shift', 0))
    use_shift = d.get('use_shift', False)
    ks_val = int(d.get('ks_abs', 1))
    allow_daku = d.get('allow_daku', False)
    allow_handaku = d.get('allow_handaku', False)
    unify_small = d.get('unify_small', False)
    once_constraint = d.get('once_constraint', False)
    
    # 経由設定解析
    raw_via = to_katakana(d.get('via_pattern', ""))
    via_steps = [p.strip() for p in raw_via.split('→')] if raw_via else []
    
    # 必須文字・除外文字
    raw_mc = to_katakana(d.get('must_char', ""))
    must_chars = [c for c in re.split('[、,]', raw_mc) if c]
    exclude_chars = to_katakana(d.get('exclude_chars', ""))
    ex_list = [c.strip() for c in re.split('[、,]', exclude_chars) if c.strip()]
    
    # グループ制約
    gc_text = to_katakana(d.get('group_constraints', ""))
    group_constraints = [re.split('[、,]', line) for line in gc_text.split('\n') if line.strip()]

    start_word = to_katakana(d.get('start_word', ""))
    start_char = to_katakana(d.get('start_char', ""))
    end_char = to_katakana(d.get('end_char', ""))
    selected_cats = d.get('categories', ["country"])
    
    word_pool = []
    for cat in selected_cats:
        for w in DICTIONARY_MASTER.get(cat, []):
            check_w = "".join([SMALL_TO_LARGE.get(c, c) for c in w]) if unify_small else w
            if any(ex in check_w for ex in ex_list): continue
            word_pool.append(w)
    word_pool = list(set(word_pool))

    head_index = defaultdict(list)
    for w in word_pool:
        head_index[get_clean_char(w, "head", pos_shift)].append(w)

    results = []
    start_time = time.time()

    def solve(path, current_total_len):
        if time.time() - start_time > 10 or len(results) >= 1000: return
        
        # ステップごとの経由文字チェック
        step_idx = len(path) - 1
        if via_steps and step_idx < len(via_steps):
            v_char = via_steps[step_idx]
            h = get_clean_char(path[-1], "head", pos_shift)
            t = get_clean_char(path[-1], "tail", pos_shift)
            v_vars = get_variants(v_char, allow_daku, allow_handaku)
            if h not in v_vars and t not in v_vars: return

        if len(path) == max_len:
            full_txt = "".join(path)
            # 必須文字・単一制約
            if once_constraint:
                if not all(full_txt.count(mc) == 1 for mc in must_chars): return
            elif not all(mc in full_txt for mc in must_chars): return
            
            # グループ制約
            if group_constraints:
                for group in group_constraints:
                    if not any(g in set(path) for g in group): return
            
            # 終了字判定
            last_tail = get_clean_char(path[-1], "tail", pos_shift)
            allowed_ends = get_variants(end_char, allow_daku, allow_handaku) if end_char else set()
            if end_char and last_tail not in allowed_ends: return
            
            results.append(list(path))
            return
        
        src_char = get_clean_char(path[-1], "tail", pos_shift)
        targets = {src_char}
        if use_shift:
            def shift_kana(c, n):
                if c not in KANA_LIST: return c
                return KANA_LIST[(KANA_LIST.index(c) + n) % len(KANA_LIST)]
            targets = {shift_kana(src_char, ks_val), shift_kana(src_char, -ks_val)}

        all_targets = set()
        for bt in targets: all_targets.update(get_variants(bt, allow_daku, allow_handaku))

        for tc in all_targets:
            for nxt in head_index.get(tc, []):
                if nxt not in path: solve(path + [nxt], current_total_len + len(nxt))

    starts = [start_word] if start_word in word_pool else word_pool
    for w in sorted(starts):
        if not start_word and start_char and get_clean_char(w, "head", pos_shift) != start_char: continue
        solve([w], len(w))

    return jsonify({"routes": results, "count": len(results)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
