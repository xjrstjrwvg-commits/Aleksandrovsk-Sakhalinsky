<!DOCTYPE html>
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
        .custom-scroll { max-height: 300px; overflow-y: auto; scrollbar-width: none; }
        .btn-white { background-color: white; color: #334155; border-color: #e2e8f0; }
        .dark .btn-white { background-color: #1e293b; color: #f1f5f9; border-color: #334155; }
    </style>
</head>
<body class="bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 p-3 pb-24" onchange="saveSettings()" oninput="saveSettings()">
    <div class="max-w-md mx-auto space-y-3">
        <header class="flex justify-between items-center py-1">
            <div class="flex items-center gap-3">
                <h1 class="text-xl font-black italic text-blue-600 uppercase tracking-tighter">Ultra Engine</h1>
                <button onclick="toggleDarkMode()" class="text-xl p-1 hover:scale-110 transition-transform">🌗</button>
            </div>
            <div class="flex gap-2">
                <button onclick="resetSettings()" class="bg-rose-100 dark:bg-rose-900/30 text-rose-600 px-4 py-2 rounded-full text-[10px] font-bold uppercase">Reset</button>
                <button onclick="copyAll()" id="allCopyBtn" class="bg-slate-200 dark:bg-slate-800 px-4 py-2 rounded-full text-[10px] font-bold uppercase">All Copy</button>
            </div>
        </header>

        <div class="glass rounded-[28px] p-5 space-y-4 shadow-2xl">
            <input id="sw" placeholder="開始単語" class="w-full">
            
            <div class="grid grid-cols-3 gap-2">
                <input id="sc" placeholder="開始字" class="w-full">
                <input id="mc" placeholder="必須文字" class="w-full">
                <input id="ec" placeholder="終了字" class="w-full">
            </div>

            <!-- 全語縛り -->
            <div class="grid grid-cols-2 gap-2 border-t border-slate-100 dark:border-slate-800 pt-3">
                <div class="space-y-1">
                    <label class="text-[9px] font-bold text-blue-500 uppercase ml-1">全語開始字</label>
                    <input id="asc" placeholder="ア,カ" class="w-full">
                </div>
                <div class="space-y-1">
                    <label class="text-[9px] font-bold text-blue-500 uppercase ml-1">全語終了字</label>
                    <input id="aec" placeholder="ン,イ" class="w-full">
                </div>
            </div>

            <!-- 制約テキストエリア -->
            <div class="grid grid-cols-2 gap-3 border-t border-slate-100 dark:border-slate-800 pt-3">
                <div class="space-y-1">
                    <label class="text-[9px] font-bold text-slate-400 uppercase ml-1 tracking-widest">グループ必須</label>
                    <textarea id="gc" placeholder="1行1組" class="w-full h-16 resize-none text-[10px]"></textarea>
                </div>
                <div class="space-y-1 text-orange-600">
                    <label class="text-[9px] font-bold uppercase ml-1 tracking-widest">選択必須</label>
                    <textarea id="cc" placeholder="ン,ン:2" class="w-full h-16 resize-none text-[10px]"></textarea>
                </div>
            </div>
            <div class="flex items-center gap-2 bg-orange-50 dark:bg-orange-900/20 p-2 rounded-xl border border-orange-100 dark:border-orange-900/30">
                <input type="checkbox" id="exclusive_choice" class="w-4 h-4 cursor-pointer accent-orange-500">
                <label for="exclusive_choice" class="text-[9px] font-bold text-orange-600 uppercase cursor-pointer">出現合計を「ちょうど」に限定</label>
            </div>

            <div class="grid grid-cols-2 gap-2 border-t border-slate-100 dark:border-slate-800 pt-3">
                <div class="space-y-1">
                    <label class="text-[9px] font-bold text-slate-400 uppercase ml-1">使用不可文字</label>
                    <input id="exc" placeholder="ン,ガ" class="w-full">
                </div>
                <div class="space-y-1">
                    <label class="text-[9px] font-bold text-rose-400 uppercase ml-1">禁止開始文字</label>
                    <input id="bsc" placeholder="ガ,ザ" class="w-full">
                </div>
            </div>

            <!-- 50音ずらし -->
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

            <!-- 辞書管理 -->
            <div class="border-t border-slate-100 dark:border-slate-800 pt-3 space-y-2">
                <button type="button" onclick="document.getElementById('dict-manager').classList.toggle('hidden')" class="w-full py-2 bg-slate-100 dark:bg-slate-800 rounded-xl text-[10px] font-black uppercase tracking-widest text-slate-500 flex justify-between px-4 items-center">
                    Dictionary Table <span id="dict-status" class="text-blue-500">OFF</span>
                </button>
                <div id="dict-manager" class="hidden space-y-3 p-2 bg-slate-50 dark:bg-slate-900/50 rounded-2xl border border-slate-100 dark:border-slate-800">
                    <div class="flex gap-2">
                        <button type="button" onclick="bulkSet('white')" class="flex-1 py-2 bg-white dark:bg-slate-700 rounded-lg text-[9px] font-bold shadow-sm">全開放</button>
                        <button type="button" onclick="bulkSet('red')" class="flex-1 py-2 bg-rose-100 dark:bg-rose-900/30 text-rose-600 rounded-lg text-[9px] font-bold shadow-sm">全禁止</button>
                    </div>
                    <div id="dict-list" class="grid grid-cols-2 gap-1 custom-scroll p-1"></div>
                </div>
            </div>

            <!-- 探索設定 -->
            <div class="grid grid-cols-2 gap-4 border-t border-slate-100 dark:border-slate-800 pt-3">
                <div class="space-y-1">
                    <label class="text-[9px] font-bold text-rose-500 uppercase tracking-widest">Timeout (秒)</label>
                    <div class="flex items-center gap-2">
                        <button type="button" onclick="adjustVal('timeout',-5)" class="step-btn">-</button>
                        <input type="number" id="timeout" value="15" class="w-10 text-center bg-transparent border-none text-sm font-bold">
                        <button type="button" onclick="adjustVal('timeout',5)" class="step-btn">+</button>
                    </div>
                </div>
                <div class="space-y-1 text-right">
                    <div class="flex justify-end items-center gap-1">
                        <input type="checkbox" id="limit_enabled" checked class="w-3 h-3 accent-emerald-500">
                        <label for="limit_enabled" class="text-[9px] font-bold text-emerald-500 uppercase tracking-widest leading-none">Max 表示数</label>
                    </div>
                    <input type="number" id="limit" value="1500" class="w-20 text-center text-sm font-bold mt-1">
                </div>
            </div>

            <!-- オプション -->
            <div class="grid grid-cols-2 gap-x-4 gap-y-2 text-[10px] font-bold border-t border-slate-100 dark:border-slate-800 pt-3">
                <label class="flex items-center gap-1 cursor-pointer"><input type="checkbox" id="allow_daku"> 濁点OK</label>
                <label class="flex items-center gap-1 cursor-pointer"><input type="checkbox" id="allow_handaku"> 半濁点OK</label>
                <label class="flex items-center gap-1 cursor-pointer text-indigo-600"><input type="checkbox" id="auto_recovery"> 遡り接続</label>
                <label class="flex items-center gap-1 cursor-pointer text-orange-600"><input type="checkbox" id="unify_small"> 大文字=小文字</label>
                <label class="flex items-center gap-1 cursor-pointer text-blue-600"><input type="checkbox" id="rt"> 牛耕</label>
                <label class="flex items-center gap-1 cursor-pointer text-blue-600"><input type="checkbox" id="once"> 単一制約</label>
                <label class="flex items-center gap-1 cursor-pointer text-rose-600"><input type="checkbox" id="char_limit_mode"> 重複禁止</label>
                <label class="flex items-center gap-1 cursor-pointer text-emerald-600"><input type="checkbox" id="copy_with_len" checked> 文字数含コピー</label>
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

            <div class="flex items-center justify-between pt-2">
                <div class="flex gap-3 text-[11px] font-bold">
                    <label class="cursor-pointer text-blue-500"><input type="checkbox" name="cat" value="country" checked onchange="loadDictionaryUI()"> 国</label>
                    <label class="cursor-pointer text-blue-500"><input type="checkbox" name="cat" value="capital" onchange="loadDictionaryUI()"> 首都</label>
                </div>
                <button type="button" onclick="run()" id="btn" class="bg-blue-600 text-white font-black px-8 py-3.5 rounded-2xl shadow-lg active:scale-95 transition-all uppercase tracking-widest">Explore</button>
            </div>
            
            <div id="stats" class="text-center text-[10px] font-bold text-blue-500 hidden uppercase py-1"></div>
        </div>
        <div id="res" class="space-y-3 pb-20"></div>
    </div>

    <script>
        let currentRoutes = [];
        let wordStates = {};

        function to_katakana(text) { return text.replace(/[ぁ-ん]/g, s => String.fromCharCode(s.charCodeAt(0) + 0x60)); }
        function toggleDarkMode() { document.documentElement.classList.toggle('dark'); loadDictionaryUI(); saveSettings(); }
        function getWordStyle(state) {
            if (state === 'red') return "background-color: #f43f5e; color: white; border-color: #e11d48;";
            if (state === 'blue') return "background-color: #2563eb; color: white; border-color: #1d4ed8;";
            return ""; 
        }

        function resetSettings() {
            if(!confirm("設定をすべて初期化しますか？")) return;
            localStorage.removeItem('ultraSettings');
            location.reload();
        }

        async function init() {
            if (localStorage.ultraSettings) {
                const s = JSON.parse(localStorage.ultraSettings);
                const fields = ['sw','sc','asc','mc','ec','aec','exc','bsc','pattern','ml','ps','ks_abs','ttl','timeout','limit','gc','cc'];
                fields.forEach(f => { if(s[f] !== undefined && document.getElementById(f)) document.getElementById(f).value = s[f]; });
                const checks = ['allow_daku','allow_handaku','char_limit_mode','auto_recovery','limit_enabled','unify_small','rt','once','copy_with_len','use_shift','exclusive_choice'];
                checks.forEach(f => { if(s[f] !== undefined && document.getElementById(f)) document.getElementById(f).checked = s[f]; });
                if (s.dark_mode) document.documentElement.classList.add('dark');
                if (s.wordStates) wordStates = s.wordStates;
                document.querySelectorAll('input[name="cat"]').forEach(c => c.checked = (s.cats || ["country"]).includes(c.value));
            }
            await loadDictionaryUI();
        }

        async function loadDictionaryUI() {
            const r = await fetch('/get_dictionary');
            const dict = await r.json();
            const cats = Array.from(document.querySelectorAll('input[name="cat"]:checked')).map(c => c.value);
            let allWords = [];
            cats.forEach(c => allWords = allWords.concat(dict[c] || []));
            allWords = Array.from(new Set(allWords)).sort();
            const list = document.getElementById('dict-list');
            list.innerHTML = allWords.map(w => {
                const state = wordStates[w] || 'white';
                const style = getWordStyle(state);
                const baseClass = state === 'white' ? 'btn-white' : '';
                return `<button type="button" onclick="toggleWordState(this, '${w}')" class="word-btn text-[10px] font-bold p-2 rounded-lg border transition-all ${baseClass}" style="${style}">${w}</button>`;
            }).join('');
            updateDictStatus();
        }

        function toggleWordState(btn, word) {
            const cycle = { 'white': 'red', 'red': 'blue', 'blue': 'white' };
            const newState = cycle[wordStates[word] || 'white'];
            wordStates[word] = newState;
            if (newState === 'white') { btn.classList.add('btn-white'); btn.style = ""; }
            else { btn.classList.remove('btn-white'); btn.style = getWordStyle(newState); }
            updateDictStatus(); saveSettings();
        }

        function bulkSet(state) {
            document.querySelectorAll('.word-btn').forEach(btn => {
                wordStates[btn.innerText] = state;
                if (state === 'white') { btn.classList.add('btn-white'); btn.style = ""; }
                else { btn.classList.remove('btn-white'); btn.style = getWordStyle(state); }
            });
            updateDictStatus(); saveSettings();
        }

        function updateDictStatus() {
            const redCount = Object.values(wordStates).filter(v => v === 'red').length;
            const blueCount = Object.values(wordStates).filter(v => v === 'blue').length;
            document.getElementById('dict-status').innerText = (redCount || blueCount) ? `R:${redCount} B:${blueCount}` : "OFF";
        }

        function saveSettings() {
            const cats = Array.from(document.querySelectorAll('input[name="cat"]:checked')).map(c => c.value);
            localStorage.ultraSettings = JSON.stringify({
                sw: document.getElementById('sw').value, sc: document.getElementById('sc').value, asc: document.getElementById('asc').value,
                mc: document.getElementById('mc').value, ec: document.getElementById('ec').value, aec: document.getElementById('aec').value,
                exc: document.getElementById('exc').value, bsc: document.getElementById('bsc').value, pattern: document.getElementById('pattern').value,
                ml: document.getElementById('ml').value, timeout: document.getElementById('timeout').value, limit: document.getElementById('limit').value,
                gc: document.getElementById('gc').value, cc: document.getElementById('cc').value,
                ps: document.getElementById('ps').value, ks_abs: document.getElementById('ks_abs').value, ttl: document.getElementById('ttl').value,
                limit_enabled: document.getElementById('limit_enabled').checked, use_shift: document.getElementById('use_shift').checked,
                unify_small: document.getElementById('unify_small').checked, rt: document.getElementById('rt').checked,
                once: document.getElementById('once').checked, copy_with_len: document.getElementById('copy_with_len').checked,
                exclusive_choice: document.getElementById('exclusive_choice').checked, dark_mode: document.documentElement.classList.contains('dark'),
                allow_daku: document.getElementById('allow_daku').checked, allow_handaku: document.getElementById('allow_handaku').checked,
                char_limit_mode: document.getElementById('char_limit_mode').checked, auto_recovery: document.getElementById('auto_recovery').checked,
                wordStates: wordStates, cats: cats
            });
        }

        function adjustVal(id, delta) { const el = document.getElementById(id); el.value = Math.max(1, parseInt(el.value) + delta); saveSettings(); }

        async function run() {
            const btn = document.getElementById('btn'); btn.innerText = "EXPLORING..."; btn.disabled = true;
            try {
                const cclines = document.getElementById('cc').value.split('\n').map(l => {
                    const items = l.split(/[、,]/).map(w => w.trim()).filter(w => w);
                    return items.length ? items.map(item => item.includes(':') ? to_katakana(item.split(':')[0]) + ':' + item.split(':')[1] : to_katakana(item)) : null;
                }).filter(g => g);

                const r = await fetch('/search', {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        start_word: document.getElementById('sw').value, start_char: document.getElementById('sc').value,
                        all_start_char: document.getElementById('asc').value, must_char: document.getElementById('mc').value,
                        end_char: document.getElementById('ec').value, all_end_char: document.getElementById('aec').value,
                        exclude_chars: document.getElementById('exc').value, ban_start_chars: document.getElementById('bsc').value,
                        max_len: document.getElementById('ml').value, timeout: document.getElementById('timeout').value, 
                        limit: document.getElementById('limit').value, limit_enabled: document.getElementById('limit_enabled').checked,
                        pos_shift: parseInt(document.getElementById('ps').value), use_shift: document.getElementById('use_shift').checked,
                        ks_abs: parseInt(document.getElementById('ks_abs').value), shift_mode: document.querySelector('input[name="shift_mode"]:checked').value,
                        allow_daku: document.getElementById('allow_daku').checked, allow_handaku: document.getElementById('allow_handaku').checked,
                        auto_recovery: document.getElementById('auto_recovery').checked, char_limit_mode: document.getElementById('char_limit_mode').checked,
                        unify_small: document.getElementById('unify_small').checked, round_trip: document.getElementById('rt').checked,
                        once_constraint: document.getElementById('once').checked, exclusive_choice: document.getElementById('exclusive_choice').checked,
                        group_constraints: document.getElementById('gc').value.split('\n').map(l => l.split(/[、,]/).map(w => to_katakana(w.trim())).filter(w => w)).filter(g => g.length),
                        choice_constraints: cclines, categories: Array.from(document.querySelectorAll('input[name="cat"]:checked')).map(c => c.value),
                        red_words: Object.keys(wordStates).filter(k => wordStates[k] === 'red'), blue_words: Object.keys(wordStates).filter(k => wordStates[k] === 'blue')
                    })
                });
                const d = await r.json(); currentRoutes = d.routes || []; btn.innerText = "Explore"; btn.disabled = false; display();
            } catch(e) { btn.innerText = "Explore"; btn.disabled = false; }
        }

        function display() {
            document.getElementById('res').innerHTML = currentRoutes.map((rt, i) => `
                <div class="glass p-4 rounded-[20px] flex flex-col gap-2 relative">
                    <div class="flex justify-between items-center text-[10px] font-black uppercase text-slate-400"><span>Route #${i+1}</span><button type="button" onclick="copyOne(${i}, this)" class="text-blue-600 bg-blue-50 px-3 py-1 rounded-full font-bold">Copy</button></div>
                    <div class="font-bold text-[14px] leading-relaxed">${rt.join(' <span class="text-blue-500 opacity-40">→</span> ')}</div>
                    <div class="flex gap-2"><span class="bg-blue-100 text-blue-600 px-2 py-0.5 rounded font-black text-[9px] uppercase">${rt.join('').length} 文字</span></div>
                </div>`).join('');
            const stats = document.getElementById('stats'); stats.innerText = `${currentRoutes.length} ROUTES FOUND`; stats.classList.remove('hidden');
        }
        function copyOne(i, btn) { 
            const rt = currentRoutes[i];
            const base = rt.join(' → ');
            const text = document.getElementById('copy_with_len').checked ? `${base} (${rt.join('').length}文字)` : base;
            navigator.clipboard.writeText(text); 
        }
        function copyAll() { 
            const text = currentRoutes.map(rt => {
                const base = rt.join(' → ');
                return document.getElementById('copy_with_len').checked ? `${base} (${rt.join('').length}文字)` : base;
            }).join('\n');
            navigator.clipboard.writeText(text); 
        }
        window.onload = init;
    </script>
</body>
</html>
