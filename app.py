from flask import Flask, request, jsonify
from engine import runSearch
from dictionary import DICTIONARY_MASTER

app = Flask(__name__)

@app.route("/get_dictionary")
def get_dictionary():
    return jsonify(DICTIONARY_MASTER)

@app.route("/search", methods=["POST"])
def search():
    d = request.json

    # 必要な項目だけ抽出（削除対象は完全排除）
    params = {
        "start_word": d.get("start_word", ""),
        "start_char": d.get("start_char", ""),
        "all_start_char": d.get("all_start_char", ""),
        "must_char": d.get("must_char", ""),
        "end_char": d.get("end_char", ""),
        "all_end_char": d.get("all_end_char", ""),
        "exclude_chars": d.get("exclude_chars", ""),
        "ban_start_chars": d.get("ban_start_chars", ""),
        "valid_chars": d.get("valid_chars", ""),
        "max_len": d.get("max_len", 5),

        # shift 系
        "use_shift": d.get("use_shift", False),
        "ks_abs": d.get("ks_abs", 1),
        "shift_mode": d.get("shift_mode", "abs"),

        # 濁点系
        "allow_daku": d.get("allow_daku", False),
        "allow_handaku": d.get("allow_handaku", False),

        # その他
        "auto_recovery": d.get("auto_recovery", False),
        "char_limit_mode": d.get("char_limit_mode", False),
        "round_trip": d.get("round_trip", False),
        "exclude_conjugate": d.get("exclude_conjugate", False),

        # 辞書カテゴリ
        "categories": d.get("categories", ["country"]),

        # 色指定
        "red_words": d.get("red_words", []),
        "blue_words": d.get("blue_words", [])
    }

    result = runSearch(params)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
