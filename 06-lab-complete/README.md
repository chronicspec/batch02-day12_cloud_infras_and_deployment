# VinWonders AI Assistant Prototype

Prototype AI Assistant giúp khách trong VinWonders tìm facility gần nhất theo flow deterministic:

- Rule engine chạy trước
- LLM 1 chỉ extract intent JSON
- Backend filter + rank quyết định kết quả
- LLM 2 chỉ diễn đạt lại từ dữ liệu đã xác thực

## Scope đã hoàn thành

- FastAPI backend
- Streamlit demo UI
- Public VinWonders Nam Hội An JSON data load in-memory
- Deterministic chat orchestration
- 4 response paths:
  - success
  - clarification
  - fallback
  - fast_track
- Session memory ngắn hạn cho correction path
- Test skeleton cho 5 scenario chính

## Project structure

```text
prototype_ai_assistant/
  app/
    main.py
    config.py
    api/
    schemas/
    services/
    engines/
    adapters/
    prompts/
    data/
    utils/
  web/ (React + Vite)
    
  tests/
  requirements.txt
  .env.example
  README.md
```

## Main API

### 1. Health

```http
GET /api/v1/health
```

### 2. Facilities debug

```http
GET /api/v1/facilities
GET /api/v1/facilities?facility_type=restaurant
GET /api/v1/facilities?zone_id=water_world
```

### 3. Chat

```http
POST /api/v1/chat
Content-Type: application/json
```

Example request:

```json
{
  "session_id": "sess_001",
  "message": "Có nhà hàng nào gần đây cho trẻ em không?",
  "current_zone": "water_world",
  "language": "vi",
  "user_context": {
    "has_child": true
  }
}
```

## Response modes

### success
- Có kết quả tốt nhất rõ ràng

### clarification
- Có kết quả nhưng xa hơn ngưỡng low-confidence
- Hoặc request ngoài scope / cần hỏi lại

### fallback
- Không có kết quả khớp hoàn toàn
- Trả 3 điểm gần nhất để user chọn

### fast_track
- Emergency keyword match mạnh
- Bỏ qua intent extraction và đi thẳng first-aid

## Scenarios đang support

- Happy path:
  - `Có nhà hàng nào gần đây cho trẻ em không?`
- Low-confidence path:
  - `Tìm nhà hàng chay gần đây`
- Failure path:
  - `Tìm quán lẩu băng chuyền Hàn Quốc ít cay có khu chơi trẻ em`
- Correction path:
  - `Tìm nhà hàng gần đây` → `đổi sang món cho trẻ em`
- Emergency path:
  - `Bé bị đứt tay cần sơ cứu`

## Setup

```bash
cd prototype_ai_assistant
py -3 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run FastAPI

```bash
uvicorn app.main:app --reload
```

Swagger:
- <http://127.0.0.1:8000/docs>

## Run Streamlit demo

```bash
streamlit run web/ (React + Vite)
```

Optional env for UI:

```bash
set API_BASE_URL=http://127.0.0.1:8000/api/v1
```

## Optional LLM setup

Adapter hiện hỗ trợ:
- OpenAI-compatible `chat/completions` API
- Gemini native `generateContent` API

Ví dụ `.env`:

```env
LLM_ENABLED=true
LLM_PROVIDER=gemini
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta
LLM_INTENT_MODEL=gemini-3-flash-preview
LLM_RESPONSE_MODEL=gemini-3-flash-preview
```

Ghi chú:
- Không cấu hình LLM cũng không làm hỏng flow.
- Khi LLM lỗi hoặc timeout, hệ thống tự fallback về heuristic/template deterministic.
- Backend vẫn là nơi quyết định `selected_facility` cuối cùng.
- Với Gemini, nên dùng đúng model id mà key đang được cấp quyền, ví dụ `gemini-3-flash-preview`.

## Run tests

```bash
pytest tests -v
```

Test files:
- `tests/test_chat_happy.py`
- `tests/test_chat_low_confidence.py`
- `tests/test_chat_failure.py`
- `tests/test_chat_correction.py`
- `tests/test_rule_engine.py`

## Important implementation notes

### Deterministic backend control
- Facility selection không nằm trong prompt
- Prompt không quyết định ranking
- Backend là nơi chốt selected facility cuối cùng

### Rule engine before LLM
- emergency detection
- toilet detection
- out-of-scope check
- basic prompt injection guard
- input normalization

### Intent extraction fallback
- thử LLM parse JSON tối đa 2 lần
- fail thì fallback heuristic

### Response generation fallback
- `ResponseService` luôn có fallback template
- Nếu LLM 2 fail, API vẫn trả được response đầy đủ

## Data source notes

Dataset hiện đã chuyển từ mock thuần sang dữ liệu public map/service của **VinWonders Nam Hội An**:
- zone dùng theo các phân khu thật: `harbor_corner`, `folk_culture_island`, `river_safari`, `adventure_land`, `water_world`, `indoor_games`
- restaurant dùng tên địa điểm public như: `Riverine Restaurant`, `Cocoon Restaurant`, `Deliland Restaurant`, `Cho Que Restaurant`, `Chingu BBQ`, `An Restaurant`, `Little Tokyo`, `Yummy Land`, `3S Food & Drink`, `D'Art Chocolate`
- các service point như toilet / first-aid / locker / refill / rest area được map theo vị trí công khai trên park map và mô tả vận hành public

Assumption có chủ đích để app vẫn chạy deterministic:
- `distance_map`, `walk_time_map`, `crowd_level`, `wait_time_min` chưa có feed realtime từ VinWonders nên đang là dữ liệu vận hành giả lập bám theo layout thật
- nếu sau này có file map/GIS/internal ops sheet, có thể thay trực tiếp mà không đổi service logic

## Current limitations

- chưa có realtime feed cho khoảng cách động, crowd và wait time
- tests chưa chạy được nếu môi trường chưa cài dependency
- UI tập trung demo flow, chưa tối ưu giao diện production
- Session store đang là in-memory

## Suggested next step nếu muốn nâng tiếp

- nối LLM thật vào `LLMAdapter`
- thêm metrics/logging
- bổ sung test coverage cho API route level
- refine constraint extraction cho correction và search phrases
