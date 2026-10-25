import sys, json
from client import AdaptiveCircuitBreakerClient
sys.stdout.reconfigure(encoding='utf-8')

def handle_mcp():
    breaker = AdaptiveCircuitBreakerClient()
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print(json.dumps({"status": "ready", "skill": "genpark-agent-adaptive-retry-circuit-breaker-skill"}))
        return
    req = json.loads(sys.stdin.read() or "{}")
    action = req.get("action", "allow_request")
    if action == "record_failure":
        res = breaker.record_failure()
    elif action == "record_success":
        res = breaker.record_success()
    else:
        res = breaker.allow_request()
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    handle_mcp()
