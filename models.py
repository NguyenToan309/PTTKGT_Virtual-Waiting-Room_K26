"""
models.py - Cấu trúc dữ liệu chuẩn cho Hệ thống Virtual Waiting Room & Overbooking.
Nghiệp vụ: Đại nhạc hội Quốc gia 2026 - Tri ân người có công với cách mạng.
Tuân thủ quy chuẩn: R2.4 trong AGENTS.md và Master Prompt v2.0.
"""

from dataclasses import dataclass, field
from typing import Any, Dict

# Danh mục diện đối tượng ưu tiên quốc gia và điểm ưu tiên tương ứng
PRIORITY_GROUPS: Dict[str, Dict[str, Any]] = {
    "ME_VNAH": {
        "name": "Bà mẹ Việt Nam Anh hùng",
        "score": 100,
        "badge": "⭐ Mẹ VNAH",
        "color": "#D4AF37",  # Vàng hoàng gia
        "protected": True,   # Miễn trừ 100% Denied Boarding
    },
    "ANH_HUNG_LLVT": {
        "name": "Anh hùng LLVT / Thân nhân Liệt sĩ",
        "score": 90,
        "badge": "🎖️ Anh hùng LLVT",
        "color": "#FF4D4D",  # Đỏ tươi vinh danh
        "protected": True,
    },
    "THUONG_BINH": {
        "name": "Thương binh / Bệnh binh",
        "score": 80,
        "badge": "🎗️ Thương binh",
        "color": "#FF8C00",  # Cam đậm
        "protected": True,
    },
    "CUU_CHIEN_BINH": {
        "name": "Cựu chiến binh / Cựu TNXP",
        "score": 70,
        "badge": "🎖️ Cựu chiến binh",
        "color": "#2E8B57",  # Xanh quân đội
        "protected": True,
    },
    "THANH_NIEN_XUNG_PHONG": {
        "name": "Đoàn viên / Thanh niên tiêu biểu",
        "score": 50,
        "badge": "⭐ Thanh niên tiêu biểu",
        "color": "#1E90FF",  # Xanh thanh niên
        "protected": False,
    },
    "PHO_THONG": {
        "name": "Khán giả / Nhân dân",
        "score": 10,
        "badge": "👥 Khán giả nhân dân",
        "color": "#A0AEC0",  # Bạc xám
        "protected": False,
    },
}


@dataclass
class User:
    """
    Thông tin người dùng trong phòng chờ ảo.
    user_id: Mã định danh người dùng.
    arrival_time: Thời điểm truy cập vào phòng chờ (giây / tick).
    loyalty_score: Điểm ưu tiên (tự động tính từ priority_group hoặc tùy chỉnh).
    ticket_type: Hạng vé mong muốn ('VVIP', 'PLATINUM', 'GOLD', 'SILVER').
    status: Trạng thái ('WAITING', 'SUCCESS', 'UPGRADED', 'REJECTED').
    full_name: Họ và tên đầy đủ.
    citizen_id: Số Căn cước công dân / Định danh.
    priority_group: Mã diện đối tượng ưu tiên ('ME_VNAH', 'THUONG_BINH',...).
    seat_number: Số ghế phân bổ (nếu có).
    """
    user_id: int
    arrival_time: int
    loyalty_score: int = 10
    ticket_type: str = "GOLD"
    status: str = "WAITING"
    full_name: str = ""
    citizen_id: str = ""
    priority_group: str = "PHO_THONG"
    seat_number: str = ""

    def __post_init__(self) -> None:
        if self.priority_group in PRIORITY_GROUPS and self.loyalty_score == 10:
            self.loyalty_score = PRIORITY_GROUPS[self.priority_group]["score"]

    @property
    def badge(self) -> str:
        """Huy hiệu danh dự hiển thị trên UI."""
        return PRIORITY_GROUPS.get(self.priority_group, {}).get("badge", "👥 Khán giả")

    @property
    def group_name(self) -> str:
        """Tên diện đối tượng tiếng Việt."""
        return PRIORITY_GROUPS.get(self.priority_group, {}).get("name", "Khán giả nhân dân")

    @property
    def is_protected(self) -> bool:
        """Khách thuộc nhóm chính sách bảo vệ tuyệt đối khỏi Denied Boarding."""
        return PRIORITY_GROUPS.get(self.priority_group, {}).get("protected", False)

    def to_dict(self) -> Dict[str, Any]:
        """Chuyển đổi sang dict để tương thích toàn bộ hệ thống và JSON API."""
        return {
            "user_id": self.user_id,
            "id_khach": self.user_id,
            "arrival_time": self.arrival_time,
            "loyalty_score": self.loyalty_score,
            "diem_loyalty": self.loyalty_score,
            "ticket_type": self.ticket_type,
            "hang_ve_mong_muon": self.ticket_type,
            "status": self.status,
            "seat_number": self.seat_number,
            "full_name": self.full_name or f"Khán giả #{self.user_id}",
            "ten": self.full_name or f"Khán giả #{self.user_id}",
            "citizen_id": self.citizen_id or f"001202{self.user_id:06d}",
            "priority_group": self.priority_group,
            "badge": self.badge,
            "group_name": self.group_name,
            "is_protected": self.is_protected,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Tạo đối tượng User từ dict."""
        return cls(
            user_id=int(data.get("user_id") or data.get("id_khach", 0)),
            arrival_time=int(data.get("arrival_time", 0)),
            loyalty_score=int(data.get("loyalty_score") or data.get("diem_loyalty", 10)),
            ticket_type=str(data.get("ticket_type") or data.get("hang_ve_mong_muon", "GOLD")),
            status=str(data.get("status", "WAITING")),
            full_name=str(data.get("full_name") or data.get("ten", "")),
            citizen_id=str(data.get("citizen_id", "")),
            priority_group=str(data.get("priority_group", "PHO_THONG")),
            seat_number=str(data.get("seat_number", "")),
        )


@dataclass
class Ticket:
    """
    Thông tin vé concert trong hệ thống.
    ticket_id: Mã định danh vé.
    ticket_type: Hạng vé ('VVIP', 'PLATINUM', 'GOLD', 'SILVER').
    price: Đơn giá vé (VNĐ).
    expire_time: Thời điểm hết hạn giữ chỗ (epoch seconds / tick) cho Min-Heap TTL.
    assigned_user_id: ID khách hàng được gán (-1 nếu còn trong kho).
    seat_id: Tên vị trí ghế ngồi chính thức.
    """
    ticket_id: int
    ticket_type: str
    price: float
    expire_time: int
    assigned_user_id: int = -1
    seat_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ticket_id": self.ticket_id,
            "ticket_type": self.ticket_type,
            "price": self.price,
            "expire_time": self.expire_time,
            "expiration_time": self.expire_time,
            "assigned_user_id": self.assigned_user_id,
            "seat_id": self.seat_id,
        }
