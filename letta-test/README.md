# AI聊天系统 - Letta版

基于Letta框架重构的AI聊天系统，使用Letta进行大模型交互和记忆管理，保持GPT-SoVITS进行TTS音频生成。

## 架构特点

- **Letta框架**: 使用Letta进行Agent管理、记忆存储和工具调用
- **GPT-SoVITS**: 保持原有的高质量TTS音频生成
- **客户端-服务器分离**: 清晰的职责分工
- **生产者-消费者模式**: 高效的音频流处理
- **实时音频清理**: 播放完成后立即删除临时文件
- **配置持久化**: 自动保存Letta Agent ID到配置文件，避免重复创建

## 系统架构

```
┌─────────────────┐    RESTful API    ┌─────────────────┐
│   Letta客户端   │ ◄────────────────► │   Letta服务器   │
│   (UI + 播放)   │                   │ (推理 + 音频生成)│
└─────────────────┘                   └─────────────────┘
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │   Letta服务     │
                                    │ (Agent + 记忆)  │
                                    └─────────────────┘
                                              │
                                              ▼
                                    ┌─────────────────┐
                                    │  GPT-SoVITS     │
                                    │   (TTS服务)     │
                                    └─────────────────┘
```

## 文件结构

```
letta-test/
├── letta_server.py          # Letta版服务器
├── letta_client.py          # Letta版客户端
├── start_letta_server.py    # 服务器启动脚本
├── test_letta_api.py        # API测试脚本
├── setup_letta.py           # Letta安装配置脚本
├── requirements.txt         # 依赖文件
├── modelconfig.yaml         # 角色配置文件
└── README.md               # 本文档
```

## 安装和配置

### 1. 安装依赖

```bash
cd letta-test
pip install -r requirements.txt
```

### 2. 安装Letta

```bash
# 安装Letta客户端
pip install letta-client

# 安装Letta服务器（可选，用于本地部署）
pip install letta
```

### 3. 配置Letta

#### 方式一：使用Letta Cloud
```bash
export LETTA_API_KEY="your_letta_api_key"
```

#### 方式二：使用本地Letta服务器
```bash
# 启动本地Letta服务器
letta server start

# 设置环境变量
export LETTA_BASE_URL="http://localhost:8283"
```

### 4. 配置角色

编辑 `modelconfig.yaml` 文件，可以添加Letta Agent ID：

```yaml
Agents:
  银狼:
    GPTPath: "GPT_SoVITS/pretrained_models/s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt"
    SoVITSPath: "GPT_SoVITS/pretrained_models/s2G488k.pth"
    bgPath: "lib/bgSilverWolf.png"
    promptPath: "lib/prompt/promptSilverWolf.txt"
    refaudioPath: "lib/参考音频/该做的事都做完了么？好，别睡下了才想起来日常没做，拜拜。.wav"
    letta_agent_id: ""  # 留空则自动创建并保存
```

**重要**: 系统会自动管理Letta Agent ID：
- 首次使用时，如果`letta_agent_id`为空，系统会自动创建Agent并保存ID到配置文件
- 重启后，系统会使用已保存的Agent ID，避免重复创建
- 这样可以确保Agent的连续性和记忆的持久化

## 使用方法

### 1. 启动服务器

```bash
python start_letta_server.py
```

服务器将在 `http://127.0.0.1:8000` 启动，提供以下API：

- `GET /` - 服务器状态
- `GET /agents` - 获取角色列表
- `GET /agent/{name}` - 获取角色配置
- `GET /agent/{name}/prompt` - 获取角色提示词
- `POST /agent/{name}/init` - 初始化角色会话
- `POST /chat` - 发送聊天消息
- `POST /switch_agent/{name}` - 切换角色
- `GET /letta/agents` - 获取Letta Agents列表
- `GET /letta/health` - 检查Letta服务状态
- `GET /config/agents` - 获取所有角色配置信息（包括Agent ID）

### 2. 启动客户端

```bash
python letta_client.py
```

### 3. 测试API

```bash
python test_letta_api.py
```

## 核心功能

### 1. Letta Agent管理

- **自动创建Agent**: 根据角色提示词自动创建Letta Agent
- **Agent复用**: 支持配置中指定Agent ID，避免重复创建
- **配置持久化**: 自动保存Agent ID到配置文件，重启后继续使用
- **会话管理**: 每个角色独立的会话上下文

### 2. 记忆系统

- **长期记忆**: 使用Letta的Core Memory存储重要信息
- **会话记忆**: 自动维护对话上下文
- **知识检索**: 支持基于记忆的智能回复
- **记忆持久化**: Agent重启后记忆不会丢失

### 3. 音频处理

- **分句生成**: 将长文本分割为句子，逐句生成音频
- **流式处理**: 使用生产者-消费者模式处理音频数据
- **实时清理**: 播放完成后立即删除临时文件
- **Think标签过滤**: 自动过滤`<think></think>`标签内容

### 4. 角色系统

- **多角色支持**: 支持多个AI角色切换
- **角色初始化**: 启动时自动初始化角色并显示介绍
- **配置管理**: 统一的角色配置文件管理
- **Agent ID管理**: 自动管理每个角色的Letta Agent ID

