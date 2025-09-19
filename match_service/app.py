from flask import Flask, request, jsonify
import os, requests

app = Flask(__name__)

# ---- Service URLs (overridden by docker-compose env) ----
STEAM = os.getenv('STEAM_API_URL', 'http://steam_api:5002')
DB    = os.getenv('DB_API_URL',   'http://db_api:5001')
OCR   = os.getenv('OCR_URL',      'http://ocr:5003')
LLM   = os.getenv('LLM_URL',      'http://llm:5004')

# ---- Helpers ------------------------------------------------
def db_post(payload):
    """Call DB_API /execute_sql and raise on HTTP errors."""
    r = requests.post(f"{DB}/execute_sql", json=payload, timeout=10)
    r.raise_for_status()
    return r.json()

def ok(data=None):
    return jsonify(data or {"ok": True})

def err(status, msg, detail=None):
    out = {"error": msg}
    if detail is not None:
        out["detail"] = detail
    return jsonify(out), status

# ---- Routes -------------------------------------------------
@app.get("/")
def index():
    return ok({
        "service": "match-service",
        "endpoints": {
            "GET /health": "basic health check",
            "GET /pattern?user_id=1": "compute win/loss ratio via DB_API",
            "GET /similar?steamid=...": "propose similar players via Steam_API",
            "POST /coach": "get coaching tips via llm façade"
        }
    })

@app.get("/health")
def health():
    return ok()

@app.get("/pattern")
def pattern():
    """Compute win/loss ratio for a user. Seeds demo data on first run."""
    user = request.args.get("user_id", "1")
    try:
        # 1) Ensure table exists (quoted names preserve casing)
        db_post({
            "query": (
                'CREATE TABLE IF NOT EXISTS "Match" ('
                '  "MatchID" SERIAL PRIMARY KEY,'
                '  "UserID"  INT,'
                '  "Won"     BOOLEAN)'
            )
        })

        # 2) Seed demo data if empty
        cnt = db_post({
            "query": 'SELECT COUNT(*) AS c FROM "Match" WHERE "UserID" = %s',
            "params": [user]
        })["results"][0]["c"]
        if not cnt:
            for won in [True, False, True, True, False]:
                db_post({
                    "query": 'INSERT INTO "Match"("UserID","Won") VALUES (%s,%s)',
                    "params": [user, won]
                })

        # 3) Aggregate wins/losses in SQL
        agg = db_post({
            "query": (
                'SELECT '
                '  COALESCE(SUM(CASE WHEN "Won" THEN 1 ELSE 0 END),0) AS wins,'
                '  COALESCE(SUM(CASE WHEN NOT "Won" THEN 1 ELSE 0 END),0) AS losses '
                'FROM "Match" WHERE "UserID" = %s'
            ),
            "params": [user]
        })["results"][0]

        wins   = int(agg["wins"])
        losses = int(agg["losses"])
        ratio  = round(wins / max(losses, 1), 2)
        return ok({"user_id": user, "wins": wins, "losses": losses, "win_loss_ratio": ratio})

    except requests.HTTPError as e:
        return err(502, "DB_API HTTP error", str(e))
    except Exception as e:
        return err(500, "Failed to compute pattern", str(e))

@app.get("/similar")
def similar():
    """Use Steam_API to fetch playtime + friends (simple 'similar players' signal)."""
    sid = request.args.get("steamid")
    if not sid:
        return err(400, "steamid required (query param)")
    try:
        cs2     = requests.get(f"{STEAM}/steam/user/{sid}/cs2", timeout=15).json().get("playtime", {})
        friends = requests.get(f"{STEAM}/steam/user/{sid}/friends", timeout=15).json().get("friends", [])
        return ok({"user": sid, "cs2_playtime": cs2, "candidate_friends": friends[:10]})
    except requests.HTTPError as e:
        return err(502, "Steam_API HTTP error", str(e))
    except Exception as e:
        return err(500, "Failed to fetch similar players", str(e))

@app.post("/coach")
def coach():
    """Forward player stats to LLM façade for tips."""
    try:
        payload = request.get_json(force=True, silent=True) or {}
        r = requests.post(f"{LLM}/coach", json=payload, timeout=15)
        r.raise_for_status()
        return ok(r.json())
    except requests.HTTPError as e:
        return err(502, "LLM service HTTP error", str(e))
    except Exception as e:
        return err(500, "Failed to get coaching tips", str(e))

# ---- Main ---------------------------------------------------
if __name__ == "__main__":
    # If you ever run this outside Docker, 5000 matches docker-compose mapping.
    app.run(host="0.0.0.0", port=5000)
