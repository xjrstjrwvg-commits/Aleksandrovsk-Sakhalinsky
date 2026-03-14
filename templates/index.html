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
        .btn-white { background-color: white; color: #334155; border-color: #e2e8f0; }
        .dark .btn-white { background-color: #1e293b; color: #f1f5f9; border-color: #334155; }
    </style>
</head>
<body class="bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 p-3 pb-24" onchange="saveSettings()" oninput="saveSettings()">
    <div class="max-w-md mx-auto space-y-3">
        <header class="flex justify-between items-center py-1">
            <h1 class="text-xl font-black italic text-blue-600 uppercase tracking-tighter">Ultra Engine</h1>
            <div class="flex gap-2">
                <button onclick="resetSettings()" class="bg-rose-100 dark:bg-rose-900/30 text-rose-600 px-4 py-2 rounded-full text-[10px] font-bold uppercase">Reset</button>
                <button onclick="copyAll()" id="allCopyBtn" class="bg-slate-200 dark:bg-slate-800 px-4 py-2 rounded-full text-[10px] font-bold uppercase">All Copy</button>
            </div>
        </header>

        <div class="glass rounded-[28px] p-5 space-y-4">
            <input id="sw" placeholder="開始単語" class="w-full">
            <div class="grid grid-cols-2 gap-2">
                <div class="space-y-1"><label class="text-[9px] font-bold text-blue-500 uppercase">全語開始字</label><input id="asc" placeholder="ア,カ" class="w-full"></div>
                <div class="space-y-1"><label class="text-[9px] font-bold text-blue-500 uppercase">全語終了字</label><input id="aec" placeholder="ン,イ" class="w-full"></div>
            </div>

            <div class="grid grid-cols-2 gap-x-4 gap-y-2 text-[10px] font-bold border-t border-slate-100 dark:border-slate-800 pt-3">
                <label class="flex items-center gap-1 cursor-pointer"><input type="checkbox" id="allow_daku"> 濁点OK</label>
                <label class="flex items-center gap-1 cursor-pointer"><input type="checkbox" id="allow_handaku"> 半濁点OK</label>
                <label class="flex items-center gap-1 cursor-pointer text-indigo-600"><input type="checkbox" id="auto_recovery"> 遡り接続</label>
                <label class="flex items-center gap-1 cursor-pointer text-orange-600"><input type="checkbox" id="unify_small"> 大文字=小文字</label>
                <label class="flex items-center gap-1 cursor-pointer text-blue-600"><input type="checkbox" id="rt"> 牛耕</label>
                <label class="flex items-center gap-1 cursor-pointer text-blue-600"><input type="checkbox" id="conj"> 共役排除</label>
                <label class="flex items-center gap-1 cursor-pointer text-blue-600"><input type="checkbox" id="use_shift"> 50音ずらし</label>
            </div>

            <!-- 辞書パネル -->
            <div class="border-t border-slate-100 dark:border-slate-800 pt-3">
                <button type="button" onclick="document.getElementById('dict-manager').classList.toggle('hidden')" class="w-full py-2 bg-slate-100 dark:bg-slate-800 rounded-xl text-[10px] font-black uppercase text-slate-500">Dictionary Table</button>
                <div id="dict-manager" class="hidden mt-2 max-h-48 overflow-y-auto grid grid-cols-2 gap-1" id="dict-list"></div>
            </div>

            <div class="grid grid-cols-2 gap-4 border-t border-slate-100 dark:border-slate-800 pt-3">
                <div class="space-y-1"><label class="text-[9px] font-bold text-rose-500 uppercase">Timeout</label><input type="number" id="timeout" value="15" class="w-full"></div>
                <div class="space-y-1"><label class="text-[9px] font-bold text-emerald-500 uppercase">Max表示</label><input type="number" id="limit" value="1500" class="w-full"></div>
            </div>

            <div class="flex items-center justify-between pt-2">
                <div class="flex gap-3 text-[11px] font-bold">
                    <label><input type="checkbox" name="cat" value="country" checked> 国</label>
                    <label><input type="checkbox" name="cat" value="capital"> 首都</label>
                </div>
                <button onclick="run()" id="btn" class="bg-blue-600 text-white font-black px-8 py-3 rounded-2xl">Explore</button>
            </div>
        </div>
        <div id="res" class="space-y-3 pb-20"></div>
    </div>

    <script>
        let currentRoutes = [];
        let wordStates = {};

        function saveSettings() {
            const settings = {
                sw: document.getElementById('sw').value,
                asc: document.getElementById('asc').value,
                aec: document.getElementById('aec').value,
                timeout: document.getElementById('timeout').value,
                limit: document.getElementById('limit').value,
                rt: document.getElementById('rt').checked,
                conj: document.getElementById('conj').checked,
                use_shift: document.getElementById('use_shift').checked,
                allow_daku: document.getElementById('allow_daku').checked,
                allow_handaku: document.getElementById('allow_handaku').checked,
                auto_recovery: document.getElementById('auto_recovery').checked,
                unify_small: document.getElementById('unify_small').checked,
                wordStates: wordStates
            };
            localStorage.setItem('ultraSettings', JSON.stringify(settings));
        }

        function loadSettings() {
            const s = JSON.parse(localStorage.getItem('ultraSettings') || '{}');
            if (s.sw) {
                document.getElementById('sw').value = s.sw;
                document.getElementById('asc').value = s.asc;
                document.getElementById('aec').value = s.aec;
                document.getElementById('timeout').value = s.timeout;
                document.getElementById('limit').value = s.limit;
                document.getElementById('rt').checked = s.rt;
                document.getElementById('conj').checked = s.conj;
                document.getElementById('use_shift').checked = s.use_shift;
                document.getElementById('allow_daku').checked = s.allow_daku;
                document.getElementById('allow_handaku').checked = s.allow_handaku;
                document.getElementById('auto_recovery').checked = s.auto_recovery;
                document.getElementById('unify_small').checked = s.unify_small;
                wordStates = s.wordStates || {};
            }
        }

        async function loadDictionaryUI() {
            const r = await fetch('/get_dictionary');
            const dict = await r.json();
            const allWords = [...dict.country, ...dict.capital].sort();
            const list = document.getElementById('dict-manager');
            list.innerHTML = allWords.map(w => {
                const state = wordStates[w] || 'white';
                const style = state === 'red' ? "background: #f43f5e; color: white" : (state === 'blue' ? "background: #2563eb; color: white" : "");
                return `<button onclick="toggleWord(this, '${w}')" class="text-[9px] p-1 border rounded" style="${style}">${w}</button>`;
            }).join('');
        }

        function toggleWord(btn, word) {
            const cycle = { 'white': 'red', 'red': 'blue', 'blue': 'white' };
            wordStates[word] = cycle[wordStates[word] || 'white'];
            loadDictionaryUI();
            saveSettings();
        }

        function resetSettings() { localStorage.removeItem('ultraSettings'); location.reload(); }

        async function run() {
            const btn = document.getElementById('btn'); btn.innerText = "...";
            const r = await fetch('/search', {
                method: 'POST', headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    start_word: document.getElementById('sw').value,
                    all_start_char: document.getElementById('asc').value,
                    all_end_char: document.getElementById('aec').value,
                    timeout: document.getElementById('timeout').value,
                    limit: document.getElementById('limit').value,
                    rt: document.getElementById('rt').checked,
                    conj: document.getElementById('conj').checked,
                    use_shift: document.getElementById('use_shift').checked,
                    allow_daku: document.getElementById('allow_daku').checked,
                    allow_handaku: document.getElementById('allow_handaku').checked,
                    auto_recovery: document.getElementById('auto_recovery').checked,
                    unify_small: document.getElementById('unify_small').checked,
                    red_words: Object.keys(wordStates).filter(k => wordStates[k] === 'red'),
                    blue_words: Object.keys(wordStates).filter(k => wordStates[k] === 'blue'),
                    categories: ["country"]
                })
            });
            const d = await r.json();
            currentRoutes = d.routes;
            display();
            btn.innerText = "Explore";
        }

        function display() {
            document.getElementById('res').innerHTML = currentRoutes.map(rt => `
                <div class="glass p-3 rounded-xl text-sm font-bold">${rt.join(' → ')}</div>
            `).join('');
        }

        window.onload = () => { loadSettings(); loadDictionaryUI(); };
    </script>
</body>
</html>
