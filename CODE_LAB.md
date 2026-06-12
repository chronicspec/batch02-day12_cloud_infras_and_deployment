# Code Lab: Deploy Your AI Agent to Production

> **AICB-P1 · VinUniversity 2026**  
> Thời gian: 3-4 giờ | Độ khó: Intermediate

## Mục Tiêu

Sau khi hoàn thành lab này, bạn sẽ:

- Hiểu sự khác biệt giữa development và production
- Containerize một AI agent với Docker
- Deploy agent lên cloud platform
- Bảo mật API với authentication và rate limiting
- Thiết kế hệ thống có khả năng scale và reliable

---

## Yêu Cầu

```bash
 Python 3.11+
 Docker & Docker Compose
 Git
 Text editor (VS Code khuyến nghị)
 Terminal/Command line
```

**Không cần:**

- OpenAI API key (dùng mock LLM)
- Credit card
- Kinh nghiệm DevOps trước đó

---

## Lộ Trình Lab

| Phần | Thời gian | Nội dung |
|------|-----------|----------|
| **Part 1** | 30 phút | Localhost vs Production |
| **Part 2** | 45 phút | Docker Containerization |
| **Part 3** | 45 phút | Cloud Deployment |
| **Part 4** | 40 phút | API Security |
| **Part 5** | 40 phút | Scaling & Reliability |
| **Part 6** | 60 phút | Final Project |

---

## Part 1: Localhost vs Production (30 phút)

### Concepts

**Vấn đề:** "It works on my machine" — code chạy tốt trên laptop nhưng fail khi deploy.

**Nguyên nhân:**

- Hardcoded secrets
- Khác biệt về environment (Python version, OS, dependencies)
- Không có health checks
- Config không linh hoạt

**Giải pháp:** 12-Factor App principles

### Exercise 1.1: Phát hiện anti-patterns

```bash
cd 01-localhost-vs-production/develop
```

**Nhiệm vụ:** Đọc `app.py` và tìm ít nhất 5 vấn đề.

1. API Key bị Hardcode: OPENAI_API_KEY và DATABASE_URL được viết trực tiếp vào code. Nếu code này bị đẩy lên GitHub, kẻ gian sẽ thấy được key và có thể xài lén gây thiệt hại về tài chính.
2. Hardcode Cấu Hình (Config): Các biến cấu hình như DEBUG = True, MAX_TOKENS = 500 không được lấy từ file .env hay biến môi trường. Mỗi khi muốn đổi, ta lại phải sửa code và deploy lại.
3. Print log bừa bãi và làm lộ Secret: Việc dùng print() thay vì thư viện logging chuyên nghiệp không tiện cho việc tìm lỗi sau này. Tệ hơn, dòng print(f"[DEBUG] Using key: {OPENAI_API_KEY}") in thẳng Secret Key ra file log.
4. Không có Health Check endpoint: Không có các đường dẫn như /health hay /ready. Nếu ứng dụng bị treo, nền tảng Cloud (như Render, Railway, Kubernetes) sẽ không biết để tự động khởi động lại (restart) ứng dụng.
5. Cố định Port và Host: Code gán cứng host="localhost" và port=8000. Khi đóng gói bằng Docker hoặc đưa lên Cloud, ứng dụng thường phải lắng nghe ở IP 0.0.0.0 và cổng do Cloud tự động cấp (thông qua biến môi trường PORT), nếu gán cứng như vậy ứng dụng sẽ không nhận được traffic từ bên ngoài.

<details>
<summary> Gợi ý</summary>

Tìm:

- API key hardcode
- Port cố định
- Debug mode
- Không có health check
- Không xử lý shutdown

</details>

### Exercise 1.2: Chạy basic version

```bash
pip install -r requirements.txt
python app.py
```

Test:

```bash
curl -X POST "http://localhost:8000/ask?question=hello"
```

