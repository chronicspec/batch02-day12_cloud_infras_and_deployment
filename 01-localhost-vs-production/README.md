# Section 1 — Từ Localhost Đến Production

## Mục tiêu học

- Hiểu tại sao "it works on my machine" là vấn đề
- Nhận ra sự khác biệt giữa dev và production environment
- Áp dụng 4 nguyên tắc 12-factor cơ bản

---

## Ví dụ Basic — Agent "Kiểu Localhost"

```
develop/
├── app.py          # ❌ Anti-patterns: hardcode secrets, no config, no health check
├── .env.example
└── requirements.txt
```

### Chạy thử

```bash
cd basic
pip install -r requirements.txt
python app.py
# Truy cập: http://localhost:8000
```

### Những vấn đề trong code này

1. API key hardcode trong code
OPENAI_API_KEY và DATABASE_URL được viết trực tiếp vào code. Nếu code này bị đẩy lên GitHub, kẻ gian sẽ thấy được key và có thể xài lén gây thiệt hại về tài chính.
2. Không có health check endpoint
Các biến cấu hình như DEBUG = True, MAX_TOKENS = 500 không được lấy từ file .env hay biến môi trường. Mỗi khi muốn đổi, ta lại phải sửa code và deploy lại.
3. Debug mode bật cứng
Việc dùng print() thay vì thư viện logging chuyên nghiệp không tiện cho việc tìm lỗi sau này. Tệ hơn, dòng print(f"[DEBUG] Using key: {OPENAI_API_KEY}") in thẳng Secret Key ra file log.
4. Không xử lý SIGTERM gracefully
Không có các đường dẫn như /health hay /ready. Nếu ứng dụng bị treo, nền tảng Cloud (như Render, Railway, Kubernetes) sẽ không biết để tự động khởi động lại (restart) ứng dụng.
5. Config không đến từ environment
Code gán cứng host="localhost" và port=8000. Khi đóng gói bằng Docker hoặc đưa lên Cloud, ứng dụng thường phải lắng nghe ở IP 0.0.0.0 và cổng do Cloud tự động cấp (thông qua biến môi trường PORT), nếu gán cứng như vậy ứng dụng sẽ không nhận được traffic từ bên ngoài.

---

## Ví dụ Advanced — 12-Factor Compliant Agent

```
production/
├── app.py          # ✅ Clean: config from env, health check, graceful shutdown
├── config.py       # ✅ Centralized config management
├── .env.example    # ✅ Template — không commit .env thật
└── requirements.txt
```

### Chạy thử

```bash
cd advanced
pip install -r requirements.txt
cp .env.example .env
# Sửa .env nếu cần
python app.py
```

### So sánh với Basic

| | Basic (❌) | Advanced (✅) |
|--|-----------|--------------|
| Config | Hardcode trong code | Đọc từ env vars |
| Secrets | `api_key = "sk-abc123"` | `os.getenv("OPENAI_API_KEY")` |
| Port | Cố định `8000` | Từ `PORT` env var |
| Health check | Không có | `GET /health` |
| Shutdown | Tắt đột ngột | Graceful — hoàn thành request hiện tại |
| Logging | `print()` | Structured JSON logging |

---

## Câu hỏi thảo luận

1. Điều gì xảy ra nếu bạn push code với API key hardcode lên GitHub public?
OPENAI_API_KEY và DATABASE_URL được viết trực tiếp vào code. Nếu code này bị đẩy lên GitHub, kẻ gian sẽ thấy được key và có thể xài lén gây thiệt hại về tài chính.
2. Tại sao stateless quan trọng khi scale?
Khi tăng số lượng instances (scale out), mỗi instance phải độc lập và không phụ thuộc vào dữ liệu lưu trên local disk hoặc RAM của instance đó.
3. 12-factor nói "dev/prod parity" — nghĩa là gì trong thực tế?
Dev/prod parity (sự tương đồng giữa môi trường phát triển và production) là việc đảm bảo rằng môi trường nơi code được phát triển (dev) giống nhất có thể với môi trường nơi code được triển khai (production).
