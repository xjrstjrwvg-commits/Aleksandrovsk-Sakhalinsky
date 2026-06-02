from flask import Flask, request, jsonify
from dictionary import build_nodes, DAKU_MAP, HANDAKU_MAP, REV_MAP, KANA_LIST

app = Flask(__name__)

NODES = build_nodes()


# =============================
# 文字ユーティリティ
# =============================
def variants(char, allow_daku=True, allow_handaku=True, allow_small=True):

    v = {char}

    if allow_daku:
        if char in DAKU_MAP:
            v.add(DAKU_MAP[char])
        if char in REV_MAP:
            v.add(REV_MAP[char])

    if allow_handaku:
        if char in HANDAKU_MAP:
            v.add(HANDAKU_MAP[char])

    return v


def strip_long(w):
    return w.replace("ー","")


# =============================
# 接続判定（通常＋牛耕）
# =============================
def can_connect(prev, nxt, idx, rt=False):

    if not rt:
        return prev.tail == nxt.head
    else:
        return (prev.tail == nxt.head) if idx % 2 == 0 else (prev.head == nxt.tail)


# =============================
# 50音シフト
# =============================
def shift_kana(c, k):
    if c not in KANA_LIST:
        return c
    i = KANA_LIST.index(c)
    return KANA_LIST[(i+k)%len(KANA_LIST)]


# =============================
# 遡り接続
# =============================
def auto_recovery(word):
    w = strip_long(word)
    return w[-1]


# =============================
# MCチェック
# =============================
def check_mc(path, mc):
    if not mc:
        return True
    text="".join(n.word for n in path)
    for k,v in mc.items():
        if text.count(k)!=v:
            return False
    return True


# =============================
# TTLチェック
# =============================
def check_ttl(path, ttl):
    if not ttl:
        return True
    return sum(len(n.word) for n in path)==ttl


# =============================
# 共役排除（前処理版）
# =============================
def exclude_conjugate(nodes):
    seen={}
    for n in nodes:
        k=(n.head,n.tail)
        seen.setdefault(k,[]).append(n)

    return [v[0] for v in seen.values() if len(v)==1] or nodes


# =============================
# DFS本体（完全仕様）
# =============================
def dfs(node,nodes,path,used,cfg,res,state):

    if state["stop"]:
        return

    if len(path)==cfg["ml"]:

        if not check_mc(path,cfg.get("mc")):
            return

        if not check_ttl(path,cfg.get("ttl")):
            return

        res.append([n.word for n in path])

        if len(res)>=cfg["limit"]:
            state["stop"]=True

        return


    idx=len(path)

    for nxt in nodes:

        if nxt.id in state["used"]:
            continue

        # 文字重複禁止
        if cfg["char_limit"] and (used & nxt.chars):
            continue

        # 接続＋牛耕
        if not can_connect(path[-1],nxt,idx,cfg["rt"]):
            continue

        state["used"].add(nxt.id)

        dfs(
            nxt,nodes,
            path+[nxt],
            used|nxt.chars,
            cfg,res,state
        )

        state["used"].remove(nxt.id)

        if state["stop"]:
            return


# =============================
# API
# =============================
@app.route("/search",methods=["POST"])
def search():

    d=request.json

    nodes=[n for n in NODES if n.cat==d.get("category","country")]

    # 共役排除
    if d.get("exclude_conjugate"):
        nodes=exclude_conjugate(nodes)

    cfg={
        "ml":int(d.get("ml",3)),
        "limit":int(d.get("limit",50)),
        "char_limit":d.get("char_limit_mode",False),
        "rt":d.get("rt",False),
        "mc":d.get("mc"),
        "ttl":d.get("ttl")
    }

    res=[]
    state={"stop":False,"used":set()}

    for s in nodes:
        dfs(s,nodes,[s],s.chars,cfg,res,state)
        if state["stop"]:
            break

    return jsonify({"count":len(res),"results":res})


if __name__=="__main__":
    app.run(debug=True)
