from flask import Flask, request, jsonify
app = Flask(__name__)

@app.post("/coach")
def coach():
    data = request.get_json(force=True, silent=True) or {}
    kills  = float(data.get("kills", 0))
    deaths = float(data.get("deaths", 1))
    adr    = float(data.get("adr", 0))
    tips = []
    if deaths and kills/deaths < 1: tips.append("Improve survival: trade with a buddy, avoid dry peeks.")
    if adr < 70: tips.append("Utility/impact low: practice nades, pre-aim common angles.")
    if kills < 15: tips.append("Aim: 10-min KovaaK/Aim Lab + DM warmup.")
    return jsonify({"kdr": round(kills/max(deaths,1),2), "adr": adr, "tips": tips or ["Solid performance—keep it up!"]})

@app.get("/health")
def health():
    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
