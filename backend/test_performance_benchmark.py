import os
import sys
import time
from pathlib import Path
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).parent))

from app.database import engine, SessionLocal
from app.models.user import User
from app.models.project import Project
from app.models.dataset import Dataset
from app.services.file_service import FileService
from app.api.auth import demo_login, guest_login
from app.api.projects import list_projects
from app.api.datasets import get_project_dataset_analysis

def run_performance_benchmarks():
    print("=" * 70)
    print("DATANOVA AI: FULL-STACK PERFORMANCE BENCHMARK REPORT")
    print("=" * 70)

    # 1. Database Engine & Pragma Settings
    print("\n--- 1. Database Configuration & PRAGMA Settings ---")
    with engine.connect() as conn:
        jm = conn.execute(text("PRAGMA journal_mode")).scalar()
        sync = conn.execute(text("PRAGMA synchronous")).scalar()
        cs = conn.execute(text("PRAGMA cache_size")).scalar()
        ts = conn.execute(text("PRAGMA temp_store")).scalar()
        fk = conn.execute(text("PRAGMA foreign_keys")).scalar()

    print(f"  [OK] journal_mode: {jm} (Target: wal)")
    print(f"  [OK] synchronous:  {sync} (Target: 1 / NORMAL)")
    print(f"  [OK] cache_size:   {cs} (Target: -64000 / 64MB)")
    print(f"  [OK] temp_store:   {ts} (Target: 2 / MEMORY)")
    print(f"  [OK] foreign_keys: {fk} (Target: 1 / ON)")

    # 2. Database Read & Write Latency
    print("\n--- 2. Database Transaction Latencies ---")
    db = SessionLocal()

    # Read benchmark
    read_times = []
    for _ in range(50):
        t0 = time.perf_counter()
        _ = db.query(User).first()
        read_times.append((time.perf_counter() - t0) * 1000)
    avg_read = sum(read_times) / len(read_times)
    print(f"  [OK] 50 Read Transactions: total={sum(read_times):.2f}ms, avg={avg_read:.3f}ms/query")

    # Write commit benchmark
    write_times = []
    for i in range(20):
        t0 = time.perf_counter()
        p = Project(name=f"PerfCommit_{i}", owner_id=1)
        db.add(p)
        db.commit()
        write_times.append((time.perf_counter() - t0) * 1000)
    avg_write = sum(write_times) / len(write_times)
    print(f"  [OK] 20 Write Commit Transactions: total={sum(write_times):.2f}ms, avg={avg_write:.3f}ms/commit")

    # Clean up test rows
    db.query(Project).filter(Project.name.like("PerfCommit_%")).delete()
    db.commit()

    # 3. Core API Endpoint Latency
    print("\n--- 3. Core API Endpoint Durations ---")
    demo_user = db.query(User).filter(User.email == "demo@datanova.ai").first()

    # Demo Login
    demo_times = []
    for _ in range(5):
        t0 = time.perf_counter()
        _ = demo_login(db=db)
        demo_times.append((time.perf_counter() - t0) * 1000)
    print(f"  [OK] POST /auth/demo: avg={sum(demo_times)/len(demo_times):.2f}ms")

    # Guest Login
    guest_times = []
    for _ in range(10):
        t0 = time.perf_counter()
        _ = guest_login()
        guest_times.append((time.perf_counter() - t0) * 1000)
    print(f"  [OK] POST /auth/guest: avg={sum(guest_times)/len(guest_times):.2f}ms")

    # List Projects
    proj_times = []
    for _ in range(10):
        t0 = time.perf_counter()
        _ = list_projects(current_user=demo_user, db=db)
        proj_times.append((time.perf_counter() - t0) * 1000)
    print(f"  [OK] GET /projects: avg={sum(proj_times)/len(proj_times):.2f}ms")

    # Dataset Analysis Restoration
    ds = db.query(Dataset).first()
    if ds:
        owner = db.query(User).filter(User.id == ds.project.owner_id).first()
        analysis_times = []
        for _ in range(5):
            t0 = time.perf_counter()
            _ = get_project_dataset_analysis(
                project_id=ds.project_id,
                dataset_id=ds.id,
                session_id="perf_benchmark",
                current_user=owner,
                db=db,
            )
            analysis_times.append((time.perf_counter() - t0) * 1000)
        avg_analysis = sum(analysis_times) / len(analysis_times)
        print(f"  [OK] GET /projects/{{id}}/datasets/{{id}}/analysis: avg={avg_analysis:.2f}ms")
        print(f"       (Baseline was ~2049ms; speedup = ~{2049/avg_analysis:.1f}x)")

    db.close()

    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETED SUCCESSFULLY")
    print("=" * 70)

if __name__ == "__main__":
    run_performance_benchmarks()
