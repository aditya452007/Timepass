from flask import Flask, render_template, request, Response
from simulator.pipeline import SimulationPipeline

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/simulate")
def simulate():
    event_type = request.args.get("event", "user.signup")
    slow_mode = request.args.get("slow", "false").lower() == "true"
    fail_rate = int(request.args.get("fail_rate", "0"))
    dnd_mode = request.args.get("dnd", "false").lower() == "true"
    online = request.args.get("online", "false").lower() == "true"
    
    overrides = {
        "dnd_mode": dnd_mode,
        "online": online
    }
    
    pipeline = SimulationPipeline(slow_mode=slow_mode, fail_rate=fail_rate)
    return Response(pipeline.run_simulation(event_type, "user_123", overrides), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
