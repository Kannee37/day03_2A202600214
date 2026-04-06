# Group Report: Lab 3 - Production-Grade Agentic System

- **Team Name**: C401 - B4
- **Team Members**: Nguyen Thi Thuy Trang, Trinh Uyen Chi, Tran Viet Phuong, Le Duc Anh, Nguyen Hoang Nghia, Pham Nguyen Tien Manh, Nguyen Ngoc Tan
- **Deployment Date**: 2026-04-06

---

## 1. Executive Summary

_Brief overview of the agent's goal and success rate compared to the baseline chatbot._

- **Success Rate**: 90% on 20 test cases
- **Key Outcome**: The agent improved the overall success rate by 30% points compared to the baseline chatbot. The baseline LLM-only chatbot correctly answered 12 out of 20 test cases (60%), while the agent, which integrates external tools and the ReAct reasoning loop, successfully solved 18 out of 20 queries (90%) by retrieving and processing course information more effectively.

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation

Our agent follows the **ReAct (Reasoning + Action) loop**:

1. **Thought**: Analyze user input to identify intent and required information.
2. **Action**: Decide which tool to call based on the query.
3. **Observation**: Execute the tool and collect results.
4. **Iteration**: Repeat Thought-Action-Observation until the query is resolved or max steps are reached.

### 2.2 Tool Definitions (Inventory)

| Tool Name                    | Input Format                                                                             | Use Case                                                                                                            |
| ---------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `search_course_info`         | `string query`                                                                           | Search for online course listings using the Google Search API, returning JSON with course title, snippet, and link. |
| `extract_course_information` | `object`<br>`link` (string)<br>`level` (string)<br>`topic` (string)<br>`format` (string) | Retrieve detailed course information (tuition, duration) from a valid course page.                                  |
| `calculate_course_fee`       | `float total_fee`, `int total_hours`                                                     | Compute the average fee per hour for a course to compare pricing across different centers.                          |

### 2.3 LLM Providers Used

- **Primary**: Gemini 2.5 Flash
- **Secondary (Backup)**: Gemini 1.5 Flash

---

## 3. Telemetry & Performance Dashboard

_Analyze the industry metrics collected during the final test run._

- **Average Latency (P50)**: 1405ms
- **Max Latency (P99)**: 3301ms
- **Average Tokens per Task**: 698 tokens
- **Total Cost of Test Suite**: ≈ $0.0165 for 20 test queries

---

## 4. Root Cause Analysis (RCA) - Failure Traces

_Deep dive into why the agent failed._

### Case Study: Empty Output due to Missing Information

- **Input**: "Find me a list of basic Python programming courses offline in Cau Giay, Hanoi."
- **Observation**: The agent called `search_course_info` multiple times, but the returned JSON did not standardize `location` and `format` information. In loop 4, the LLM returned empty output (`finish_reason=1`) → Agent could not aggregate results.
- **Root Cause**: The tool output lacked clear location and format data, combined with a prompt missing `Few-Shot` examples on handling incomplete JSON, causing the LLM to be unable to proceed when data was missing.

---

## 5. Ablation Studies & Experiments

### Experiment 1: Prompt v1 vs Prompt v2

- **Diff**: Added instruction "Always double-check tool inputs and parameters before calling" in Prompt v2.
- **Result**: Reduced invalid tool call errors from 4/5 test cases to 1/5 (~75% reduction).

### Experiment 2: Chatbot vs Agent

| Case              | Chatbot Result                     | Agent Result                                                 | Winner    |
| :---------------- | :--------------------------------- | :----------------------------------------------------------- | :-------- |
| Simple Q          | Correct                            | Correct                                                      | Draw      |
| Multi-step        | Incorrect (hallucinated or empty)  | Correct, tool calls and aggregated results accurately        | **Agent** |
| Location-specific | Often ignored location information | Correctly identified the Cau Giay branch (if data available) | **Agent** |

_Observations_:

- The agent outperforms in multi-step logic and data aggregation across multiple sources.
- Pure LLM chatbots tend to hallucinate or skip specific conditions like location or offline course format.

---

## 6. Production Readiness Review

_Considerations for deploying this system in a real-world environment._

- **Security**:
  - Validate and sanitize user inputs before calling tools to prevent errors or injection.
  - Restrict access to API keys and sensitive credentials, avoid hardcoding in source code.

- **Guardrails**:
  - Limit the maximum number of ReAct loops (e.g., `max_steps=5`) to prevent infinite execution and cost escalation.
  - Verify tool outputs before using them to avoid propagating errors into the pipeline.

- **Scaling**:
  - For multi-branching or multi-agent workflows, consider using LangGraph or dedicated orchestration systems.
  - Cache frequent tool results to reduce API calls and improve response times.

- **Monitoring & Logging**:
  - Log detailed actions, tool calls, and latency for performance and failure analysis.
  - Track average latency, P50/P99 to monitor production performance.

- **Cost Management**:
  - Limit tokens or calls per user/session to control LLM and tool expenses.
  - Use batch processing for large tasks to reduce overall costs.

- **User Experience**:
  - Provide clear feedback if the agent cannot find results or encounters tool errors.
  - Allow users to refine queries or provide additional information when prompted by the agent.

---