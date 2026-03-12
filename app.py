import os, time, sys, re<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>極・ULTRA ENGINE Pro</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        html, body { overflow-x: hidden; position: relative; width: 100%; touch-action: pan-y; }
        .dark { color-scheme: dark; }
        .glass { @apply bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xl; }
        input, select, textarea { @apply bg-slate-100 dark:bg-slate-800 p-3 rounded-xl text-sm outline-none focus:ring-1 ring-blue-500 font-bold; }
        .step-btn { @apply bg-slate-200 dark:bg-slate-700 w-9 h-9 flex items-center justify-center rounded-lg font-black active:scale-90 transition-all text-sm; }
        ::-webkit-scrollbar { display: none; }
        .success-btn { @apply bg-emerald-500 text-white !important; }
    </style>
</head>
<body class="bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 p-3 pb-24" onchange="saveSettings()" oninput="saveSettings()">
    <div class="max-w-md mx-auto space-y-3">
        <header class="flex justify-between items-center py-1">
            <h1 class="text-xl font-black italic text-blue-600 uppercase tracking-tighter">Ultra Engine</h1>
            <button onclick="copyAll()" id="allCopyBtn" class="bg-slate-200 dark:bg-slate-800 px-4 py-2 rounded-full text-[10px] font-bold uppercase transition-colors">All Copy</button>
        </header>

        <!-- メインパネル -->
        <div class="glass rounded-[28px] p-5 space-y-4 shadow-2xl">
            <input id="sw" placeholder="開始単語" class="w-full">
            <div class="grid grid-cols-3 gap-2">
                <input id="sc" placeholder="開始字">
                <input id="mc" placeholder="必須(ア:2)">
                <input id="ec" placeholder="終了字">
            </div>

            <div class="grid grid-cols-2 gap-2">
                <div class="space-y-1">
                    <label class="text-[9px] font-bold text-slate-400 uppercase ml-1">使用不可文字</label>
                    <input id="exc" placeholder="ン,ガ" class="w-full">
                </div>
                <div class="space-y-1">
                    <label class="text-[9px] font-bold text-slate-400 uppercase ml-1">ルートパターン</label>
                    <input id="pattern" placeholder="1*, 2ア*, *ン" class="w-full">
                </div>
            </div>

            <div class="space-y-1 border-t border-slate-100 dark:border-slate-800 pt-3">
                <label class="text-[9px] font-bold text-slate-400 uppercase ml-1">グループ必須 (どれか1つ以上出現)</label>
                <textarea id="gc" placeholder="アメリカ,イギリス" class="w-full h-16 resize-none text-[11px]"></textarea>
            </div>

            <div class="space-y-2 border-t border-slate-100 dark:border-slate-800 pt-3">
                <label class="text-[9px] font-bold text-orange-400 uppercase ml-1">選択必須 (例: ン,ン:2)</label>
                <textarea id="cc" placeholder="ン,ン:2" class="w-full h-16 resize-none text-[11px]"></textarea>
                <div class="flex items-center gap-2 bg-orange-50 dark:bg-orange-900/20 p-2 rounded-xl border border-orange-100 dark:border-orange-900/30">
                    <input type="checkbox" id="exclusive_choice" class="w-4 h-4 cursor-pointer accent-orange-500">
                    <label for="exclusive_choice" class="text-[9px] font-bold text-orange-600 uppercase cursor-pointer">出現合計を「ちょうど」に限定</label>
                </div>
            </div>

            <div class="space-y-2 border-t border-slate-100 dark:border-slate-800 pt-3">
                <div class="flex justify-between items-center">
                    <label class="text-[9px] font-bold text-slate-400 uppercase tracking-widest">50音ずらし</label>
                    <input type="checkbox" id="use_shift" class="w-5 h-5 cursor-pointer accent-blue-600">
                </div>
                <div class="flex items-center gap-3 bg-slate-50 dark:bg-slate-800/30 p-2 rounded-xl">
                    <div class="flex gap-2 font-bold text-[10px]">
                        <label class="cursor-pointer flex items-center gap-1"><input type="radio" name="shift_mode" value="abs" checked class="w-3 h-3"> ±</label>
                        <label class="cursor-pointer flex items-center gap-1"><input type="radio" name="shift_mode" value="normal" class="w-3 h-3"> 通常</label>
                    </div>
                    <div class="flex items-center gap-2 ml-auto">
                        <button type="button" onclick="adjustVal('ks_abs',-1)" class="step-btn">-</button>
                        <input type="number" id="ks_abs" value="1" class="w-10 text-center bg-transparent border-none text-sm font-bold">
                        <button type="button" onclick="adjustVal('ks_abs',1)" class="step-btn">+</button>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-2 gap-3 text-[10px] font-bold border-t border-slate-100 dark:border-slate-800 pt-3">
                <div class="space-y-1">
                    <label class="flex items-center gap-1 cursor-pointer"><input type="checkbox" id="allow_daku" class="accent-blue-600"> 濁点変換OK</label>
                    <label class="flex items-center gap-1 cursor-pointer"><input type="checkbox" id="allow_handaku" class="accent-blue-600"> 半濁点OK</label>
                    <label class="flex items-center gap-1 cursor-pointer text-rose-600"><input type="checkbox" id="char_limit_mode" class="accent-rose-500"> 文字重複禁止</label>
                </div>
                <div class="space-y-1">
                    <label class="flex items-center gap-1 cursor-pointer text-indigo-600"><input type="checkbox" id="auto_recovery" class="accent-indigo-500"> 遡り接続</label>
                    <label class="flex items-center gap-1 cursor-pointer text-orange-600"><input type="checkbox" id="unify_small" class="accent-orange-500"> 小文字=大文字</label>
                </div>
            </div>

            <div class="grid grid-cols-2 gap-4 border-t border-slate-100 dark:border-slate-800 pt-3">
                <div class="space-y-1">
                    <label class="text-[9px] font-bold text-slate-400 uppercase tracking-widest">単語数</label>
                    <div class="flex items-center gap-2">
                        <button type="button" onclick="adjustVal('ml',-1)" class="step-btn">-</button>
                        <input type="number" id="ml" value="5" class="w-10 text-center bg-transparent border-none text-sm font-bold">
                        <button type="button" onclick="adjustVal('ml',1)" class="step-btn">+</button>
                    </div>
                </div>
                <div class="space-y-1 text-right">
                    <label class="text-[9px] font-bold text-slate-400 uppercase tracking-widest">物理 / 文字計</label>
                    <div class="flex justify-end gap-2">
                        <input type="number" id="ps" value="0" class="w-10 text-center text-sm font-bold">
                        <input type="number" id="ttl" placeholder="計" class="w-12 text-center text-sm font-bold">
                    </div>
                </div>
            </div>

            <div class="flex flex-wrap gap-3 text-[10px] font-bold border-t border-slate-100 dark:border-slate-800 pt-3">
                <label class="flex items-center gap-1 cursor-pointer"><input type="checkbox" id="conj" class="accent-blue-600"> 共役排除</label>
                <label class="flex items-center gap-1 cursor-pointer"><input type="checkbox" id="rt" class="accent-blue-600"> 牛耕</label>
                <label class="flex items-center gap-1 cursor-pointer"><input type="checkbox" id="once" class="accent-blue-600"> 単一制約</label>
                <label class="flex items-center gap-1 cursor-pointer text-emerald-600"><input type="checkbox" id="copy_with_len" checked> 文字数含コピー</label>
            </div>

            <div class="flex items-center justify-between pt-2">
                <div class="flex gap-3 text-[11px] font-bold">
                    <label class="cursor-pointer text-blue-500"><input type="checkbox" name="cat" value="country" checked> 国</label>
                    <label class="cursor-pointer text-blue-500"><input type="checkbox" name="cat" value="capital"> 首都</label>
                </div>
                <button type="button" onclick="run()" id="btn" class="bg-blue-600 text-white font-black px-8 py-3.5 rounded-2xl shadow-lg active:scale-95 transition-all uppercase tracking-widest">Explore</button>
            </div>
            
            <div class="flex items-center justify-between border-t border-slate-100 dark:border-slate-800 pt-3">
                <div class="flex items-center gap-2">
                    <label class="text-[9px] font-bold text-slate-400 uppercase italic">Top</label>
                    <input type="number" id="copy_limit" value="10" class="!w-12 !p-1 text-center bg-white dark:bg-slate-900 border-none text-blue-500 font-black rounded-lg">
                    <button type="button" onclick="copyTop()" id="topCopyBtn" class="bg-blue-600 text-white text-[9px] font-bold px-3 py-1.5 rounded-lg uppercase transition-colors">Copy Top</button>
                </div>
                <select id="sort_order" class="bg-transparent font-bold text-blue-500 text-[10px] w-auto outline-none" onchange="display(); saveSettings();">
                    <option value="len_asc">最短順</option>
                    <option value="len_desc">最長順</option>
                    <option value="kana">50音順</option>
                </select>
            </div>
            <div id="stats" class="text-center text-[10px] font-bold text-blue-500 hidden uppercase py-1"></div>
        </div>
        <div id="res" class="space-y-3 pb-20"></div>
    </div>

    <script>
        let currentRoutes = [];

        function to_katakana(text) {
            return text.replace(/[ぁ-ん]/g, s => String.fromCharCode(s.charCodeAt(0) + 0x60));
        }

        async function init() {
            if (localStorage.ultraSettings) {
                const s = JSON.parse(localStorage.ultraSettings);
                const fields = ['sw','sc','mc','ec','exc','pattern','gc','cc','ml','ps','ks_abs','ttl','copy_limit'];
                fields.forEach(f => { if(s[f] !== undefined && document.getElementById(f)) document.getElementById(f).value = s[f]; });
                if(s.sort_order) document.getElementById('sort_order').value = s.sort_order;
                document.getElementById('use_shift').checked = s.use_shift || false;
                const checks = ['conj','rt','once','copy_with_len','allow_daku','allow_handaku','unify_small','exclusive_choice','auto_recovery','char_limit_mode'];
                checks.forEach(f => { if(s[f] !== undefined && document.getElementById(f)) document.getElementById(f).checked = s[f]; });
                document.querySelectorAll('input[name="cat"]').forEach(c => c.checked = (s.cats || ["country"]).includes(c.value));
            }
        }

        function saveSettings() {
            const cats = Array.from(document.querySelectorAll('input[name="cat"]:checked')).map(c => c.value);
            localStorage.ultraSettings = JSON.stringify({
                sw: document.getElementById('sw').value, sc: document.getElementById('sc').value,
                mc: document.getElementById('mc').value, ec: document.getElementById('ec').value,
                exc: document.getElementById('exc').value, pattern: document.getElementById('pattern').value,
                gc: document.getElementById('gc').value, cc: document.getElementById('cc').value,
                ml: document.getElementById('ml').value, ps: document.getElementById('ps').value,
                ks_abs: document.getElementById('ks_abs').value, ttl: document.getElementById('ttl').value,
                copy_limit: document.getElementById('copy_limit').value, sort_order: document.getElementById('sort_order').value,
                use_shift: document.getElementById('use_shift').checked,
                conj: document.getElementById('conj').checked, rt: document.getElementById('rt').checked,
                once: document.getElementById('once').checked, copy_with_len: document.getElementById('copy_with_len').checked,
                allow_daku: document.getElementById('allow_daku').checked, allow_handaku: document.getElementById('allow_handaku').checked,
                unify_small: document.getElementById('unify_small').checked, exclusive_choice: document.getElementById('exclusive_choice').checked,
                auto_recovery: document.getElementById('auto_recovery').checked, char_limit_mode: document.getElementById('char_limit_mode').checked,
                cats: cats
            });
        }

        function adjustVal(id, delta) { const el = document.getElementById(id); el.value = Math.max(-50, parseInt(el.value) + delta); saveSettings(); }

        async function run() {
            const btn = document.getElementById('btn'); btn.innerText = "EXPLORING..."; btn.disabled = true;
            try {
                // ルートパターンのパース修正 (数値+パターンの形式に対応)
                const patterns = document.getElementById('pattern').value.split(',').map(p => {
                    const s = p.trim();
                    const m = s.match(/^(\d+)(.*)$/);
                    if(m) return m[1] + to_katakana(m[2]);
                    return to_katakana(s);
                }).filter(p => p);

                const cclines = document.getElementById('cc').value.split('\n').map(l => {
                    const items = l.split(/[、,]/).map(w => w.trim()).filter(w => w);
                    if (items.length === 0) return null;
                    const last = items[items.length - 1];
                    if (last.includes(':')) {
                        const parts = last.split(':');
                        items[items.length - 1] = to_katakana(parts[0]) + ':' + parts[1];
                        for(let i=0; i < items.length - 1; i++) items[i] = to_katakana(items[i]);
                    } else {
                        for(let i=0; i < items.length; i++) items[i] = to_katakana(items[i]);
                    }
                    return items;
                }).filter(g => g !== null);

                const r = await fetch('/search', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        start_word: document.getElementById('sw').value, start_char: document.getElementById('sc').value,
                        must_char: document.getElementById('mc').value, end_char: document.getElementById('ec').value,
                        exclude_chars: document.getElementById('exc').value, 
                        patterns: patterns,
                        group_constraints: document.getElementById('gc').value.split('\n').map(l => l.split(/[、,]/).map(w => to_katakana(w.trim())).filter(w => w)).filter(g => g.length > 0),
                        choice_constraints: cclines,
                        exclusive_choice: document.getElementById('exclusive_choice').checked,
                        auto_recovery: document.getElementById('auto_recovery').checked,
                        char_limit_mode: document.getElementById('char_limit_mode').checked,
                        max_len: document.getElementById('ml').value,
                        target_total_len: document.getElementById('ttl').value ? parseInt(document.getElementById('ttl').value) : null,
                        pos_shift: document.getElementById('ps').value, use_shift: document.getElementById('use_shift').checked,
                        ks_abs: document.getElementById('ks_abs').value,
                        allow_daku: document.getElementById('allow_daku').checked,
                        allow_handaku: document.getElementById('allow_handaku').checked,
                        unify_small: document.getElementById('unify_small').checked,
                        exclude_conjugates: document.getElementById('conj').checked,
                        round_trip: document.getElementById('rt').checked,
                        once_constraint: document.getElementById('once').checked,
                        categories: Array.from(document.querySelectorAll('input[name="cat"]:checked')).map(c => c.value),
                        blocked_words: [], force_words: []
                    })
                });
                const d = await r.json(); currentRoutes = d.routes || []; btn.innerText = "Explore"; btn.disabled = false;
                display();
            } catch(e) { console.error(e); alert("エラー"); btn.innerText = "Explore"; btn.disabled = false; }
        }

        function display() {
            const order = document.getElementById('sort_order').value;
            if (order === 'len_asc') currentRoutes.sort((a, b) => a.join('').length - b.join('').length || a.join('').localeCompare(b.join('')));
            else if (order === 'len_desc') currentRoutes.sort((a, b) => b.join('').length - a.join('').length || a.join('').localeCompare(b.join('')));
            else if (order === 'kana') currentRoutes.sort((a, b) => a.join('').localeCompare(b.join('')));

            document.getElementById('res').innerHTML = currentRoutes.map((rt, i) => `
                <div class="glass p-4 rounded-[20px] flex flex-col gap-2 relative animate-in fade-in slide-in-from-bottom-2">
                    <div class="flex justify-between items-center text-[10px] font-black uppercase text-slate-400"><span>Route #${i+1}</span><button type="button" onclick="copyOne(${i}, this)" class="text-blue-600 bg-blue-50 px-3 py-1 rounded-full font-bold">Copy</button></div>
                    <div class="font-bold text-[14px] leading-relaxed">${rt.join(' <span class="text-blue-500 opacity-40">→</span> ')}</div>
                    <div class="flex gap-2"><span class="bg-blue-100 text-blue-600 px-2 py-0.5 rounded font-black text-[9px] uppercase">${rt.join('').length} 文字</span></div>
                </div>`).join('');
            const stats = document.getElementById('stats');
            stats.innerText = `${currentRoutes.length} ROUTES FOUND`;
            stats.classList.remove('hidden');
        }

        function getRouteText(rt) {
            const includeLen = document.getElementById('copy_with_len').checked;
            const base = rt.join(' → ');
            return includeLen ? `${base} (${rt.join('').length}文字)` : base;
        }

        function showSuccess(btn, msg) {
            const original = btn.innerText; btn.innerText = msg; btn.classList.add('success-btn');
            setTimeout(() => { btn.innerText = original; btn.classList.remove('success-btn'); }, 1500);
        }

        async function execCopy(text, btn, successMsg) {
            if (!text) return;
            try {
                if (navigator.clipboard && window.isSecureContext) { await navigator.clipboard.writeText(text); }
                else {
                    const textArea = document.createElement("textarea"); textArea.value = text;
                    document.body.appendChild(textArea); textArea.select();
                    document.execCommand('copy'); document.body.removeChild(textArea);
                }
                showSuccess(btn, successMsg);
            } catch (err) { alert("コピー失敗"); }
        }

        function copyOne(i, btn) { execCopy(getRouteText(currentRoutes[i]), btn, "DONE!"); }
        function copyTop() {
            const limit = parseInt(document.getElementById('copy_limit').value) || 10;
            const targets = currentRoutes.slice(0, limit);
            if (!targets.length) return;
            execCopy(targets.map(rt => getRouteText(rt)).join('\n'), document.getElementById('topCopyBtn'), "COPIED!");
        }
        function copyAll() {
            if (!currentRoutes.length) return;
            execCopy(currentRoutes.map(rt => getRouteText(rt)).join('\n'), document.getElementById('allCopyBtn'), "ALL DONE!");
        }
        window.onload = init;
    </script>