**Quan sát:** Nó chạy! Nhưng có production-ready không?
Bình thường, nếu chạy python app.py ở file develop, nó sẽ chạy thành công trên máy tính của chúng ta (Works on my machine). Tuy nhiên, vì nó có các lỗi ở phần 1.1, quá trình vận hành sau này sẽ gặp vô số rủi ro về bảo mật cũng như tính sẵn sàng của ứng dụng.

### Exercise 1.3: So sánh với advanced version

```bash
cd ../production
cp .env.example .env
pip install -r requirements.txt
python app.py
```

**Nhiệm vụ:** So sánh 2 files `app.py`. Điền vào bảng:

| Feature | Basic | Advanced | Tại sao quan trọng? |
|---------|-------|----------|---------------------|
| Config | Hardcode | Env vars | Giữ bí mật an toàn (không lộ lên Git), thay đổi linh hoạt mà không cần sửa code. |
| Health check | Không có | Có /health (liveness) và /ready (readiness) | Giúp Cloud/Load Balancer biết khi nào app treo để tự khởi động lại, và khi nào sẵn sàng nhận request. |
| Logging | print() | JSON | Dễ dàng đưa vào các hệ thống phân tích log lớn (Datadog, Kibana), dễ filter lỗi, và không in ra secret. |
| Shutdown | Đột ngột | Graceful | Cho phép các request đang xử lý dở được chạy cho xong rồi mới tắt hẳn, giúp người dùng không bị văng lỗi 502/504. |
| Network Binding | localhost:8000 | 0.0.0.0 và dùng biến môi trường PORT | Ứng dụng mới có thể giao tiếp được ra bên ngoài khi nằm trong Docker Container hoặc chạy trên Cloud. |

### Checkpoint 1

- [ ] Hiểu tại sao hardcode secrets là nguy hiểm
- [ ] Biết cách dùng environment variables
- [ ] Hiểu vai trò của health check endpoint
- [ ] Biết graceful shutdown là gì

---

## Part 2: Docker Containerization (45 phút)

### Concepts

**Vấn đề:** "Works on my machine" part 2 — Python version khác, dependencies conflict.

**Giải pháp:** Docker — đóng gói app + dependencies vào container.

**Benefits:**

- Consistent environment
- Dễ deploy
- Isolation
- Reproducible builds

### Exercise 2.1: Dockerfile cơ bản

```bash
cd ../../02-docker/develop
```

**Nhiệm vụ:** Đọc `Dockerfile` và trả lời:

1. Base image là gì?
Là python:3.11. Đây là bản phân phối đầy đủ của Python (full distribution), chứa rất nhiều công cụ đi kèm nên dung lượng khá nặng (khoảng ~1GB).
2. Working directory là gì?
Là thư mục /app trong Container. Tất cả các lệnh sau đó (RUN, COPY, CMD) sẽ được thực thi hoặc xử lý trong thư mục này.
3. Tại sao COPY requirements.txt trước?
Để tận dụng Docker layer caching. Khi ta sửa code Python nhưng không sửa file dependencies, Docker sẽ không chạy lại bước cài đặt thư viện (RUN pip install), giúp build image rất nhanh.
4. CMD vs ENTRYPOINT khác nhau thế nào?
CMD là lệnh mặc định khi container chạy, nhưng nó rất dễ bị ghi đè (overwrite) khi bạn gõ thêm lệnh đằng sau docker run. Ví dụ: docker run my-agent bash sẽ chạy bash thay vì lệnh CMD.
ENTRYPOINT biến container thành một file thực thi cố định. Những gì bạn gõ sau docker run sẽ được truyền vào làm tham số (arguments) cho ENTRYPOINT thay vì ghi đè nó.

### Exercise 2.2: Build và run

```bash
# Build image
docker build -f 02-docker/develop/Dockerfile -t my-agent:develop .

# Run container
docker run -p 8000:8000 my-agent:develop

# Test
curl http://localhost:8000/ask -X POST \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Docker?"}'
```

**Quan sát:** Image size là bao nhiêu?
REPOSITORY   TAG       IMAGE ID       CREATED          SIZE  
my-agent     develop   0d4f0535c0b9   11 minutes ago   1.66GB

```bash
docker images my-agent:develop
```

