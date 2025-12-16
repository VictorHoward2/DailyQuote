# Daily Quote - Ứng dụng hiển thị câu nói hay

Ứng dụng desktop nhỏ gọn để hiển thị các câu nói hay, nhắc nhở bản thân mỗi ngày.

## Tính năng

- ✅ Hiển thị một câu nói tại một thời điểm
- ✅ Tự động chuyển sang câu nói tiếp theo sau khoảng thời gian cài đặt
- ✅ Lưu trữ dữ liệu cục bộ (file JSON) - dữ liệu được giữ lại sau khi đóng app
- ✅ Giao diện nhỏ gọn, không chiếm nhiều diện tích màn hình
- ✅ Tích hợp vào system tray (thanh taskbar) với đầy đủ tính năng
- ✅ Quản lý câu nói: thêm, sửa, xóa
- ✅ Cài đặt thời gian hiển thị (5 giây - 1 giờ)
- ✅ Có thể thay đổi kích thước cửa sổ
- ✅ Ẩn/hiện thanh điều khiển để giao diện gọn gàng hơn
- ✅ Phím tắt để điều khiển nhanh

## Cài đặt

1. Cài đặt Python 3.7 trở lên

2. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

## Sử dụng

1. Chạy ứng dụng:
```bash
python main.py
```

2. Ứng dụng sẽ hiển thị một cửa sổ nhỏ với câu nói đầu tiên.

3. Các nút điều khiển:
   - **◀ Trước**: Chuyển về câu nói trước đó
   - **Tiếp ▶**: Chuyển sang câu nói tiếp theo
   - **⚙ Cài đặt**: Mở cửa sổ quản lý câu nói và cài đặt
   - **▼ Thu nhỏ**: Thu nhỏ vào system tray

4. System Tray (Thanh taskbar):
   - **Click vào icon**: Toggle hiển thị/ẩn cửa sổ
   - **Hover vào icon**: Xem tooltip với câu nói hiện tại
   - **Click chuột phải vào icon**: Mở menu với các tùy chọn:
     - **Hiển thị quote hiện tại**: Hiển thị notification với câu nói hiện tại
     - **Câu tiếp theo**: Chuyển sang câu nói tiếp theo (kèm notification nếu cửa sổ đang ẩn)
     - **Câu trước**: Chuyển về câu nói trước đó (kèm notification nếu cửa sổ đang ẩn)
     - **Hiển thị cửa sổ**: Mở lại cửa sổ ứng dụng
     - **Thoát**: Đóng ứng dụng hoàn toàn

5. Trong cửa sổ Cài đặt:
   - **Tab Quản lý Quotes**: Thêm, sửa, xóa câu nói
   - **Tab Cài đặt thời gian**: 
     - Đặt thời gian hiển thị mỗi câu (5-3600 giây)
     - Bật/tắt tự động chuyển câu nói
     - Ẩn/hiện thanh điều khiển
     - Xem danh sách phím tắt

6. **Phím tắt**:
   - **Space** hoặc **→** : Chuyển sang câu tiếp theo
   - **←** : Chuyển về câu trước
   - **H** : Ẩn/hiện thanh điều khiển
   - **S** : Mở cửa sổ cài đặt
   - **Escape** : Thu nhỏ vào system tray

## Dữ liệu

Dữ liệu được lưu trong file `quotes_data.json` trong cùng thư mục với ứng dụng. File này chứa:
- Danh sách các câu nói
- Thời gian hiển thị
- Vị trí câu nói hiện tại

## Ghi chú

- Cửa sổ luôn hiển thị ở trên cùng để dễ dàng nhìn thấy
- Bạn có thể di chuyển và thay đổi kích thước cửa sổ đến bất kỳ vị trí nào trên màn hình
- Khi đóng cửa sổ hoặc click "Thu nhỏ", ứng dụng sẽ chạy ngầm trong system tray
- Tooltip của icon tray sẽ tự động cập nhật khi chuyển câu nói
- Bạn có thể điều khiển ứng dụng hoàn toàn từ system tray mà không cần mở cửa sổ
- Khi ẩn thanh điều khiển, bạn vẫn có thể sử dụng phím tắt để điều khiển
- Phím tắt hoạt động ngay cả khi cửa sổ không được focus (chỉ cần cửa sổ đang hiển thị)