</body>
</html>

from flask import Flask, render_template, request, jsonify
from collections import Counter, defaultdict

sys.setrecursionlimit(10000)
app = Flask(__name__)

KANA_LIST = (
    "アイウエオ" "カキクケコ" "ガギグゲゴ" "サシスセソ" "ザジズゼゾ"
    "タチツテト" "ダヂヅデド" "ナニヌネノ" "ハヒフヘホ" "バビブベボ"
    "パピプペポ" "マミムメモ" "ヤユヨ" "ラリルレロ" "ワン"
)
SMALL_TO_LARGE = {"ァ": "ア", "ィ": "イ", "ゥ": "ウ", "ェ": "エ", "ォ": "オ", "ッ": "ツ", "ャ": "ヤ", "ュ": "ユ", "ョ": "ヨ", "ヮ": "ワ"}

DAKU_MAP = {"カ":"ガ", "キ":"ギ", "ク":"グ", "ケ":"ゲ", "コ":"ゴ", "サ":"ザ", "シ":"ジ", "ス":"ズ", "セ":"ゼ", "ソ":"ゾ", "タ":"ダ", "チ":"ヂ", "ツ":"ヅ", "テ":"デ", "ト":"ド", "ハ":"バ", "ヒ":"ビ", "フ":"ブ", "ヘ":"ベ", "ホ":"ボ"}
HANDAKU_MAP = {"ハ":"パ", "ヒ":"ピ", "フ":"プ", "ヘ":"ペ", "ホ":"ポ"}