### Exercise 2.3: Multi-stage build

```bash
cd ../production
```

**Nhiệm vụ:** Đọc `Dockerfile` và tìm:

- Stage 1 làm gì?
(Builder) stage build ra image chứa tất cả tools và source code.
- Stage 2 làm gì?
(Runtime) Stage runtime chỉ chứa runtime dependencies và code cần để chạy app.
- Tại sao image nhỏ hơn?
Vì Stage 2 đã bỏ lại toàn bộ rác, cache từ hệ điều hành và các công cụ compile. File image cuối cùng rất sạch, gọn nhẹ (< 500MB) và đặc biệt bảo mật hơn vì kẻ tấn công không có sẵn công cụ biên dịch để khai thác lỗ hổng nếu lỡ xâm nhập được. File này còn cẩn thận tạo một appuser riêng chứ không chạy bằng quyền root nguy hiểm.

Build và so sánh:

```bash
docker build -t my-agent:advanced .
docker images | grep my-agent
```

### Exercise 2.4: Docker Compose stack

**Nhiệm vụ:** Đọc `docker-compose.yml` và vẽ architecture diagram.

```bash
docker compose up
```

Services nào được start? Chúng communicate thế nào?
Có 3 service chính: Frontend (chạy React), Backend (API), và Database (PostgreSQL).

- Frontend giao tiếp với Backend qua cổng 8000.
- Frontend giao tiếp với PostgreSQL qua cổng 5432.
- Backend giao tiếp với PostgreSQL qua cổng 5432.

Test:

```bash
# Health check
curl http://localhost/health

# Agent endpoint
curl http://localhost/ask -X POST \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain microservices"}'
```

### Checkpoint 2

- [ ] Hiểu cấu trúc Dockerfile
- [ ] Biết lợi ích của multi-stage builds
- [ ] Hiểu Docker Compose orchestration
- [ ] Biết cách debug container (`docker logs`, `docker exec`)

---

## Part 3: Cloud Deployment (45 phút)

### Concepts

**Vấn đề:** Laptop không thể chạy 24/7, không có public IP.

**Giải pháp:** Cloud platforms — Railway, Render, GCP Cloud Run.

**So sánh:**

| Platform | Độ khó | Free tier | Best for |
|----------|--------|-----------|----------|
| Railway | ⭐ | $5 credit | Prototypes |
| Render | ⭐⭐ | 750h/month | Side projects |
| Cloud Run | ⭐⭐⭐ | 2M requests | Production |

### Exercise 3.1: Deploy Railway (15 phút)

```bash
cd ../../03-cloud-deployment/railway
```

**Steps:**

1. Install Railway CLI:

```bash
npm i -g @railway/cli
```

1. Login:

```bash
railway login
```

1. Initialize project:

```bash
railway init
```

1. Set environment variables:

```bash
railway variables set PORT=8000
railway variables set AGENT_API_KEY=my-secret-key
```

1. Deploy:

```bash
railway up
```

1. Get public URL:

```bash
railway domain
```

**Nhiệm vụ:** Test public URL với curl hoặc Postman.

Test:

```bash
# Health check
curl http://student-agent-domain/health

# Agent endpoint
curl http://studen-agent-domain/ask -X POST \
  -H "Content-Type: application/json" \
  -d '{"question": ""}'
```

### Exercise 3.2: Deploy Render (15 phút)

```bash
cd ../render
```

**Steps:**

