#Merge Sort cho danh sach user theo thoi gian den.

from numbers import Real
from typing import Any, Dict, List

#Tron hai danh sach da sap xep, giu thu tu on dinh.
def _merge(
    left: List[Dict[str, Any]],
    right: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        if left[left_index]["arrival_time"] <= right[right_index]["arrival_time"]:
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1

    merged.extend(left[left_index:])
    merged.extend(right[right_index:])
    return merged

#Sap xep bang Merge Sort theo tu tuong Divide & Conquer.
def _merge_sort(users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    
    if len(users) <= 1:
        return users.copy()

    middle = len(users) // 2
    left = _merge_sort(users[:middle])
    right = _merge_sort(users[middle:])
    return _merge(left, right)

#Kiem tra cau truc dau vao truoc khi sap xep.
def _validate_users(users: List[Dict[str, Any]]) -> None:
    if not isinstance(users, list):
        raise TypeError("users phai la List[Dict[str, Any]], khong duoc la None.")

    for index, user in enumerate(users):
        if not isinstance(user, dict):
            raise TypeError(f"user tai vi tri {index} phai la dict.")
        if "arrival_time" not in user:
            raise ValueError(f"user tai vi tri {index} thieu truong 'arrival_time'.")
        arrival_time = user["arrival_time"]
        if isinstance(arrival_time, bool) or not isinstance(arrival_time, Real):
            raise TypeError(
                f"arrival_time cua user tai vi tri {index} phai la mot gia tri so."
            )


def chia_de_tri_sap_xep_thoi_gian(
    users: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    _validate_users(users)
    return _merge_sort(users)


if __name__ == "__main__":
    users = [
        {"user_id": "U003", "arrival_time": 15, "diem_loyalty": 80},
        {"user_id": "U001", "arrival_time": 5, "diem_loyalty": 95},
        {"user_id": "U004", "arrival_time": 10, "diem_loyalty": 60},
        {"user_id": "U002", "arrival_time": 10, "diem_loyalty": 70},
    ]

    result = chia_de_tri_sap_xep_thoi_gian(users)
    for user in result:
        print(
            f"user_id: {user['user_id']}, "
            f"arrival_time: {user['arrival_time']}, "
            f"diem_loyalty: {user['diem_loyalty']}"
        )