## API接口详解

### 聊天接口

```python
POST /chat
{
    "message": "用户消息",
    "agent": "角色名称",
    "session_id": "会话ID（可选）"
}

Response:
{
    "response": "AI回复",
    "session_id": "会话ID",
    "audio_data": ["base64音频数据1", "base64音频数据2", ...]
}
```

### 角色初始化接口

```python
POST /agent/{agent_name}/init
{
    "message": "",
    "agent": "角色名称",
    "session_id": "会话ID（可选）"
}

Response:
{
    "response": "角色介绍",
    "session_id": "会话ID",
    "audio_data": ["base64音频数据1", "base64音频数据2", ...]
}
```

### 配置查询接口

```python
GET /config/agents

Response:
{
    "agents": {
        "银狼": {
            "name": "银狼",
            "gpt_path": "...",
            "sovits_path": "...",
            "bg_path": "...",
            "prompt_path": "...",
            "ref_audio_path": "...",
            "letta_agent_id": "agent_123456"  # 自动保存的Agent ID
        }
    }
}
```

## 配置说明

### 环境变量

- `LETTA_API_KEY`: Letta Cloud API密钥
- `LETTA_BASE_URL`: Letta服务器地址（默认：http://localhost:8283）

### 角色配置

每个角色包含以下配置项：

- `GPTPath`: GPT模型路径
- `SoVITSPath`: SoVITS模型路径
- `bgPath`: 背景图片路径
- `promptPath`: 角色提示词文件路径
- `refaudioPath`: 参考音频文件路径
- `letta_agent_id`: Letta Agent ID（可选，留空则自动创建并保存）

### 配置持久化机制

1. **首次使用**: 当角色的`letta_agent_id`为空时，系统会：
   - 读取角色提示词
   - 创建新的Letta Agent
   - 将Agent ID保存到内存和配置文件
   - 显示创建成功信息

2. **后续使用**: 当角色的`letta_agent_id`已存在时，系统会：
   - 直接使用已保存的Agent ID
   - 保持Agent的连续性和记忆
   - 避免重复创建Agent

3. **配置更新**: 系统会自动：
   - 在创建新Agent后立即保存配置
   - 在启动时显示已配置的Agent信息
   - 提供配置查询API

## 故障排除

### 1. Letta连接失败

```bash
# 检查Letta服务状态
curl http://localhost:8283/health

# 检查环境变量
echo $LETTA_API_KEY
echo $LETTA_BASE_URL
```

### 2. GPT-SoVITS服务异常

```bash
# 检查GPT-SoVITS服务
curl http://127.0.0.1:9880
```

### 3. 音频生成失败

- 检查参考音频文件是否存在
- 确认GPT-SoVITS模型路径正确
- 查看服务器日志获取详细错误信息

### 4. Agent ID问题

```bash
# 查看已配置的Agent
curl http://127.0.0.1:8000/config/agents

# 检查配置文件
cat modelconfig.yaml
```

## 性能优化

### 1. 音频处理优化

- 使用生产者-消费者模式避免阻塞
- 实时清理临时文件减少磁盘占用
- 分句生成提高响应速度

### 2. 内存管理

- 及时释放音频数据
- 使用流式处理避免大文件加载
- 定期清理会话缓存

### 3. Agent管理优化

- 配置持久化避免重复创建Agent
- Agent复用减少资源消耗
- 记忆持久化提高用户体验

## 开发说明

### 1. 添加新角色

1. 在 `modelconfig.yaml` 中添加角色配置
2. 准备角色提示词文件
3. 准备参考音频文件
4. 重启服务器（系统会自动创建Agent并保存ID）

### 2. 自定义Letta Agent

```python
# 在 letta_server.py 中修改 create_letta_agent 函数
def create_letta_agent(agent_name: str, system_prompt: str) -> Optional[str]:
    agent_data = {
        "name": f"{agent_name}_agent",
        "description": f"AI聊天角色: {agent_name}",
        "instructions": system_prompt,
        "model": "gpt-4",  # 可以修改模型
        "tools": []  # 可以添加工具
    }
    # ...
```

### 3. 扩展音频处理

```python
# 在 letta_server.py 中修改 generate_audio_segments 函数
async def generate_audio_segments(text: str, agent: str) -> List[str]:
    # 可以添加音频预处理、后处理等逻辑
    # ...
```

### 4. 配置管理扩展

```python
# 在 letta_server.py 中修改 save_config 函数
def save_config():
    # 可以添加配置验证、备份等逻辑
    # ...
```

## 版本历史

- **v2.0.0**: 基于Letta重构，支持Agent管理和记忆系统
- **v2.1.0**: 添加配置持久化功能，避免重复创建Agent
- **v1.x**: 原始版本，使用Ollama/DeepSeek

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 贡献

欢迎提交Issue和Pull Request来改进项目。

## 联系方式

如有问题，请通过以下方式联系：

- 提交GitHub Issue
- 发送邮件至项目维护者 