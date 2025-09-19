from flask import Flask, request, jsonify
import os, requests, sqlite3, pathlib

app = Flask(__name__)

# ---- External services (still available if you want them) ----
STEAM = os.getenv('STEAM_API_URL', 'http://steam_api:5002')
DBAPI = os.getenv('DB_API_URL',   'http://db_api:5000')  # unused when USE_SQLITE=1
OCR   = os.getenv('OCR_URL',      'http://ocr:5003')
LLM   = os.getenv('LLM_URL',      'http://llm:5004')

USE_SQLITE = os.getenv("USE_SQLITE", "1") == "1"
SQLITE_PATH = os.getenv("SQLITE_PATH", "/data/matches.db")

# ---- Helpers ------------------------------------------------
def ok(x=None): return jsonify(x or {"ok": True})
def err(status, msg, detail=None):
    out={"error": msg}; 
    if detail: out["detail"]=str(detail)
    return jsonify(out), status

def _sqlite_conn():
    pathlib.Path(SQLITE_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _ensure_sqlite():
    with _sqlite_conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS Match(
            MatchID INTEGER PRIMARY KEY AUTOINCREMENT,
            UserID  INTEGER,
            Won     INTEGER -- 1=true, 0=false
        )""")
        c.commit()

def _seed_sqlite(user_id: int):
    with _sqlite_conn() as c:
        cur = c.execute("SELECT COUNT(*) AS c FROM Match WHERE UserID=?", (user_id,))
        if cur.fetchone()["c"] == 0:
            for won in [1,0,1,1,0]:
                c.execute("INSERT INTO Match(UserID,Won) VALUES(?,?)", (user_id, won))
            c.commit()

# ---- Routes -------------------------------------------------
@app.get("/")
def index():
    return ok({
        "service":"match-service",
        "mode":"sqlite" if USE_SQLITE else "db_api",
        "endpoints":{
            "GET /health":"basic health check",
            "GET /pattern?user_id=1":"compute win/loss ratio",
            "GET /similar?steamid=...":"propose similar players",
            "POST /coach":"coaching tips"
        }
    })

@app.get("/health")
def health(): return ok()

@app.get("/pattern")
def pattern():
    user = int(request.args.get("user_id","1"))
    try:
        if USE_SQLITE:
            _ensure_sqlite()
            _seed_sqlite(user)
            with _sqlite_conn() as c:
                row = c.execute("""
                    SELECT
                      SUM(CASE WHEN Won=1 THEN 1 ELSE 0 END) AS wins,
                      SUM(CASE WHEN Won=0 THEN 1 ELSE 0 END) AS losses
                    FROM Match WHERE UserID=?""", (user,)
                ).fetchone()
            wins   = int(row["wins"] or 0)
            losses = int(row["losses"] or 0)
        else:
            # Old path via DB_API (kept for later if you fix DB_API)
            def db_post(payload):
                r = requests.post(f"{DBAPI}/execute_sql", json=payload, timeout=10)
                r.raise_for_status()
                return r.json()
            db_post({"query":'CREATE TABLE IF NOT EXISTS "Match"("MatchID" SERIAL PRIMARY KEY,"UserID" INT,"Won" BOOLEAN)'})
            cnt = db_post({"query":'SELECT COUNT(*) AS c FROM "Match" WHERE "UserID"=%s', "params":[user]})["results"][0]["c"]
            if not cnt:
                for won in [True,False,True,True,False]:
                    db_post({"query":'INSERT INTO "Match"("UserID","Won") VALUES (%s,%s)', "params":[user, won]})
            agg = db_post({"query":(
                'SELECT COALESCE(SUM(CASE WHEN "Won" THEN 1 ELSE 0 END),0) AS wins,'
                'COALESCE(SUM(CASE WHEN NOT "Won" THEN 1 ELSE 0 END),0) AS losses '
                'FROM "Match" WHERE "UserID"=%s'), "params":[user]})["results"][0]
            wins, losses = int(agg["wins"]), int(agg["losses"])

        ratio = round(wins / max(losses,1), 2)
        return ok({"user_id": user, "wins": wins, "losses": losses, "win_loss_ratio": ratio})
    except requests.HTTPError as e:
        return err(502, "DB_API HTTP error", e)
    except Exception as e:
        return err(500, "Failed to compute pattern", e)

@app.get("/similar")
def similar():
    sid = request.args.get("steamid")
    if not sid:
        return err(400, "steamid required (query param)")
    try:
        # If no Steam key, just return a friendly stub instead of erroring
        try:
            cs2  = requests.get(f"{STEAM}/steam/user/{sid}/cs2", timeout=10).json().get("playtime", {})
            frns = requests.get(f"{STEAM}/steam/user/{sid}/friends", timeout=10).json().get("friends", [])
        except Exception:
            cs2, frns = {"appid":730,"playtime_forever":1200}, [{"steamid":"stub1"},{"steamid":"stub2"}]
        return ok({"user": sid, "cs2_playtime": cs2, "candidate_friends": frns[:10]})
    except Exception as e:
        return err(500, "Failed to fetch similar players", e)

@app.post("/coach")
def coach():
    try:
        payload = request.get_json(force=True, silent=True) or {}
        r = requests.post(f"{LLM}/coach", json=payload, timeout=10)
        r.raise_for_status()
        return ok(r.json())
    except requests.HTTPError as e:
        return err(502, "LLM service HTTP error", e)
    except Exception as e:
        return err(500, "Failed to get coaching tips", e)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