1. Push code lên GitHub (nếu chưa có)
2. Vào [render.com](https://render.com) → Sign up
3. New → Blueprint
4. Connect GitHub repo
5. Render tự động đọc `render.yaml`
6. Set environment variables trong dashboard
7. Deploy!

**Nhiệm vụ:** So sánh `render.yaml` với `railway.toml`. Khác nhau gì?
render.yaml sử dụng cấu hình YAML thuần túy cho từng service riêng biệt, còn railway.toml dùng cấu trúc "mở rộng" (extensible) với các trường như services, templates, và pipelines. render.yaml có cấu trúc đơn giản, dễ đọc, phù hợp với các dự án nhỏ và vừa.

### Exercise 3.3: (Optional) GCP Cloud Run (15 phút)

```bash
cd ../production-cloud-run
```

**Yêu cầu:** GCP account (có free tier).

**Nhiệm vụ:** Đọc `cloudbuild.yaml` và `service.yaml`. Hiểu CI/CD pipeline.

### Checkpoint 3

- [ ] Deploy thành công lên ít nhất 1 platform
- [ ] Có public URL hoạt động
- [ ] Hiểu cách set environment variables trên cloud
- [ ] Biết cách xem logs

---

## Part 4: API Security (40 phút)

### Concepts

**Vấn đề:** Public URL = ai cũng gọi được = hết tiền OpenAI.

**Giải pháp:**

1. **Authentication** — Chỉ user hợp lệ mới gọi được
2. **Rate Limiting** — Giới hạn số request/phút
3. **Cost Guard** — Dừng khi vượt budget

### Exercise 4.1: API Key authentication

```bash
cd ../../04-api-gateway/develop
```

**Nhiệm vụ:** Đọc `app.py` và tìm:

- API key được check ở đâu?
Tại api_key_required là một decorator, được định nghĩa trong file security.py. Hàm này hoạt động như một middleware (trung gian) của FastAPI. Khi có request tới, nó sẽ kiểm tra xem header X-API-Key có khớp với AGENT_API_KEY đã cấu hình trong biến môi trường không. Nếu không khớp, nó sẽ trả về lỗi 401 Unauthorized ngay lập tức trước khi request kịp tới endpoint /ask.

- Điều gì xảy ra nếu sai key?
Trả về lỗi 401 Unauthorized.

- Làm sao rotate key?
Đổi giá trị biến môi trường AGENT_API_KEY trên môi trường deployment (Railway, Render...). Khi container khởi động lại, nó sẽ tự load key mới.

Test:

```bash
python app.py

#  Không có key
curl http://localhost:8000/ask -X POST \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'

#  Có key
curl http://localhost:8000/ask -X POST \
  -H "X-API-Key: secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello"}'
```

### Exercise 4.2: JWT authentication (Advanced)

```bash
cd ../production
```

**Nhiệm vụ:**

1. Đọc `auth.py` — hiểu JWT flow
2. Lấy token:

```bash
python app.py

curl http://localhost:8000/token -X POST \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "secret"}'
```

1. Dùng token để gọi API:

```bash
TOKEN="<token_từ_bước_2>"
curl http://localhost:8000/ask -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "Explain JWT"}'
```

### Exercise 4.3: Rate limiting

**Nhiệm vụ:** Đọc `rate_limiter.py` và trả lời:

- Algorithm nào được dùng? (Token bucket? Sliding window?)
Token bucket

- Limit là bao nhiêu requests/minute?
60 requests/minute.

- Làm sao bypass limit cho admin?
Trong hàm rate_limit_required, nếu user là admin thì nó return True luôn, không kiểm tra gì hết.

Test:

```bash
# Gọi liên tục 20 lần
for i in {1..20}; do
  curl http://localhost:8000/ask -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"question": "Test '$i'"}'
  echo ""
done
```

Quan sát response khi hit limit.

### Exercise 4.4: Cost guard

**Nhiệm vụ:** Đọc `cost_guard.py` và implement logic:

```python
def check_budget(user_id: str, estimated_cost: float) -> bool:
    """
    Return True nếu còn budget, False nếu vượt.
    
    Logic:
    - Mỗi user có budget $10/tháng
    - Track spending trong Redis
    - Reset đầu tháng
    """
    # TODO: Implement
    pass
```

<details>
<summary> Solution</summary>

```python
import redis
from datetime import datetime

r = redis.Redis()

def check_budget(user_id: str, estimated_cost: float) -> bool:
    month_key = datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"
    
    current = float(r.get(key) or 0)
    if current + estimated_cost > 10:
        return False
    
    r.incrbyfloat(key, estimated_cost)
    r.expire(key, 32 * 24 * 3600)  # 32 days
    return True
```

</details>

### Checkpoint 4

- [ ] Implement API key authentication
- [ ] Hiểu JWT flow
- [ ] Implement rate limiting
- [ ] Implement cost guard với Redis

---

## Part 5: Scaling & Reliability (40 phút)

### Concepts

**Vấn đề:** 1 instance không đủ khi có nhiều users.

**Giải pháp:**

1. **Stateless design** — Không lưu state trong memory
2. **Health checks** — Platform biết khi nào restart
3. **Graceful shutdown** — Hoàn thành requests trước khi tắt
4. **Load balancing** — Phân tán traffic

### Exercise 5.1: Health checks

```bash
cd ../../05-scaling-reliability/develop
```

**Nhiệm vụ:** Implement 2 endpoints:

```python
@app.get("/health")
def health():
    """Liveness probe — container còn sống không?"""
    return {"status": "ok"}

@app.get("/ready")
def ready():
    """Readiness probe — sẵn sàng nhận traffic không?"""
    try:
        # Check Redis
        r.ping()
        # Check database
        db.execute("SELECT 1")
        return {"status": "ready"}
    except:
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=503,
            content={"status": "not ready"}
        )
```

<details>
<summary> Solution</summary>

```python
@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    try:
        # Check Redis
        r.ping()
        # Check database
        db.execute("SELECT 1")
        return {"status": "ready"}
    except:
        return JSONResponse(
            status_code=503,
            content={"status": "not ready"}
        )
```

</details>

### Exercise 5.2: Graceful shutdown

**Nhiệm vụ:** Implement signal handler:

```python
import signal
import sys
import time

def shutdown_handler(signum, frame):
    """Handle SIGTERM from container orchestrator"""
    print("Received SIGTERM! Initiating graceful shutdown...")
    # 1. Stop accepting new requests (uvicorn tự xử lý, ta đánh dấu cờ not ready)
    global is_ready
    is_ready = False
    
    # 2. Finish current requests
    print("Waiting for in-flight requests to finish...")
    time.sleep(2) # Giả lập chờ request đang dở
    
    # 3. Close connections
    print("Closing database and Redis connections...")
    
    # 4. Exit
    print("Shutdown complete.")
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdown_handler)
```

Test:

```bash
python app.py &
PID=$!

# Gửi request
curl http://localhost:8000/ask -X POST \
  -H "Content-Type: application/json" \
  -d '{"question": "Long task"}' &

# Ngay lập tức kill
kill -TERM $PID

# Quan sát: Request có hoàn thành không?
```

### Exercise 5.3: Stateless design

```bash
cd ../production
```

**Nhiệm vụ:** Refactor code để stateless.

**Anti-pattern:**

```python
#  State trong memory
conversation_history = {}

@app.post("/ask")
def ask(user_id: str, question: str):
    history = conversation_history.get(user_id, [])
    # ...
```

**Correct:**

```python
#  State trong Redis
@app.post("/ask")
def ask(user_id: str, question: str):
    history = r.lrange(f"history:{user_id}", 0, -1)
    # ...
```

Tại sao? Vì khi scale ra nhiều instances, mỗi instance có memory riêng.

### Exercise 5.4: Load balancing

**Nhiệm vụ:** Chạy stack với Nginx load balancer:

```bash
docker compose up --scale agent=3
```

Quan sát:

- 3 agent instances được start
- Nginx phân tán requests
- Nếu 1 instance die, traffic chuyển sang instances khác

Test:

```bash
# Gọi 10 requests
for i in {1..10}; do
  curl http://localhost/ask -X POST \
    -H "Content-Type: application/json" \
    -d '{"question": "Request '$i'"}'
done

# Check logs — requests được phân tán
docker compose logs agent
```

### Exercise 5.5: Test stateless

```bash
python test_stateless.py
```

Script này:

1. Gọi API để tạo conversation
2. Kill random instance
3. Gọi tiếp — conversation vẫn còn không?

### Checkpoint 5

- [ ] Implement health và readiness checks
- [ ] Implement graceful shutdown
- [ ] Refactor code thành stateless
- [ ] Hiểu load balancing với Nginx
- [ ] Test stateless design

---

## Part 6: Final Project (60 phút)

### Objective

Build một production-ready AI agent từ đầu, kết hợp TẤT CẢ concepts đã học.

### Requirements

**Functional:**

- [ ] Agent trả lời câu hỏi qua REST API
- [ ] Support conversation history
- [ ] Streaming responses (optional)

**Non-functional:**

- [ ] Dockerized với multi-stage build
- [ ] Config từ environment variables
- [ ] API key authentication
- [ ] Rate limiting (10 req/min per user)
- [ ] Cost guard ($10/month per user)
- [ ] Health check endpoint
- [ ] Readiness check endpoint
- [ ] Graceful shutdown
- [ ] Stateless design (state trong Redis)
- [ ] Structured JSON logging
- [ ] Deploy lên Railway hoặc Render
- [ ] Public URL hoạt động

### 🏗 Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Nginx (LB)     │
└──────┬──────────┘
       │
       ├─────────┬─────────┐
       ▼         ▼         ▼
   ┌──────┐  ┌──────┐  ┌──────┐
   │Agent1│  │Agent2│  │Agent3│
   └───┬──┘  └───┬──┘  └───┬──┘
       │         │         │
       └─────────┴─────────┘
                 │
                 ▼
           ┌──────────┐
           │  Redis   │
           └──────────┘
```

### Step-by-step

#### Step 1: Project setup (5 phút)

```bash
mkdir my-production-agent
cd my-production-agent

# Tạo structure
mkdir -p app
touch app/__init__.py
touch app/main.py
touch app/config.py
touch app/auth.py
touch app/rate_limiter.py
touch app/cost_guard.py
touch Dockerfile
touch docker-compose.yml
touch requirements.txt
touch .env.example
touch .dockerignore
```

#### Step 2: Config management (10 phút)

**File:** `app/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    environment: str = "development"
    debug: bool = False
    app_name: str = "Production AI Agent"
    app_version: str = "1.0.0"
    openai_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    agent_api_key: str = "dev-key-change-me"
    allowed_origins: list = ["*"]
    rate_limit_per_minute: int = 20
    daily_budget_usd: float = 5.0
    redis_url: str = ""

settings = Settings()
```

#### Step 3: Main application (15 phút)

**File:** `app/main.py`

```python
from fastapi import FastAPI, Depends, HTTPException
from .config import settings
from .auth import verify_api_key
from .rate_limiter import check_rate_limit
from .cost_guard import check_budget

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok", "version": settings.app_version}

@app.get("/ready")
def ready():
    if not getattr(app.state, "is_ready", True):
        raise HTTPException(503, "Not ready")
    return {"ready": True}

@app.post("/ask")
def ask(
    question: str,
    user_id: str = Depends(verify_api_key),
    _rate_limit: None = Depends(check_rate_limit),
    _budget: None = Depends(check_budget)
):
    # Lấy câu trả lời (Mock LLM)
    answer = llm_ask(question)
    
    return {
        "question": question,
        "answer": answer,
        "model": settings.llm_model,
        "user_id": user_id
    }
```

#### Step 4: Authentication (5 phút)

**File:** `app/auth.py`

```python
from fastapi import Header, HTTPException

def verify_api_key(x_api_key: str = Header(...)):
    if not x_api_key or x_api_key != settings.agent_api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key. Include header: X-API-Key: <key>",
        )
    return x_api_key