DICTIONARY_MASTER = {
    "country": ["アイスランド", "アイルランド", "アゼルバイジャン", "アフガニスタン", "アメリカ", "アラブシュチョウコクレンポウ", "アルジェリア", "アルゼンチン", "アルバニア", "アルメニア", "アンゴラ", "アンティグアバーブーダ", "アンドラ", "イエメン", "イギリス", "イスラエル", "イタリア", "イラク", "イラン", "インド", "インドネシア", "ウガンダ", "ウクライナ", "ウズベキスタン", "ウルグアイ", "エクアドル", "エジプト", "エストニア", "エスワティニ", "エチオピア", "エリトリア", "エルサルバドル", "オーストラリア", "オーストリア", "オマーン", "オランダ", "ガーナ", "カーボベルデ", "ガイアナ", "カザフスタン", "カタール", "カナダ", "ガボン", "カメルーン", "ガンビア", "カンボジア", "キタマケドニア", "ギニア", "ギニアビサウ", "キプロス", "キューバ", "ギリシャ", "キリバス", "キルギス", "グアテマラ", "クウェート", "クックショトウ", "グレナダ", "クロアチア", "ケニア", "コートジボワール", "コスタリカ", "コソボ", "コモロ", "コロンビア", "コンゴキョウワコク", "コンゴミンシュキョウワコク", "サウジアラビア", "サモア", "サントメプリンシペ", "ザンビア", "サンマリノ", "シエラレオネ", "ジブチ", "ジャマイカ", "ジョージア", "シリア", "シンガポール", "ジンバブエ", "スイス", "スウェーデン", "スーダン", "スペイン", "スリナム", "スリランカ", "スロバキア", "スロベニア", "セーシェル", "セキドウギニア", "セネガル", "セルビア", "セントクリストファーネービス", "セントビンセントグレナディーンショトウ", "セントルシア", "ソマリア", "ソロモンショトウ", "タイ", "ダイカンミンコク", "タジキスタン", "タンザニア", "チェコ", "チャド", "チュウオウアフリカ", "チュウカジンミンキョウワコク", "チュニジア", "チョウセンミンシュシュギジンミンキョウワコク", "チリ", "ツバル", "デンマーク", "ドイツ", "トーゴ", "ドミニカキョウワコク", "ドミニカコク", "トリニダードトバゴ", "トルクメニスタン", "トルコ", "トンガ", "ナイジェリア", "ナウル", "ナミビア", "ニウエ", "ニカラグア", "ニジェール", "ニホン", "ニュージーランド", "ネパール", "ノルウェー", "バーレーン", "ハイチ", "パキスタン", "バチカンシコク", "パナマ", "バヌアツ", "バハマ", "パプアニューギニア", "パラオ", "パラグアイ", "バルバドス", "ハンガリー", "バングラデシュ", "ヒガシティモール", "フィジー", "フィリピン", "フィンランド", "ブータン", "ブラジル", "フランス", "ブルガリア", "ブルキナファソ", "ブルネイ", "ブルンジ", "ベトナム", "ベナン", "ベネズエラ", "ベラルーシ", "ベリーズ", "ペルー", "ベルギー", "ポーランド", "ボスニアヘルツェゴビナ", "ボツワナ", "ボリビア", "ポルトガル", "ホンジュラス", "マーシャルショトウ", "マダガスカル", "マラウイ", "マリ", "マルタ", "マレーシア", "ミクロネシアレンポウ", "ミナミアフリカキョウワコク", "ミナミスーダン", "ミャンマー", "メキシコ", "モーリシャス", "モーリタニア", "モザンビーク", "モナコ", "モルディブ", "モルドバ", "モロッコ", "モンゴル", "モンテネグロ", "ヨルダン", "ラオス", "ラトビア", "リトアニア", "リビア", "リヒテンシュタイン", "リベリア", "ルーマニア", "ルクセンブルク", "ルワンダ", "レソト", "レバノン", "ロシア"],
    "capital": ["アクラ", "アシガバット", "アスタナ", "アスマラ", "アスンシオン", "アディスアベバ", "アテネ", "アバルア", "アピア", "アブジャ", "アブダビ", "アムステルダム", "アルジェ", "アロフィ", "アンカラ", "アンタナナリボ", "アンドララベリャ", "アンマン", "イスラマバード", "ウィーン", "ウィントフック", "ウェリントン", "ウランバートル", "エルサレム", "エレバン", "オスロ", "オタワ", "カイロ", "カストリーズ", "カトマンズ", "カブール", "カラカス", "カンパラ", "キーウ", "キガリ", "キシナウ", "ギテガ", "キト", "キャンベラ", "キングスタウン", "キングストン", "キンシャサ", "グアテマラシティ", "クアラルンプール", "クウェート", "コナクリ", "コペンハーゲン", "ザグレブ", "サヌア", "サラエボ", "サンサルバドル", "サンティアゴ", "サントドミンゴ", "サントメ", "サンホセ", "サンマリノ", "ジブチ", "ジャカルタ", "ジュバ", "ジョージタウン", "シンガポール", "スコピエ", "ストックホルム", "スバ", "スリジャヤワルダナプラコッテ", "セントジョージズ", "セントジョンズ", "ソウル", "ソフィア", "ダカール", "タシケント", "ダッカ", "ダブリン", "ダマスカス", "タラワ", "タリン", "チュニス", "ティラナ", "ディリ", "ティンプー", "テグシガルパ", "テヘラン", "デリー", "トウキョウ", "ドゥシャンベ", "ドーハ", "ドドマ", "トビリシ", "トリポリ", "ナイロビ", "ナッソー", "ニアメ", "ニコシア", "ヌアクショット", "ヌクアロファ", "ネピドー", "バクー", "バグダッド", "バセテール", "パナマシティ", "バチカン", "ハノイ", "ハバナ", "ハボローネ", "バマコ", "パラマリボ", "ハラレ", "パリ", "パリキール", "ハルツーム", "バレッタ", "バンギ", "バンコク", "バンジュール", "バンダルスリブガワン", "ビエンチャン", "ビクトリア", "ビサウ", "ビシュケク", "ピョンヤン", "ビリニュス", "ファドゥーツ", "ブエノスアイレス", "ブカレスト", "ブダペスト", "フナフティ", "プノンペン", "プライア", "ブラザビル", "ブラジリア", "ブラチスラバ", "プラハ", "フリータウン", "プリシュティナ", "ブリッジタウン", "ブリュッセル", "プレトリア", "ベイルート", "ベオグラード", "ペキン", "ヘルシンキ", "ベルモパン", "ベルリン", "ベルン", "ポートオブスペイン", "ポートビラ", "ポートモレスビー", "ポートルイス", "ボゴタ", "ポドゴリツァ", "ホニアラ", "ポルトープランス", "ポルトノボ", "マジュロ", "マスカット", "マセル", "マドリード", "マナーマ", "マナグア", "マニラ", "マプト", "マラボ", "マルキョク", "マレ", "ミンスク", "ムババーネ", "メキシコシティ", "モガディシュ", "モスクワ", "モナコ", "モロニ", "モンテビデオ", "モンロビア", "ヤウンデ", "ヤムスクロ", "ヤレン", "ラパス", "ラバト", "リーブルビル", "リガ", "リスボン", "リマ", "リヤド", "リュブリャナ", "リロングウェ", "ルアンダ", "ルクセンブルク", "ルサカ", "レイキャビク", "ローマ", "ロゾー", "ロメ", "ロンドン", "ワガドゥグー", "ワシントンディーシー", "ワルシャワ", "ンジャメナ"]
}

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
    
    allow_daku = d.get('allow_daku', False)
    allow_handaku = d.get('allow_handaku', False)
    unify_small = d.get('unify_small', False)
    
    choice_constraints = d.get('choice_constraints', [])
    exclusive_choice = d.get('exclusive_choice', False)
    auto_recovery = d.get('auto_recovery', False)
    patterns = d.get('patterns', [])
    char_limit_mode = d.get('char_limit_mode', False)

    raw_pattern = to_katakana(d.get('pattern', ""))
    exclude_chars = to_katakana(d.get('exclude_chars', ""))
    ex_list = [c.strip() for c in re.split('[、,]', exclude_chars) if c.strip()]
    group_constraints = d.get('group_constraints', [])

    raw_mc = to_katakana(d.get('must_char', ""))
    must_chars = [c for c in re.split('[、,]', raw_mc) if c]

    round_trip = d.get('round_trip', False)
    once_constraint = d.get('once_constraint', False)
    
    start_word = to_katakana(d.get('start_word', ""))
    start_char = to_katakana(d.get('start_char', ""))
    end_char = to_katakana(d.get('end_char', ""))
    blocked_words = set(d.get('blocked_words', []))
    force_words = set(d.get('force_words', []))
    selected_cats = d.get('categories', ["country"])
    
    temp_pool = []
    for cat in selected_cats:
        for w in DICTIONARY_MASTER.get(cat, []):
            if w in blocked_words: continue
            check_w = "".join([SMALL_TO_LARGE.get(c, c) for c in w]) if unify_small else w
            if any(ex in check_w for ex in ex_list): continue
            temp_pool.append(w)
    
    word_pool = list(set(temp_pool))
    head_index = defaultdict(list)
    for w in word_pool:
        head_index[get_clean_char(w, "head")].append(w)

    results = []
    start_time = time.time()

    def solve(path, current_total_len):
        if time.time() - start_time > 15 or len(results) >= 1500: return
        
        # --- ルートパターン判定 ---
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
                elif p:
                    free_patterns.append(p)

            if has_pos_constraint and not pos_match: return
            if free_patterns:
                f_match = False
                for p in free_patterns:
                    regex = "^" + re.escape(p).replace(r"\*", ".*") + "$"
                    if re.match(regex, current_word):
                        f_match = True
                        break
                if not f_match: return

        full_current = "".join(path)
        if unify_small:
            full_current = "".join([SMALL_TO_LARGE.get(c, c) for c in full_current])

        if len(path) == max_len:
            if not force_words.issubset(set(path)): return
            for group in group_constraints:
                if not any(target in set(path) for target in group if target): return
            
            # 選択式必須の判定
            for choice_group in choice_constraints:
                target_count = 1
                clean_group = []
                last_item = choice_group[-1]
                if ':' in last_item:
                    val_parts = last_item.split(':')
                    if val_parts[-1].isdigit():
                        target_count = int(val_parts[-1])
                        # 数値を除いた残りを抽出
                        base_val = val_parts[0]
                        clean_group = choice_group[:-1] + ([base_val] if base_val else [])
                    else: clean_group = choice_group
                else: clean_group = choice_group

                total_found = sum(full_current.count(target) for target in clean_group if target)
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

            base_targets = {shift_kana(src_char, abs(ks_val)), shift_kana(src_char, -abs(ks_val))} if use_shift and ks_val != 0 else {src_char}
            all_targets = set()
            for bt in base_targets:
                all_targets.update(get_variants(bt, allow_daku, allow_handaku))

            for tc in all_targets:
                for nxt in head_index.get(tc, []):
                    if nxt not in path:
                        # 文字重複禁止チェック
                        if char_limit_mode:
                            used_chars = set("".join(path))
                            next_word_chars = set(nxt)
                            if not used_chars.isdisjoint(next_word_chars):
                                continue
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
