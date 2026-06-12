# Public POI Source Mapping

## Coordinate Source
- Tọa độ `lat/lng` hiện tại đã được đồng bộ thêm từ Google Sheet do user cung cấp, trong đó các nhãn địa điểm/phân khu chủ yếu ở **tiếng Việt** và được map lại sang các `facility.id` / `zone_id` **tiếng Anh** trong codebase.
- Với các POI không trùng tên 1:1, prototype dùng mapping bảo toàn contract hiện tại (ví dụ `harbor_corner`, `water_world`, `indoor_games`) nhưng lấy vị trí theo nhãn thực địa gần nhất trong sheet.
- Sau vòng review toàn bộ, các POI có đối sánh exact nhưng trước đó lệch zone logic đã được chỉnh đồng bộ lại, nổi bật là:
  - `Riverine Restaurant` → `adventure_land` (theo vị trí `Nhà hàng Riverrine` trong `Vùng Đất Phiêu Lưu`)
  - `Yummy Land` → `water_world` (theo vị trí `Nhà hàng Yummy Land` trong `Thế Giới Nước`)

Dữ liệu địa điểm (POI) trong prototype này được map từ các nguồn public của VinWonders Nam Hội An nhằm đảm bảo tính chân thực (bước chuẩn bị chuyển sang data thật hoàn toàn). Dưới đây là bảng trace nguồn gốc:

## Restaurants & Dining
- **Riverine Restaurant**: Có trong danh sách nhà hàng buffet/alacarte dọc bờ sông trên web Vinpearl.
- **Cocoon Restaurant**: Thuộc khu Food Court/Indoor, có đề cập trong review/website.
- **Deliland Restaurant**: Nhà hàng lớn ở Harbor Corner mô phỏng con tàu, công bố trên sơ đồ tiện ích.
- **Cho Que Restaurant** (Chợ Quê): Khu văn hóa ẩm thực đặc trưng tại Đảo Văn Hóa Dân Gian, có trên web chính thức.
- **Chingu BBQ**: Quán nướng Hàn Quốc, định vị trong khu Indoor Games / Phố Châu Âu.
- **An Restaurant**: Nguồn từ các blog ẩm thực và danh sách nhà hàng VinWonders.
- **Little Tokyo**: Quầy ẩm thực Nhật, thường có trong các banner quảng cáo/cẩm nang vui chơi VinWonders.
- **Yummy Land**: Khu Food Court tiện lợi/đồ ăn nhanh.
- **3S Food & Drink**: Quầy giải khát và ăn nhẹ gần Adventure Land, có trên bản đồ chi tiết.
- **D'Art Chocolate**: Điểm mua chocolate và đồ ngọt, nằm phía đầu Harbor Corner.

## Public Services (Utilities)
- **Water World Restroom Hub**: Cụm nhà vệ sinh trung tâm (thực tế hiển thị biểu tượng WC tại cổng Công viên nước trên map).
- **Indoor Games Restroom**: Biểu tượng WC bên trong khối nhà trung tâm.
- **River Safari Restroom**: WC công cộng tại bến chờ thuyền River Safari.
- **Harbor Corner Medical Station**: Phòng y tế (First Aid) gần khu cổng chính.
- **Water World First Aid Desk**: Điểm hỗ trợ y tế sơ cứu bên trong Water World.
- **River Safari Shade Rest Area** & **Harbor Corner Bench Garden**: Các khu vực ghế băng có mái che (được ước lượng và định danh dựa trên không gian xanh của bản đồ).
- **Water World Locker House**: Khu vực gửi đồ thật tại cổng Water World (khách tắm cần gửi đồ).
- **Harbor Gate Locker Point**: Dịch vụ giữ hành lý tại cổng chính.
- **Indoor Games Water Refill Station** & **Adventure Land Hydration Point**: Ước lượng dịch vụ nước uống công cộng (vòi nước uống) thường được bố trí ở khu vui chơi / trong nhà theo tiêu chuẩn công viên.

## Mở rộng (Extended Support)
- **Riveria Souvenir**: Tên mượn cho hệ thống cửa hàng lưu niệm (thường là VinWonders Souvenir shop tại cổng/River Safari).
- **Harbor Corner Lost & Found Desk**: Quầy thất lạc hành lý tại khu vực hỗ trợ khách hàng cổng chính.
- **Main Gate Ticket Support Counter**: Quầy tư vấn và hỗ trợ vé cổng giao thoa.

> **Lưu ý**: Các thông số vận hành (`distance_map`, `walk_time_map`, `crowd_level`, `wait_time_min`) hiện đang sử dụng **giả lập có kiểm soát (ops-estimated)** để đảm bảo behavior của prototype ổn định. Khi có file GIS/Ops thật, các file data JSON có thể hot-swap ngay lập tức.