```

#### Step 5: Rate limiting (10 phút)

**File:** `app/rate_limiter.py`

```python
import redis
from fastapi import HTTPException

r = redis.from_url(settings.REDIS_URL)

def check_rate_limit(user_id: str):
    now = time.time()
    window = _rate_windows[user_id]
    while window and window[0] < now - 60:
        window.popleft()
    if len(window) >= settings.rate_limit_per_minute:
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded: {settings.rate_limit_per_minute} req/min",
            headers={"Retry-After": "60"},
        )
    window.append(now)
```

#### Step 6: Cost guard (10 phút)

**File:** `app/cost_guard.py`

```python
def check_budget(user_id: str):
    if getattr(app.state, "daily_cost", 0) >= settings.daily_budget_usd:
        raise HTTPException(
            status_code=402, 
            detail="Daily budget exhausted. Try tomorrow."
        )
```

#### Step 7: Dockerfile (5 phút)

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim AS runtime
RUN groupadd -r agent && useradd -r -g agent -d /app agent
WORKDIR /app
COPY --from=builder /root/.local /home/agent/.local
COPY app/ ./app/
COPY utils/ ./utils/
RUN chown -R agent:agent /app
USER agent
ENV PATH=/home/agent/.local/bin:$PATH
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Step 8: Docker Compose (5 phút)

```yaml
  agent:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=staging
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      redis:
        condition: service_healthy

  redis:
    image: redis:7-alpine
    command: redis-server --maxmemory 128mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
