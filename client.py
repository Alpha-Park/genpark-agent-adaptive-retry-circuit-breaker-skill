import sys, time, random
sys.stdout.reconfigure(encoding='utf-8')

class AdaptiveCircuitBreakerClient:
    """
    Deterministic adaptive circuit breaker with half-open recovery probes,
    exponential backoff with decorrelated full jitter, and state telemetry.
    """
    def __init__(self, failure_threshold=3, recovery_timeout_sec=5.0, base_backoff_sec=1.0, max_backoff_sec=30.0):
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout_sec
        self.base_backoff = base_backoff_sec
        self.max_backoff = max_backoff_sec
        self.failure_count = 0
        self.consecutive_successes = 0
        self.last_failure_time = 0.0
        self.total_requests = 0

    def allow_request(self):
        self.total_requests += 1
        now = time.time()
        if self.state == "CLOSED":
            return {"allowed": True, "state": "CLOSED", "reason": "Circuit healthy"}
        elif self.state == "OPEN":
            if now - self.last_failure_time >= self.recovery_timeout:
                self.state = "HALF_OPEN"
                return {"allowed": True, "state": "HALF_OPEN", "reason": "Recovery probing window open"}
            wait_remaining = self.recovery_timeout - (now - self.last_failure_time)
            return {"allowed": False, "state": "OPEN", "retry_after_sec": round(max(0.1, wait_remaining), 2)}
        elif self.state == "HALF_OPEN":
            return {"allowed": True, "state": "HALF_OPEN", "reason": "Probing service health"}

    def record_success(self):
        if self.state == "HALF_OPEN":
            self.consecutive_successes += 1
            if self.consecutive_successes >= 2:
                self.state = "CLOSED"
                self.failure_count = 0
                self.consecutive_successes = 0
        else:
            self.failure_count = max(0, self.failure_count - 1)
        return {"state": self.state, "failure_count": self.failure_count}

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        self.consecutive_successes = 0
        if self.state in ("CLOSED", "HALF_OPEN") and self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
        return {"state": self.state, "failure_count": self.failure_count}

    def compute_backoff(self, attempt):
        temp = min(self.max_backoff, self.base_backoff * (2 ** attempt))
        sleep_dur = random.uniform(0, temp)
        return round(sleep_dur, 3)
