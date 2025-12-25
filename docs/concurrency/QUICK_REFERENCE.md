# Concurrency Models Quick Reference

## At a Glance

| Model | Concurrency | Memory | Best For | Used in EventStreamMonitor |
|-------|------------|--------|----------|---------------------------|
| **Gunicorn** | 8-16 requests | High | CPU-bound, Flask apps | ✅ All services |
| **Async/Await** | 1000+ requests | Low | I/O-bound, high concurrency | ❌ Not used |
| **ThreadPoolExecutor** | 20-100 threads | Medium | Parallel tasks, scripts | ✅ Test scripts |

---

## Gunicorn (Current Implementation)

```python
# Configuration
workers = 4
threads = 2
worker_class = 'sync'

# Total: 4 × 2 = 8 concurrent requests
```

**Code Example:**
```python
# Synchronous Flask route
@app.route("/users/register", methods=["POST"])
def register_user():
    user = db.query(...)  # Blocks thread
    return jsonify(user)
```

**When to Use:**
- ✅ Existing Flask applications
- ✅ CPU-bound workloads
- ✅ Need process isolation
- ✅ Simple deployment

---

## Async/Await (Not Currently Used)

```python
# Single event loop
# Can handle 1000+ concurrent requests
```

**Code Example:**
```python
# Async route (FastAPI example)
@app.post("/users/register")
async def register_user():
    user = await db.fetch(...)  # Non-blocking!
    return user
```

**When to Use:**
- ✅ I/O-bound workloads
- ✅ Need 1000+ concurrent connections
- ✅ Real-time applications (WebSockets)
- ✅ Many external API calls

---

## ThreadPoolExecutor (Test Scripts)

```python
# Manual thread pool
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(task, i) for i in range(100)]
    results = [f.result() for f in as_completed(futures)]
```

**When to Use:**
- ✅ Parallelizing independent tasks
- ✅ Load testing
- ✅ Background job processing
- ✅ One-off parallel operations

---

## Performance Comparison

### Scenario: 1000 requests, each takes 100ms (I/O wait)

| Model | Concurrent | Total Time | Memory |
|-------|-----------|------------|--------|
| Gunicorn (8) | 8 | ~12.5 seconds | ~400MB |
| Async/Await | 1000+ | ~100ms | ~100MB |
| ThreadPoolExecutor (20) | 20 | ~5 seconds | ~200MB |

---

## Migration Path

### Current: Gunicorn → Future: Async/Await

1. **Option 1: FastAPI** (Recommended)
   ```python
   from fastapi import FastAPI
   import asyncpg
   
   app = FastAPI()
   
   @app.post("/users/register")
   async def register_user():
       async with db_pool.acquire() as conn:
           user = await conn.fetchrow("SELECT * FROM users...")
       return user
   ```

2. **Option 2: Flask with async** (Python 3.7+)
   ```python
   from flask import Flask
   
   app = Flask(__name__)
   
   @app.route("/users/register")
   async def register_user():
       user = await db.fetch(...)
       return jsonify(user)
   ```

---

## Key Takeaways

1. **Gunicorn** = Multi-process, multi-thread → Best for CPU-bound, existing Flask apps
2. **Async/Await** = Single-threaded event loop → Best for I/O-bound, high concurrency
3. **ThreadPoolExecutor** = Manual threading → Best for parallelizing independent tasks

**EventStreamMonitor uses Gunicorn** because:
- Works with existing Flask code
- Simple to deploy
- Good performance for current workload
- Process isolation

For detailed explanation, see [Concurrency Models Explained](CONCURRENCY_MODELS_EXPLAINED.md).

