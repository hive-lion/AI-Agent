# AI-Agent 技术调研文档（Harness / Skills / Memory / Tracing）

## 1. 调研目标与范围
本文聚焦 AI-Agent 系统中四个关键模块：
- **Harness（运行编排与执行壳层）**
- **Skills（能力插件与可复用工作流）**
- **Memory（短期/长期记忆）**
- **Tracing（可观测性与调试追踪）**

目标是梳理每个模块的主流技术、框架和落地方案，并给出组合建议，便于快速搭建可生产化的智能体系统。

---

## 2. 模块一：Harness（运行编排与执行壳层）

### 2.1 模块定义
Harness 是 Agent 的“执行底座”，负责：
- 生命周期管理（启动、任务调度、重试、停止）
- Tool 调用编排（函数调用、外部 API、脚本执行）
- 安全策略（权限、沙箱、速率限制）
- 与 Memory、Tracing、Skills 的连接

### 2.2 主流技术与框架

#### A. LangGraph（LangChain 生态）
- **优势**：状态机/图式编排强，适合复杂多分支流程；支持 checkpoint。
- **适用场景**：复杂业务流程、多 Agent 协作、需要可恢复执行的任务。
- **挑战**：设计成本高于简单链式调用。

#### B. AutoGen / AutoGen Studio
- **优势**：多 Agent 对话协作模式成熟，角色分工清晰。
- **适用场景**：研究型、多角色评审、讨论类任务。
- **挑战**：在强约束生产流中需要补充治理层。

#### C. CrewAI
- **优势**：任务（Task）+ 角色（Agent）+ 团队（Crew）模型直观，工程化上手快。
- **适用场景**：企业流程自动化、个人助理、中小型多 Agent 应用。
- **挑战**：复杂状态恢复与可视化编排能力依赖外部补充。

#### D. Semantic Kernel
- **优势**：插件化和企业系统集成（尤其 .NET 生态）友好。
- **适用场景**：微软技术栈企业应用、强工具集成。
- **挑战**：中文生态资料相对少于 LangChain。

### 2.3 方案建议
- **快速 PoC**：CrewAI / LangChain Agent。
- **复杂生产流**：LangGraph + 任务队列（Celery/Temporal）。
- **企业治理优先**：Harness + Policy Engine（如 OPA）+ 审计日志。

---

## 3. 模块二：Skills（能力插件与可复用工作流）

### 3.1 模块定义
Skills 是 Agent 可动态调用的能力单元，通常包括：
- Tool API（如日历、邮件、搜索、数据库）
- Prompt 模板
- 业务规则与校验逻辑
- 输入输出 Schema

### 3.2 主流技术与框架

#### A. OpenAI Function Calling / JSON Schema Tooling
- **优势**：结构化参数输出稳定；对接外部服务简单。
- **场景**：标准 API 编排、事务型任务。

#### B. LangChain Tools / Toolkits
- **优势**：工具生态丰富（DB、Search、Retriever、Python REPL）。
- **场景**：快速拼接多工具链。

#### C. MCP（Model Context Protocol）
- **优势**：统一模型与工具、资源之间的协议层，便于跨平台扩展。
- **场景**：需要标准化工具接入、跨团队复用 Skill。

#### D. CrewAI Tools
- **优势**：与 Agent/Task 天然耦合，定义和调用路径简单。
- **场景**：业务工作流导向的技能封装。

### 3.3 Skills 设计最佳实践
- 强类型入参（Pydantic / JSON Schema）
- 幂等与重试策略（避免重复写入）
- 超时与降级机制（fallback）
- 业务“护栏”检查（合规、敏感词、权限）
- 版本化（v1/v2）与可回滚

---

## 4. 模块三：Memory（短期/长期记忆）

### 4.1 模块定义
Memory 用于维护 Agent 在任务内和跨任务的上下文能力。
- **短期记忆**：会话窗口、当前任务状态
- **长期记忆**：用户偏好、历史事件、知识库
- **工作记忆**：中间推理结果/执行痕迹（可截断）

### 4.2 主流存储方案

#### A. 向量数据库
- 代表：Pinecone、Weaviate、Milvus、Qdrant、pgvector
- 用途：语义检索、RAG、长期知识记忆
- 注意：embedding 版本迁移与重建成本

#### B. KV/文档数据库
- 代表：Redis、MongoDB、DynamoDB
- 用途：会话态、用户偏好、任务缓存
- 注意：TTL 策略和数据一致性

#### C. 图数据库
- 代表：Neo4j、Memgraph
- 用途：人物关系、事件关系、流程依赖
- 注意：建模复杂度高但解释性强

### 4.3 记忆架构建议
- **分层存储**：
  - L1：上下文缓存（Redis）
  - L2：长期语义记忆（Vector DB）
  - L3：结构化档案（Postgres/Mongo）
- **写入门控**：只将高价值信息写入长期记忆
- **遗忘机制**：过期策略 + 摘要压缩
- **隐私治理**：PII 脱敏、分级加密、访问审计

---

## 5. 模块四：Tracing（可观测性与调试追踪）

### 5.1 模块定义
Tracing 用于追踪 Agent 的每一步决策与执行链路，包括：
- Prompt / Completion
- Tool 调用参数与结果
- Token 消耗、延迟、错误率
- 任务级链路（trace/span）

### 5.2 主流技术与框架

#### A. LangSmith
- LangChain/LangGraph 生态观测首选
- 具备运行回放、评估、数据集管理能力

#### B. OpenTelemetry + Jaeger/Tempo/Grafana
- 标准化可观测方案，跨语言统一
- 可和企业现有监控体系融合

#### C. Helicone / Arize Phoenix / Weights & Biases（LLM Observability）
- 关注 LLM 调用质量、成本与评测闭环
- 适合实验迭代与效果对比

### 5.3 Trace 数据规范建议
- 每次 Task 生成唯一 trace_id
- Tool 调用生成 span，并记录：入参摘要、耗时、状态码
- 区分用户错误、模型错误、系统错误
- 保留 prompt 版本号和 Skill 版本号

---

## 6. 组合落地架构（推荐）

### 6.1 中小团队推荐栈
- Harness：**CrewAI**
- Skills：CrewAI Tools + Function Calling
- Memory：Redis + Qdrant/pgvector
- Tracing：OpenTelemetry + Langfuse/LangSmith

### 6.2 企业生产推荐栈
- Harness：LangGraph + Temporal
- Skills：MCP + 内部 API Gateway
- Memory：Postgres + 向量库 + 数据治理层
- Tracing：OpenTelemetry + APM + 质量评估平台

---

## 7. 选型决策矩阵（简版）

| 维度 | CrewAI | LangGraph | AutoGen |
|---|---|---|---|
| 上手速度 | 高 | 中 | 中 |
| 复杂流程控制 | 中 | 高 | 中 |
| 多 Agent 协作 | 中-高 | 高 | 高 |
| 企业可治理性 | 中 | 高 | 中 |
| 生态成熟度 | 快速增长 | 高 | 中-高 |

---

## 8. 结论
- 若目标是“快速交付业务助理”，**CrewAI** 是高性价比选择。
- 若目标是“复杂流程 + 可恢复执行 + 强治理”，优先考虑 **LangGraph + 企业调度系统**。
- 无论选择何种 Harness，建议优先补齐 **Memory 分层架构** 和 **Tracing 规范**，这两项决定可持续迭代能力。
