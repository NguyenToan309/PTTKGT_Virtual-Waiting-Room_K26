from collections import deque
import time

class FIFOVirtualWaitingRoom:
    def __init__(self, capacity_dict):
        """
        Khởi tạo Phòng chờ ảo FIFO
        capacity_dict: Từ điển lưu sức chứa từng khu vực, ví dụ {'VIP1': 100, 'A01': 300}
        """
        self.queue = deque()  
        self.capacity = capacity_dict.copy()
        self.successful_tx = []
        self.failed_tx = []

    def enqueue(self, user_request):
        """Thêm người dùng vào cuối hàng đợi - Độ phức tạp O(1)"""
        self.queue.append(user_request)

    def process_queue(self):
        """Xử lý cấp vé lần lượt theo đúng thứ tự đến trước - Độ phức tạp O(1) cho mỗi lượt"""
        while self.queue:
            req = self.queue.popleft()  
            
            zone = req["zone_id"]
            qty = req["requested_seats"]
            
            if self.capacity.get(zone, 0) >= qty:
                
                self.capacity[zone] -= qty
                req["status"] = "SUCCESS"
                req["processed_at"] = time.time()
                self.successful_tx.append(req)
            else:
                
                req["status"] = "FAILED_SOLD_OUT"
                self.failed_tx.append(req)
                
        return self.successful_tx, self.failed_tx, self.capacity


if __name__ == "__main__":
    
    seats_capacity = {"VIP1": 2, "A01": 5}
    vwr = FIFOVirtualWaitingRoom(seats_capacity)

    
    vwr.enqueue({"user_id": "USR_001", "zone_id": "VIP1", "requested_seats": 2})
    vwr.enqueue({"user_id": "USR_002", "zone_id": "VIP1", "requested_seats": 1}) # Sẽ hết vé
    vwr.enqueue({"user_id": "USR_003", "zone_id": "A01", "requested_seats": 3})

   
    success, failed, remaining_seats = vwr.process_queue()

    print("=== KẾT QUẢ XỬ LÝ FIFO QUEUE ===")
    print(f"✅ Thành công ({len(success)}):", [u["user_id"] for u in success])
    print(f"❌ Thất bại ({len(failed)}):", [u["user_id"] for u in failed])
    print("🎫 Kho vé còn lại:", remaining_seats)
