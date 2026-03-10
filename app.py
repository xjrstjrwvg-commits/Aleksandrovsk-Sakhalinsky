<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>極・ULTRA ENGINE Pro</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        html, body { overflow-x: hidden; position: relative; width: 100%; touch-action: pan-y; }
        .glass { @apply bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-xl; }
        input, select, textarea { @apply bg-slate-100 dark:bg-slate-800 p-3 rounded-xl text-sm outline-none focus:ring-1 ring-blue-500 font-bold; }
        .step-btn { @apply bg-slate-200 dark:bg-slate-700 w-9 h-9 flex items-center justify-center rounded-lg font-black active:scale-90 transition-all text-[10px]; }
        .route-card { @apply bg-white dark:bg-slate-800 p-4 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 mb-2 flex justify-between items-center group; }
        .dict-btn { @apply border px-2 py-1 rounded-md text-[9px] font-bold transition-all; }
        .success-btn { @apply bg-emerald-500 text-white !important; }
        ::-webkit-scrollbar { display: none; }
        .no-scrollbar::-webkit-scrollbar { display: none; }
    </style>
</head>
<body class="bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 p-3 pb-24 font-sans">
    <div class="max-w-md mx-auto space-y-3">
        <header class="flex justify-between items-center py-1">
            <h1 class="text-xl font-black italic text-blue-600 uppercase tracking-tighter">Ultra Engine</h1>
            <div class="flex gap-2">
                <button onclick="copyTop()" class="bg-blue-100 dark:bg-blue-900/30 text-blue-600 px-3 py-2 rounded-full text-[9px] font-black uppercase transition-colors">Top Copy</button>
                <button onclick="copyAll()" id="allCopyBtn" class="bg-slate-200 dark:bg-slate-800 px-3 py-2 rounded-full text-[9px] font-black uppercase transition-colors">All Copy</button>
            </div>
        </header>

        <!-- 辞書コントロールパネル (タップで 必須/不可/可 を切り替え) -->
        <details class="glass rounded-[20px] overflow-hidden">
            <summary class="p-4 font-bold text-[10px] uppercase cursor-pointer bg-slate-100/50 dark:bg-slate-800 flex justify-between items-center">
                Dictionary Control
                <span id="dict_summary" class="text-blue-500 font-black tracking-widest">LOAD...</span>
            </summary>
            <div class="p-4 space-y-3">
                <div class="flex gap-2">
                    <button onclick="allDictStatus('ok')" class="flex-1 bg-slate-200 dark:bg-slate-700 py-2 rounded-lg text-[9px] font-black uppercase">ALL OK (全可)</button>
                    <button onclick="allDictStatus('ng')" class="flex-1 bg-slate-200 dark:bg-slate-700 py-2 rounded-lg text-[9px] font-black uppercase">ALL NG (全不可)</button>
                </div>
                <div id="dict_grid" class="flex flex-wrap gap-1 max-h-48 overflow-y-auto pr-1"></div>
            </div>
        </details>

        <!-- メインパネル -->
        <div class="glass rounded-[28px] p-5 space-y-4 shadow-2xl">
            <input id="sw" placeholder="開始単語" class="w-full">
            
            <div class="grid grid-cols-4 gap-2">
                <div class="space-y-1">
                    <label class="text-[8px] font-bold text-slate-400 uppercase ml-1">開始字</label>
                    <input id="sc" class="w-full">
                </div>
                <div class="space-y-1">
                    <label class="text-[8px] font-bold text-blue-500 uppercase ml-1">経由(→)</label>
                    <input id="via" placeholder="あ→い" class="w-full bg-blue-50 dark:bg-blue-900/20 ring-1 ring-blue-400/30">
                </div>
                <div class="space-y-1">
                    <label class="text-[8px] font-bold text-slate-400 uppercase ml-1">必須字</label>
                    <input id="mc" class="w-full">
                </div>
                <div class="space-y-1">
                    <label class="text-[8px] font-bold text-slate-400 uppercase ml-1">終了字</label>
                    <input id="ec" class="w-full">
                </div>
            </div>

            <div class="grid grid-cols-2 gap-2">
                <div class="space-y-1">
                    <label class="text-[8px] font-bold text-slate-400 uppercase ml-1">除外文字</label>
                    <input id="exc" placeholder="ン,ガ" class="w-full">
                </div>
                <div class="space-y-1">
                    <label class="text-[8px] font-bold text-slate-400 uppercase ml-1">パターン</label>
                    <input id="pattern" placeholder="*, ア*" class="w-full">
                </div>
            </div>

            <textarea id="gc" placeholder="グループ制約 (1行1組) 例:アメリカ,イギリス" class="w-full h-16 resize-none text-[10px]"></textarea>

            <!-- 数値設定セクション -->
            <div class="flex justify-between items-center border-t border-slate-100 dark:border-slate-800 pt-3">
                <div class="flex gap-2 items-center">
                    <input type="checkbox" id="use_shift" class="w-4 h-4 accent-blue-600">
                    <label class="text-[9px] font-bold uppercase text-slate-400">ずらし</label>
                    <button onclick="adjustVal('ks_abs',-1)" class="step-btn">-</button>
                    <input type="number" id="ks_abs" value="1" class="w-8 text-center bg-transparent text-xs font-bold">
                    <button onclick="adjustVal('ks_abs',1)" class="step-btn">+</button>
                </div>
                <div class="flex gap-1 items-center">
                    <input type="number" id="ml" value="3" class="w-9 text-center text-xs font-bold" title="単語数">
                    <input type="number" id="ttl" placeholder="物理" class="w-10 text-center text-xs font-bold" title="物理計">
                    <input type="number" id="ps" value="0" class="w-8 text-center text-xs font-bold" title="位置">
                    <input type="number" id="top_n" value="10" class="w-10 text-center text-xs font-bold border-l border-slate-300 dark:border-slate-700" title="上位N件">
                </div>
            </div>

            <!-- スイッチセクション -->
            <div class="grid grid-cols-2 gap-2 text-[9px] font-bold border-t border-slate-100 dark:border-slate-800 pt-3">
                <div class="space-y-1">
                    <label class="flex items-center gap-1 cursor-pointer"><input type="checkbox" id="allow_daku"> 濁点OK</label>
                    <label class="flex items-center gap-1 cursor-pointer"><input type="checkbox" id="allow_handaku"> 半濁点OK</label>
                    <label class="flex items-center gap-1 cursor-pointer text-emerald-600 font-black"><input type="checkbox" id="copy_with_len" checked> 文字数含めてコピー</label>
                </div>
                <div class="space-y-1">
                    <label class="flex items-center gap-1 cursor-pointer text-orange-500"><input type="checkbox" id="unify_small"> 小文字視</label>
                    <label class="flex items-center gap-1 cursor-pointer text-blue-500"><input type="checkbox" id="once_constraint"> 単一制約</label>
                    <label class="flex items-center gap-1 cursor-pointer"><input type="checkbox" id="rt"> 牛耕(往復)</label>
                    <label class="flex items-center gap-1 cursor-pointer"><input type="checkbox" id="use_multi_limit"> 個数指定モード</label>
                </div>
            </div>

            <div class="flex items-center justify-between pt-1">
                <div class="flex gap-3 text-[10px] font-black uppercase tracking-tighter">
                    <label class="flex items-center gap-1 cursor-pointer"><input type="checkbox" name="cat" value="country" checked> 国</label>
                    <label class="flex items-center gap-1 cursor-pointer"><input type="checkbox" name="cat" value="capital" checked> 首都</label>
                </div>
                <button onclick="run()" id="btn" class="bg-blue-600 text-white font-black px-10 py-4 rounded-2xl shadow-lg active:scale-95 transition-all text-sm uppercase tracking-widest">Start Engine</button>
            </div>
        </div>

        <!-- ソート・結果表示 -->
        <div class="flex gap-2 overflow-x-auto pb-1 no-scrollbar">
            <button onclick="sortRes('kana')" class="bg-slate-200 dark:bg-slate-800 px-3 py-2 rounded-lg text-[9px] font-black uppercase whitespace-nowrap">50音順</button>
            <button onclick="sortRes('short')" class="bg-slate-200 dark:bg-slate-800 px-3 py-2 rounded-lg text-[9px] font-black uppercase whitespace-nowrap">Shortest</button>
            <button onclick="sortRes('long')" class="bg-slate-200 dark:bg-slate-800 px-3 py-2 rounded-lg text-[9px] font-black uppercase whitespace-nowrap">Longest</button>
        </div>
        <div id="res" class="space-y-2"></div>
    </div>

    <script>
        let currentResults = [];
        let dictData = []; // {word, status} status: 0:OK, 1:FORCE, 2:BLOCK

        function adjustVal(id, step) {
            const el = document.getElementById(id);
            el.value = Math.max(0, parseInt(el.value) + step);
        }

        async function initDict() {
            try {
                const res = await fetch('/get_dictionary');
                const data = await res.json();
                const all = [...new Set([...data.country, ...data.capital])].sort();
                dictData = all.map(w => ({ word: w, status: 0 }));
                renderDict();
            } catch (e) { console.error("辞書読込失敗"); }
        }
        initDict();

        function renderDict() {
            const grid = document.getElementById('dict_grid');
            grid.innerHTML = dictData.map((d, i) => {
                let cls = "bg-white dark:bg-slate-800 text-slate-500 border-slate-200 dark:border-slate-700"; // 可
                if (d.status === 1) cls = "bg-blue-600 text-white border-blue-700 shadow-md"; // 必須
                if (d.status === 2) cls = "bg-red-500 text-white border-red-600 opacity-30"; // 不可
                return `<button onclick="toggleDict(${i})" class="dict-btn ${cls}">${d.word}</button>`;
            }).join('');
            document.getElementById('dict_summary').innerText = `${dictData.length} WORDS`;
        }

        function toggleDict(i) {
            dictData[i].status = (dictData[i].status + 1) % 3;
            renderDict();
        }

        function allDictStatus(mode) {
            dictData.forEach(d => d.status = (mode === 'ok' ? 0 : 2));
            renderDict();
        }

        async function run() {
            const btn = document.getElementById('btn');
            const resDiv = document.getElementById('res');
            btn.disabled = true; btn.innerText = "WAIT...";
            resDiv.innerHTML = '<div class="text-center py-10 animate-pulse text-blue-500 font-bold uppercase tracking-widest text-xs">Exploring...</div>';

            const cats = Array.from(document.querySelectorAll('input[name="cat"]:checked')).map(c => c.value);
            const data = {
                start_word: document.getElementById('sw').value,
                start_char: document.getElementById('sc').value,
                via_pattern: document.getElementById('via').value,
                must_char: document.getElementById('mc').value,
                end_char: document.getElementById('ec').value,
                exclude_chars: document.getElementById('exc').value,
                pattern: document.getElementById('pattern').value,
                group_constraints: document.getElementById('gc').value,
                max_len: document.getElementById('ml').value,
                target_total_len: document.getElementById('ttl').value ? parseInt(document.getElementById('ttl').value) : null,
                pos_shift: document.getElementById('ps').value,
                ks_abs: document.getElementById('ks_abs').value,
                use_shift: document.getElementById('use_shift').checked,
                use_multi_limit: document.getElementById('use_multi_limit').checked,
                allow_daku: document.getElementById('allow_daku').checked,
                allow_handaku: document.getElementById('allow_handaku').checked,
                unify_small: document.getElementById('unify_small').checked,
                once_constraint: document.getElementById('once_constraint').checked,
                round_trip: document.getElementById('rt').checked,
                blocked_words: dictData.filter(d => d.status === 2).map(d => d.word),
                force_words: dictData.filter(d => d.status === 1).map(d => d.word),
                categories: cats
            };

            try {
                const response = await fetch('/search', { 
                    method: 'POST', 
                    headers: {'Content-Type': 'application/json'}, 
                    body: JSON.stringify(data)
                });
                const result = await response.json();
                currentResults = result.routes;
                displayResults(currentResults);
            } catch (e) {
                resDiv.innerHTML = '<div class="text-center py-10 text-red-500 font-bold text-xs uppercase">Server Error</div>';
            } finally {
                btn.disabled = false; btn.innerText = "START ENGINE";
            }
        }

        function displayResults(routes) {
            const resDiv = document.getElementById('res');
            resDiv.innerHTML = routes.length ? "" : '<div class="text-center p-10 text-slate-400 font-bold uppercase text-xs tracking-widest">Not Found</div>';
            const withLen = document.getElementById('copy_with_len').checked;

            routes.forEach(route => {
                const txt = route.join(' → ');
                const len = route.join('').length;
                const copyStr = withLen ? `${txt} (${len})` : txt;
                const card = document.createElement('div');
                card.className = 'route-card';
                card.innerHTML = `<div><div class="text-[9px] text-blue-500 font-black">${len} CHARS</div><div class="font-bold text-sm leading-tight">${txt}</div></div>
                                  <button onclick="copyText('${copyStr}', this)" class="bg-blue-600 text-white text-[9px] px-3 py-2 rounded-lg font-black transition-all opacity-0 group-hover:opacity-100">COPY</button>`;
                resDiv.appendChild(card);
            });
        }

        function sortRes(mode) {
            if (mode === 'kana') currentResults.sort((a,b) => a.join('').localeCompare(b.join(''), 'ja'));
            if (mode === 'short') currentResults.sort((a,b) => a.join('').length - b.join('').length);
            if (mode === 'long') currentResults.sort((a,b) => b.join('').length - a.join('').length);
            displayResults(currentResults);
        }

        function getFormattedRoutes(routes) {
            const withLen = document.getElementById('copy_with_len').checked;
            return routes.map(r => withLen ? `${r.join(' → ')} (${r.join('').length})` : r.join(' → ')).join('\n');
        }

        function copyAll() {
            if (!currentResults.length) return;
            navigator.clipboard.writeText(getFormattedRoutes(currentResults));
            const b = document.getElementById('allCopyBtn');
            const original = b.innerText;
            b.innerText = "COPIED!"; b.classList.add('success-btn');
            setTimeout(() => { b.innerText = original; b.classList.remove('success-btn'); }, 1000);
        }

        function copyTop() {
            if (!currentResults.length) return;
            const n = parseInt(document.getElementById('top_n').value) || 10;
            navigator.clipboard.writeText(getFormattedRoutes(currentResults.slice(0, n)));
            alert(`TOP ${n} 件をコピーしました`);
        }

        function copyText(txt, btn) {
            navigator.clipboard.writeText(txt);
            const original = btn.innerText;
            btn.innerText = "DONE!"; btn.classList.add('success-btn');
            setTimeout(() => { btn.innerText = original; btn.classList.remove('success-btn'); }, 1000);
        }
    </script>
</body>
</html>
