from typing import Any

def calculate_course_fee(total_fee: Any, total_hours: Any) -> str:
    """
    Hàm thực thi logic tính toán chi phí.
    """
    try:
        fee = float(total_fee)
        hours = float(total_hours)
        
        if hours <= 0:
            return "Lỗi: Tổng số giờ học phải lớn hơn 0."
        
        fee_per_hour = fee / hours
        return f"{fee_per_hour:,.0f} VNĐ/giờ"
    except (ValueError, TypeError):
        return "Lỗi: Tham số truyền vào phải là số (Học phí hoặc Số giờ không hợp lệ)."
    except Exception as e:
        return f"Lỗi hệ thống: {str(e)}"

calculate_course_fee_metadata = {
        "name": "calculate_course_fee",
        "description": "Tính chi phí trung bình trên mỗi giờ học để so sánh giá giữa các trung tâm.",
        "parameters": {
            "total_fee": "float - Tổng học phí (VNĐ)",
            "total_hours": "int - Tổng thời lượng khóa học (giờ)"
        },
        "return": "string - Đơn giá VNĐ/giờ hoặc thông báo lỗi",
        "error_mode": "Trả về chuỗi bắt đầu bằng 'Lỗi:'",
        "func": calculate_course_fee  # Tham chiếu trực tiếp đến hàm ở trên
    }