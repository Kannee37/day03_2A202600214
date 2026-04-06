# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyen Thi Thuy Trang
- **Student ID**: 2A202600214
- **Date**: 2026-04-06

---

## I. Technical Contribution (15 Points)

- **Modules Implementated**: Triển khai logic ReAct Agent (hoàn thành phần TODO), Xây dựng phiên bản chatbot.py ban đầu (phiên bản hiện tại là phiên bản đã được chỉnh sửa - debug) 
- **Code Highlights**: 
```python
if action_match:
    tool_name = action_match.group(1)
    tool_args = action_match.group(2).strip("\"'") # Xóa dấu ngoặc kép thừa nếu có
    
    logger.info(f"[ACTION_PARSED] Bắt lệnh gọi tool: {tool_name} | Tham số: {tool_args}")
    
    # Gọi hàm thực thi vật lý
    tool_start_time = time.time()
    observation_result = self._execute_tool(tool_name, tool_args)
    tool_time = round(time.time() - tool_start_time, 2)
    
    logger.info(f"[TOOL_END] Hoàn thành tool {tool_name} trong {tool_time}s")
    logger.debug(f"[OBSERVATION_DATA] {observation_result[:200]}... (đã rút gọn)")
    
    # Ném kết quả vào giấy nháp để AI đọc ở vòng lặp tiếp theo
    current_prompt += f"Observation: {observation_result}\n"
```
- **Documentation**: Đoạn code này thực hiện các bước:
1. Trích xuất tên too; và tham số từ output của LLM
2. Gọi tool tương ứng trong danh sách tools
3. Thêm kết quả vào prompt dưới dạng Observation

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: Tôi gặp vấn đề là Agent không kích hoạt tool, Gemini trả lời trực tiếp như một Chatbot mặc dù hệ thống đã được cấu hình với nhiều tools.
- **Log Source**: Log hệ thống không xuất hiện các block Thought, Action, Observation
- **Diagnosis**: Lỗi ban đầu đến từ gọi sai tên hàm của tools. gọi sai hàm trong agent.
- **Solution**: Tôi đã rà soát lại, chỉnh sửa lại chỗ sai trong tên hàm, gọi đúng hàm trong agent

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**:  Khối Thought giúp mô hình suy nghĩ từng bước. Thay vì thấy câu hỏi xong trả lời luôn, mô hình sẽ tự phân tích: Người dùng đang hỏi gì, thiếu thông tin nào, cần tìm thêm dữ liệu hay không, nên làm gì tiếp theo. Thought giúp mô hình giúp Agent biết khi nào cần hành động, giảm kiểu trả lời "Ảo tưởng đúng", giúp xử lý bài toán phức tạp nhiều bước 
2.  **Reliability**: Agent tệ hơn Chatbot thường khi task đơn giản, không cần suy luận nhiều, khi thêm bước thought sẽ khiến kết quả trả về chậm hơn, có thể khiến mô hình bị suy luận nhiều, gọi tool không cần thiết.
3.  **Observation**: Observation giúp agent cập nhật trạng thái, quyết định bước tiếp theo; nhưng đôi khi Observation có thể làm agent lệch hướng nếu Observation sai, thiếu hoặc nhiễu.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Agent không nên thực hiện các tool call theo cách đồng bộ vì sẽ gây tắc nghẽn khi có nhiều người dùng cùng lúc. Nên khi mở rộng, có thể dùng hàng đợi bất đồng bộ (asynchronous queue) để xử lý các tác vụ nhưu gọi API, truy vấn database hoặc search. Có thể chia nhỏ dữ liệu để xử lý song song, phân phối request hoặc sử dụng Horizontal scaling (auto-scaling) - tăng số lượng máy/instance chạy song song.
- **Safety**: Agent không nên được phép hành động hoàn toàn tự động mà không có kiểm soát, cần triển khai Supervisor LLM hoặc một lớp guardrails để kiểm tra các hành động trước khi thực thi. Các biện pháp an toàn bổ sung bao gồm: phân quyền cho các tool nhạy cảm, whitelist/blacklist hành động, giới hạn tần suất hoặc yêu cầu human-in-the-loop cho các hành động quan trọng.
- **Performance**: Khi hệ thống có nhiều tool, có thể sử dụng vector database để thực hiện tool retrival, chỉ chọn ra các tool liên quan nhất. Hiệu năng cũng có thể được cải thiện bằng cách giới hạn bước suy luận của mô hình hoặc sử dụng mô hình nhỏ cho tác vụ đơn giản, mô hình lớn cho tác vụ phức tạp.