```

#### Step 9: Test locally (5 phút)

```bash
docker compose up --scale agent=3

# Test all endpoints
curl http://localhost/health
curl http://localhost/ready
curl -H "X-API-Key: secret" http://localhost/ask -X POST \
  -H "Content-Type: application/json" \
  -d '{"question": "Hello", "user_id": "user1"}'
```

#### Step 10: Deploy (10 phút)

```bash
# Railway
railway init
railway variables set REDIS_URL=...
railway variables set AGENT_API_KEY=...
railway up

# Hoặc Render
# Push lên GitHub → Connect Render → Deploy
```

### Validation

Chạy script kiểm tra:

```bash
cd 06-lab-complete
python check_production_ready.py
```

Script sẽ kiểm tra:

- Dockerfile exists và valid
- Multi-stage build
- .dockerignore exists
- Health endpoint returns 200
- Readiness endpoint returns 200
- Auth required (401 without key)
- Rate limiting works (429 after limit)
- Cost guard works (402 when exceeded)
- Graceful shutdown (SIGTERM handled)
- Stateless (state trong Redis, không trong memory)
- Structured logging (JSON format)

### Grading Rubric

| Criteria | Points | Description |
|----------|--------|-------------|
| **Functionality** | 20 | Agent hoạt động đúng |
| **Docker** | 15 | Multi-stage, optimized |
| **Security** | 20 | Auth + rate limit + cost guard |
| **Reliability** | 20 | Health checks + graceful shutdown |
| **Scalability** | 15 | Stateless + load balanced |
| **Deployment** | 10 | Public URL hoạt động |
| **Total** | 100 | |

---

## Hoàn Thành

Bạn đã:

- Hiểu sự khác biệt dev vs production
- Containerize app với Docker
- Deploy lên cloud platform
- Bảo mật API
- Thiết kế hệ thống scalable và reliable

### Next Steps

1. **Monitoring:** Thêm Prometheus + Grafana
2. **CI/CD:** GitHub Actions auto-deploy
3. **Advanced scaling:** Kubernetes
4. **Observability:** Distributed tracing với OpenTelemetry
5. **Cost optimization:** Spot instances, auto-scaling

### Resources

- [12-Factor App](https://12factor.net/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Railway Docs](https://docs.railway.app/)
- [Render Docs](https://render.com/docs)

---

## Q&A

**Q: Tôi không có credit card, có thể deploy không?**  
A: Có! Railway cho $5 credit, Render có 750h free tier.

**Q: Mock LLM khác gì với OpenAI thật?**  
A: Mock trả về canned responses, không gọi API. Để dùng OpenAI thật, set `OPENAI_API_KEY` trong env.

**Q: Làm sao debug khi container fail?**  
A: `docker logs <container_id>` hoặc `docker exec -it <container_id> /bin/sh`

**Q: Redis data mất khi restart?**  
A: Dùng volume: `volumes: - redis-data:/data` trong docker-compose.

**Q: Làm sao scale trên Railway/Render?**  
A: Railway: `railway scale <replicas>`. Render: Dashboard → Settings → Instances.

---

**Happy Deploying!**
