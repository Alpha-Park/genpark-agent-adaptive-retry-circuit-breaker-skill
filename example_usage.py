from client import AdaptiveCircuitBreakerClient
import sys, time
sys.stdout.reconfigure(encoding='utf-8')

def main():
    breaker = AdaptiveCircuitBreakerClient(failure_threshold=3, recovery_timeout_sec=0.5)
    print("=== ADAPTIVE RETRY CIRCUIT BREAKER ENGINE ===")

    print()
    print("1. Simulating 3 consecutive failures to trigger trip...")
    for i in range(1, 4):
        status = breaker.allow_request()
        fail_res = breaker.record_failure()
        backoff = breaker.compute_backoff(i)
        print(f"  Attempt {i}: Allowed={status['allowed']} | Trip State={fail_res['state']} | Backoff={backoff}s")

    print()
    print("2. Verifying OPEN state blocks requests...")
    blocked = breaker.allow_request()
    print(f"  Immediate Request: Allowed={blocked['allowed']} | State={blocked['state']} | Retry After: {blocked.get('retry_after_sec')}s")

    print()
    print("3. Waiting for recovery timeout (0.5s)...")
    time.sleep(0.55)
    probe = breaker.allow_request()
    print(f"  Probe Request: Allowed={probe['allowed']} | State={probe['state']} ({probe['reason']})")

    breaker.record_success()
    breaker.record_success()
    print(f"  After 2 successes -> Circuit State Restored to: {breaker.state}")

if __name__ == "__main__":
    main()
