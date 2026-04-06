import time
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger

class ReActAgent:
    """
    Hệ thống Agent hoàn chỉnh chạy theo vòng lặp Thought - Action - Observation.
    """
    
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self) -> str:
        """
        Nạp danh sách công cụ và ép LLM tuân thủ nghiêm ngặt định dạng ReAct.
        """
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']} (Tham số: {t['args']})" for t in self.tools])
        
        return f"""
        Bạn là một Trợ lý AI thông minh chuyên tư vấn khóa học. Bạn có quyền truy cập vào các công cụ sau:
        {tool_descriptions}

        BẠN BẮT BUỘC PHẢI SỬ DỤNG ĐÚNG ĐỊNH DẠNG SAU ĐỂ TƯ DUY:
        Thought: [Suy nghĩ của bạn về việc phải làm gì tiếp theo, bạn cần dữ liệu gì]
        Action: [ten_cong_cu(tham_so)]
        Observation: [Kết quả trả về từ công cụ - HỆ THỐNG SẼ ĐIỀN VÀO ĐÂY, BẠN KHÔNG ĐƯỢC TỰ VIẾT]
        ... (Lặp lại Thought/Action/Observation nếu cần tra cứu thêm)
        Thought: [Tôi đã thu thập đủ thông tin để trả lời]
        Final Answer: [Câu trả lời đầy đủ, chi tiết và chính xác gửi cho người dùng]
        """

    def run(self, user_input: str) -> str:
        """
        Vòng lặp cốt lõi: Gửi Prompt -> Đọc Thought -> Chạy Tool -> Trả Observation -> Lặp lại.
        """
        start_time = time.time()
        logger.info(f"\n🚀 [AGENT_START] Nhận yêu cầu: '{user_input}' | Model: {self.llm.model_name}")
        
        # current_prompt là tờ giấy nháp ghi lại toàn bộ quá trình trò chuyện
        current_prompt = f"Yêu cầu của người dùng: {user_input}\n"
        steps = 0

        while steps < self.max_steps:
            steps += 1
            logger.info(f"[VÒNG LẶP ReAct] Bắt đầu Step {steps}/{self.max_steps}")
            
            # 1. Gọi LLM sinh ra suy nghĩ (Thought) và Hành động (Action)
            result_raw = self.llm.generate(current_prompt, system_prompt=self.get_system_prompt())
            
            # Bóc tách text nếu LLM trả về một Dictionary
            if isinstance(result_raw, dict) and 'content' in result_raw:
                result_text = result_raw['content']
            else:
                result_text = str(result_raw)
            
            # Ghi log nháp của LLM để debug
            logger.debug(f"[LLM_RESPONSE_RAW]:\n{result_text}\n{'-'*40}")
            
            # Chép lời của AI vào giấy nháp
            current_prompt += f"{result_text}\n"

            # 2. Kiểm tra xem AI đã chốt đáp án chưa (Final Answer)
            if "Final Answer:" in result_text:
                final_answer = result_text.split("Final Answer:")[-1].strip()
                total_time = round(time.time() - start_time, 2)
                
                logger.info(f"[AGENT_END] Hoàn thành sau {steps} bước. Tổng thời gian: {total_time}s")
                return final_answer

            # 3. Dùng Regex tóm lấy lệnh gọi Tool (Action)
            # Cú pháp tìm kiếm: Action: ten_tool(tham_so) hoặc Action: ten_tool("tham_so")
            action_match = re.search(r"Action:\s*(\w+)\((.*?)\)", result_text)
            
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
            else:
                # Nếu AI lảm nhảm sai cú pháp, mắng nó và bắt nó làm lại
                error_msg = "Lỗi: Không tìm thấy 'Action' hoặc 'Final Answer' đúng định dạng. Hãy suy nghĩ lại."
                logger.warning(f"[PARSE_ERROR] AI trả về sai định dạng. Bắt ép sửa lỗi.")
                current_prompt += f"Observation: {error_msg}\n"
                
        # Nếu chạy hết max_steps (ví dụ 5 lần) mà vẫn không ra đáp án -> Báo lỗi Timeout
        total_time = round(time.time() - start_time, 2)
        logger.error(f"[AGENT_TIMEOUT] Đạt giới hạn {self.max_steps} bước mà chưa có Final Answer. Thời gian: {total_time}s")
        return "Xin lỗi, tôi đã cố gắng tra cứu nhưng hệ thống xử lý quá số bước cho phép. Vui lòng thử lại với câu hỏi đơn giản hơn."

    def _execute_tool(self, tool_name: str, args: str) -> str:
        """
        Nơi kết nối lệnh của AI với các file Tool thực tế.
        """
        # Import bản đồ functions từ thư mục tools
        try:
            from src.tools import TOOL_FUNCTIONS
            
            if tool_name in TOOL_FUNCTIONS:
                func = TOOL_FUNCTIONS[tool_name]
                # Thực thi tool với tham số AI truyền vào
                return func(args)
            else:
                return f"Lỗi hệ thống: Tool '{tool_name}' chưa được khai báo trong TOOL_FUNCTIONS."
                
        except ImportError:
            return "Lỗi cấu trúc: Không thể nạp TOOL_FUNCTIONS từ src.tools. Hãy đảm bảo bạn đã code file __init__.py."
        except Exception as e:
            return f"Lỗi khi chạy thực thi {tool_name}: {str(e)}"