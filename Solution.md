# Day 12 Lab - Mission Answers

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found
1. **API Key bị Hardcode**: `OPENAI_API_KEY` và `DATABASE_URL` được viết trực tiếp vào code. Nếu code này bị đẩy lên GitHub, kẻ gian sẽ thấy được key và có thể xài lén gây thiệt hại về tài chính.
2. **Hardcode Cấu Hình (Config)**: Các biến cấu hình như `DEBUG = True`, `MAX_TOKENS = 500` không được lấy từ file `.env` hay biến môi trường. Mỗi khi muốn đổi, ta lại phải sửa code và deploy lại.
3. **Print log bừa bãi và làm lộ Secret**: Việc dùng `print()` thay vì thư viện logging chuyên nghiệp không tiện cho việc tìm lỗi sau này. Tệ hơn, dòng `print(f"[DEBUG] Using key: {OPENAI_API_KEY}")` in thẳng Secret Key ra file log.
4. **Không có Health Check endpoint**: Không có các đường dẫn như `/health` hay `/ready`. Nếu ứng dụng bị treo, nền tảng Cloud sẽ không biết để tự động khởi động lại.
5. **Cố định Port và Host**: Code gán cứng `host="localhost"` và `port=8000`. Khi đóng gói bằng Docker hoặc đưa lên Cloud, ứng dụng thường phải lắng nghe ở IP `0.0.0.0` và cổng do Cloud tự động cấp.

### Exercise 1.3: Comparison table
| Feature | Develop | Production | Tại sao quan trọng? |
|---------|---------|------------|---------------------|
| Config  | Hardcode | Env vars | Giữ bí mật an toàn (không lộ lên Git), thay đổi linh hoạt mà không cần sửa code. |
| Health check | Không có | Có `/health` và `/ready` | Giúp Cloud/Load Balancer biết khi nào app treo để tự khởi động lại, và khi nào sẵn sàng nhận request. |
| Logging | `print()` | JSON | Dễ dàng đưa vào các hệ thống phân tích log lớn, dễ filter lỗi, và không in ra secret. |
| Shutdown | Đột ngột | Graceful | Cho phép các request đang xử lý dở được chạy cho xong rồi mới tắt hẳn, giúp người dùng không bị văng lỗi. |
| Network Binding | `localhost:8000` | `0.0.0.0` và dùng biến `PORT` | Ứng dụng mới có thể giao tiếp được ra bên ngoài khi nằm trong Docker Container hoặc chạy trên Cloud. |

## Part 2: Docker Containerization

### Exercise 2.1: Dockerfile cơ bản
1. **Base image là gì?** Là `python:3.11`. Đây là bản phân phối đầy đủ của Python, chứa rất nhiều công cụ đi kèm nên dung lượng khá nặng (~1GB).
2. **Working directory là gì?** Là thư mục `/app` trong Container.
3. **Tại sao COPY requirements.txt trước?** Để tận dụng Docker layer caching. Giúp build image rất nhanh khi không thay đổi dependencies.
4. **CMD vs ENTRYPOINT khác nhau thế nào?** `CMD` là lệnh mặc định dễ bị ghi đè. `ENTRYPOINT` biến container thành một file thực thi cố định, tham số sau `docker run` sẽ được truyền vào `ENTRYPOINT`.

### Exercise 2.3: Image size comparison
- Develop: `1.66GB`
- Production (Multi-stage): `< 500MB`
- Giải thích: Stage 2 đã bỏ lại toàn bộ rác, cache từ hệ điều hành và các công cụ compile. File image cuối cùng rất sạch, gọn nhẹ và bảo mật hơn vì không chạy quyền root.

### Exercise 2.4: Docker Compose stack
Có 3 service chính: Frontend (chạy React), Backend (API), và Database (PostgreSQL).
- Frontend giao tiếp với Backend qua cổng 8000.
- Frontend giao tiếp với PostgreSQL qua cổng 5432.
- Backend giao tiếp với PostgreSQL qua cổng 5432.

## Part 3: Cloud Deployment

### Exercise 3.2: Deploy Render vs Railway
`render.yaml` sử dụng cấu hình YAML thuần túy cho từng service riêng biệt, còn `railway.toml` dùng cấu trúc "mở rộng" (extensible) với các trường như services, templates, và pipelines. `render.yaml` có cấu trúc đơn giản, dễ đọc, phù hợp với các dự án nhỏ và vừa.

## Part 4: API Security

### Exercise 4.1: API Key authentication
- **API key được check ở đâu?** Tại `api_key_required` (decorator định nghĩa trong `security.py`), hoạt động như middleware kiểm tra header `X-API-Key` với `AGENT_API_KEY`.
- **Điều gì xảy ra nếu sai key?** Trả về lỗi `401 Unauthorized`.
- **Làm sao rotate key?** Đổi giá trị biến môi trường `AGENT_API_KEY` trên môi trường deployment.

### Exercise 4.3: Rate limiting
- **Algorithm nào được dùng?** Token bucket / Sliding window.
- **Limit là bao nhiêu requests/minute?** 60 requests/minute.
- **Làm sao bypass limit cho admin?** Trong hàm `rate_limit_required`, nếu user là admin thì nó return `True` luôn, không kiểm tra gì hết.

## Part 5: Scaling & Reliability
Tất cả các cơ chế (Health check, Readiness check, Graceful Shutdown, Stateless với Redis) đã được ứng dụng trực tiếp vào dự án cuối cùng ở mục `06-lab-complete`.
