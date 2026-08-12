import concurrent.futures
import sys
import time
from pathlib import Path

backend_paths = [
    Path(__file__).resolve().parent.parent.parent / "mobile" / "PreCare-App" / "precare__backend-main",
    Path(__file__).resolve().parent.parent / "mobile" / "PreCare-App" / "precare__backend-main",
    Path(__file__).resolve().parent / "precare__backend-main",
    Path(__file__).resolve().parent,
]
for p in backend_paths:
    if p.exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

from app.db import Base, SessionLocal, engine
from services.maya_service import chat_with_maya

# Initialize tables if not already present
Base.metadata.create_all(bind=engine)


def query_maya(index):
    start = time.time()
    db = SessionLocal()
    try:
        res = chat_with_maya(db=db, user_id=1, message="What type of excersices can u suggest me in week 32")
        elapsed = time.time() - start
        assert len(res["reply"]) > 20
        return elapsed
    finally:
        db.close()


def test_concurrent_maya_load():
    """Simulate 30 concurrent mobile users asking pregnancy queries."""
    concurrency = 30
    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(query_maya, i) for i in range(concurrency)]
        latencies = [f.result() for f in concurrent.futures.as_completed(futures)]

    total_time = time.time() - start_time
    avg_latency = sum(latencies) / len(latencies)
    p95_latency = sorted(latencies)[int(len(latencies) * 0.95)]

    print(f"\n--- PreCare Load Test Results ---")
    print(f"Total Requests: {concurrency}")
    print(f"Total Duration: {total_time:.3f}s")
    print(f"Throughput: {concurrency / total_time:.2f} req/s")
    print(f"Average Latency: {avg_latency * 1000:.2f}ms")
    print(f"P95 Latency: {p95_latency * 1000:.2f}ms")

    assert avg_latency < 0.5, "Average latency exceeded 500ms threshold!"


if __name__ == "__main__":
    test_concurrent_maya_load()
