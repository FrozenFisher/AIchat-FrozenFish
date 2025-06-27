# AI聊天系统 - 重构版本 (Ollama)

## 🎯 重构目标

将原本混合在单一文件中的推理、音频生成模块和UI彻底分离，采用客户端-服务器架构：

- **server.py** - 负责所有计算任务（LLM推理、音频生成、模型管理）
- **client.py** - 只负责UI交互和音频播放
- 通过RESTful API进行通信
- 使用Ollama作为LLM框架
- **新增**: 生产者-消费者模式的音频处理

## 🏗️ 新架构

```
┌─────────────────┐    HTTP API    ┌─────────────────┐
│   client.py     │ ◄────────────► │   server.py     │
│   (UI + 音频播放) │                │   (计算任务)      │
│   ┌─────────┐   │                │   ┌─────────┐   │
│   │生产者线程│   │                │   │分句音频 │   │
│   │消费者线程│   │                │   │生成     │   │
│   └─────────┘   │                │   └─────────┘   │
└─────────────────┘                └─────────────────┘
         │                                   │
         │                                   │
         ▼                                   ▼
┌─────────────────┐                ┌─────────────────┐
│   PyQt5 GUI     │                │   Ollama        │
│   AudioPlayer   │                │   GPT-SoVITS    │
└─────────────────┘                └─────────────────┘
```

## 🎵 音频处理流程

### 统一音频数据流架构
```
文本回复 → 服务器分句处理 → 服务器生成音频数据 → 客户端接收音频流 → 客户端播放音频
```

**服务器端**:
- 生成音频数据（不保存文件）
- 直接返回音频数据流
- 统一管理音频生成过程

**客户端**:
- 接收音频数据流
- 临时保存为文件
- 播放完成后立即删除

### 生产者-消费者模式
```
音频数据流 → 生产者线程保存文件 → 消费者线程播放音频 → 立即删除文件
```

**生产者线程**:
- 接收服务器音频数据流
- 临时保存到本地
- 将文件路径放入队列

**消费者线程**:
- 从队列获取文件路径
- 播放音频
- **播放完成后立即删除文件**

### 分句音频生成
- **智能分割**: 按标点符号分割文本
- **并行生成**: 多个句子同时生成音频
- **流式传输**: 音频数据直接传输，无需文件管理
- **实时清理**: 音频播放完成后立即删除临时文件

### Think标签过滤
- **智能过滤**: 自动识别并过滤`<think></think>`标签内容
- **显示优化**: 用户界面只显示可见内容
- **音频优化**: 不为think标签内容生成音频

## 📁 文件结构

```
collection/
├── server.py              # 服务器端 - 计算任务
├── client.py              # 客户端 - UI交互
├── start_server.py        # 服务器启动脚本
├── requirements.txt       # Python依赖
├── modelconfig.yaml       # 角色配置
├── temp/                  # 临时音频文件
└── lib/                   # 资源文件
    ├── bg/               # 背景图片
    ├── prompt/           # 角色提示词
    └── 参考音频/          # 参考音频文件
```

## 🚀 启动流程

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 安装并启动Ollama
```bash
# 安装Ollama (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# 启动Ollama服务
ollama serve

# 下载模型
ollama pull qwen3:8b
```

### 3. 启动GPT-SoVITS API服务
```bash
cd ../GPT-SoVITS
./go-apiv2.command
```

### 4. 启动AI聊天服务器
```bash
python start_server.py
```

### 5. 启动客户端
```bash
python client.py
```

## 🔧 API接口

### 服务器端API (server.py)

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | `/` | 服务器状态 |
| GET | `/agents` | 获取所有角色 |
| GET | `/agent/{name}` | 获取角色配置 |
| GET | `/agent/{name}/prompt` | 获取角色提示词 |
| POST | `/agent/{name}/init` | 初始化角色会话 |
| GET | `/models` | 获取可用Ollama模型 |
| POST | `/models/{name}` | 切换Ollama模型 |
| POST | `/chat` | 发送聊天消息（返回音频数据流） |
| POST | `/switch_agent/{name}` | 切换角色 |
| DELETE | `/session/{id}` | 删除会话 |

### 客户端功能 (client.py)

- **ChatClient**: API通信封装
- **AudioPlayer**: 音频播放管理
- **FloatingWindow**: 主聊天窗口
- **SettingWindow**: 设置窗口
- **音频处理**: 生产者-消费者模式

## 🎨 主要特性

### 服务器端
- ✅ 异步处理聊天请求
- ✅ 自动令牌管理
- ✅ 会话状态管理
- ✅ 角色切换功能
- ✅ 分句音频生成
- ✅ Think标签过滤
- ✅ 错误处理和重试
- ✅ Ollama模型管理
- ✅ 角色提示词管理
- ✅ 角色会话初始化

### 客户端
- ✅ 响应式UI设计
- ✅ 生产者-消费者音频处理
- ✅ 实时音频文件清理
- ✅ Think标签显示过滤
- ✅ 角色配置管理
- ✅ 拖拽窗口
- ✅ 智能颜色适配
- ✅ 自动角色初始化
- ✅ 角色提示词显示
- ✅ 角色状态管理
- ✅ 实时文字显示

## 🔄 数据流

### 角色初始化流程
1. 客户端启动时自动初始化当前角色
2. 客户端获取角色提示词并显示
3. 客户端发送初始化请求到服务器
4. 服务器加载角色提示词并生成回复
5. 客户端显示角色回复并播放音频
6. 用户可以进行正常对话

### 聊天流程
1. 用户在客户端输入消息
2. 客户端通过HTTP API发送到服务器
3. 服务器调用Ollama API生成回复
4. **服务器分句生成音频数据（不保存文件）**
5. **服务器返回文本回复和音频数据流**
6. **客户端立即显示文字回复**
7. **客户端使用生产者-消费者模式播放音频数据流**

### 音频处理流程
1. 服务器将AI回复分句
2. **服务器过滤掉`<think></think>`标签内容**
3. **服务器为每个句子生成音频数据（不保存文件）**
4. **服务器直接返回音频数据流**
5. **客户端生产者线程保存音频数据为临时文件**
6. **客户端消费者线程播放音频**
7. **播放完成后立即删除临时文件**

### 角色切换流程
1. 用户在设置窗口选择角色
2. 客户端调用角色切换API
3. 服务器更新GPT-SoVITS模型
4. 客户端更新UI背景和配置
5. 客户端重新初始化新角色（重复角色初始化流程）

### 模型切换流程
1. 客户端调用模型切换API
2. 服务器验证模型可用性
3. 服务器更新当前模型
4. 返回切换结果

## 🛠️ 技术栈

### 服务器端
- **FastAPI**: Web框架
- **Ollama**: LLM推理框架
- **GPT-SoVITS**: 语音合成
- **Pydantic**: 数据验证
- **Uvicorn**: ASGI服务器

### 客户端
- **PyQt5**: GUI框架
- **Requests**: HTTP客户端
- **Pydub**: 音频处理
- **SimpleAudio**: 音频播放
- **Threading**: 生产者-消费者模式

## 🔧 配置说明

### modelconfig.yaml
```yaml
Agents:
  银狼:
    GPTPath: GPT_weights_v2/银狼-e10.ckpt
    SoVITSPath: SoVITS_weights_v2/银狼_e15_s480.pth
    bgPath: lib/bg/bgSilverWolf.png
    promptPath: lib/prompt/promptSilverWolf.txt
    refaudioPath: lib/参考音频/xxx.wav
```

### Ollama模型配置
默认使用 `qwen3:8b` 模型，支持以下操作：
- 查看可用模型: `GET /models`
- 切换模型: `POST /models/{model_name}`
- 下载新模型: `ollama pull {model_name}`

## 🐛 故障排除

### 常见问题

1. **Ollama服务连接失败**
   - 检查Ollama是否已安装并启动
   - 确认端口11434可用
   - 运行 `ollama serve` 启动服务

2. **模型下载失败**
   - 检查网络连接
   - 使用 `ollama pull qwen2:7b` 下载模型
   - 查看可用模型: `ollama list`

3. **音频播放失败**
   - 检查音频文件权限
   - 确认simpleaudio依赖正确安装

4. **GPT-SoVITS连接失败**
   - 检查GPT-SoVITS服务是否启动
   - 确认端口9880可用

### 调试模式
```bash
# 启动服务器时启用详细日志
python -m uvicorn server:app --host 0.0.0.0 --port 8000 --log-level debug

# 查看Ollama日志
ollama logs
```

## 📈 性能优化

### 已实现优化
- ✅ 异步音频生成
- ✅ 令牌历史截断
- ✅ 连接池复用
- ✅ 后台任务处理
- ✅ Ollama模型缓存

### 未来优化方向
- 🔄 WebSocket实时通信
- 🔄 音频流式传输
- 🔄 模型热更新
- 🔄 负载均衡

## 🔮 扩展计划

1. **WebSocket支持**: 实现实时双向通信
2. **多客户端支持**: 支持多个客户端同时连接
3. **音频流式传输**: 减少延迟
4. **模型热更新**: 无需重启切换模型
5. **监控面板**: 服务器状态监控
6. **多模型支持**: 支持更多Ollama模型

## 📝 更新日志

### v1.1.0 (Ollama版本)
- ✅ 完成Xinference到Ollama的迁移
- ✅ 添加Ollama模型管理功能
- ✅ 优化API接口设计
- ✅ 改进错误处理机制
- ✅ 更新启动脚本和文档

### v1.0.0 (重构版本)
- ✅ 完成客户端-服务器架构分离
- ✅ 实现RESTful API通信
- ✅ 优化音频处理流程
- ✅ 改进错误处理机制
- ✅ 添加启动脚本和依赖管理

## 系统架构

本系统采用客户端-服务器架构，实现了推理和UI的完全分离，支持两种运行模式：

### 服务器端 (`server.py`)
- **支持双模式**：本地Ollama和在线DeepSeek API
- **负责所有计算任务**：LLM推理、音频生成、模型管理
- **统一音频生成**：所有音频文件生成和存储都在服务器端
- **RESTful API接口**：提供标准化的HTTP接口

### 客户端 (`client.py`)
- **纯UI界面**：基于PyQt5的图形界面
- **音频播放**：接收服务器音频数据流并播放
- **角色管理**：角色切换和配置显示
- **实时通信**：通过HTTP API与服务器通信

## 运行模式

### 🌐 在线模式 (DeepSeek API)
- **推理框架**：DeepSeek-V3模型
- **优势**：无需本地模型，响应速度快，质量高
- **要求**：需要DeepSeek API密钥
- **配置**：设置`DEEPSEEK_API_KEY`环境变量

### 🏠 离线模式 (Ollama)
- **推理框架**：本地Ollama + 大语言模型
- **优势**：完全离线，数据安全，无网络依赖
- **要求**：需要安装Ollama和下载模型
- **配置**：启动Ollama服务

## 音频数据流架构

### 新的音频处理流程
1. **服务器端生成音频**：使用GPT-SoVITS生成音频数据
2. **Base64编码传输**：将音频数据编码为base64字符串
3. **JSON序列化**：通过HTTP API传输base64编码的音频数据
4. **客户端解码播放**：解码base64数据并播放音频

### 音频数据格式
```json
{
  "response": "AI回复文本",
  "session_id": "会话ID",
  "audio_data": [
    "base64编码的音频片段1",
    "base64编码的音频片段2",
    ...
  ]
}
```

### 生产者-消费者模式
- **生产者线程**：解码base64数据，保存为临时文件
- **消费者线程**：播放音频文件，播放完成后立即删除
- **队列通信**：使用线程安全的队列进行数据传递

## API接口

### 核心接口
- `GET /` - 服务器状态和模式信息
- `GET /config/mode` - 获取当前运行模式
- `POST /config/online` - 切换在线/离线模式
- `GET /agents` - 获取可用角色列表
- `GET /agent/{agent_name}` - 获取角色配置
- `GET /agent/{agent_name}/prompt` - 获取角色提示词
- `POST /agent/{agent_name}/init` - 初始化角色会话
- `POST /chat` - 发送聊天消息
- `POST /switch_agent/{agent_name}` - 切换角色

### 音频相关接口
- `GET /audio/{filename}` - 获取音频文件（已废弃）
- `DELETE /audio/{filename}` - 删除音频文件（已废弃）

**注意**：音频数据现在通过`/chat`和`/agent/{agent_name}/init`接口的响应直接传输，不再需要单独的音频文件接口。

## 角色初始化流程

### 客户端启动流程
1. 加载角色配置
2. 获取当前角色的提示词
3. 初始化角色会话
4. 显示角色提示词和初始化回复
5. 启用用户输入

### 角色切换流程
1. 用户选择新角色
2. 获取新角色的提示词
3. 初始化新角色会话
4. 显示角色提示词和初始化回复
5. 更新UI背景和按钮颜色

## 音频播放机制

### 实时音频处理
- **分句生成**：服务器将AI回复按句子分割，逐句生成音频
- **流式传输**：音频数据通过HTTP响应流式传输
- **即时播放**：客户端接收到音频数据后立即开始播放
- **自动清理**：播放完成后立即删除临时音频文件

### 音频数据格式
- **编码方式**：Base64编码的字符串
- **文件格式**：WAV格式音频数据
- **传输方式**：JSON数组中的字符串列表

## 安装和配置

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 选择运行模式

#### 在线模式 (推荐)
```bash
# 设置DeepSeek API密钥
export DEEPSEEK_API_KEY="your_api_key_here"

# 启动在线模式
python start_server.py --online
```

#### 离线模式
```bash
# 安装Ollama
brew install ollama  # macOS
# 或使用安装脚本
python setup_ollama.py

# 下载模型
ollama pull qwen3:8b

# 启动离线模式
python start_server.py --offline
```

### 3. 启动GPT-SoVITS服务
确保GPT-SoVITS服务在`http://127.0.0.1:9880`运行

## 启动系统

### 1. 启动服务器
```bash
# 在线模式
python start_server.py --online

# 离线模式
python start_server.py --offline

# 自动检测模式
python start_server.py
```

### 2. 启动客户端
```bash
python client.py
```

### 3. 测试API
```bash
python test_api.py
```

## 配置说明

### 环境变量
- `DEEPSEEK_API_KEY`：DeepSeek API密钥（在线模式必需）
- `ONLINE_MODE`：运行模式标志（true=在线，false=离线）

### 模型配置 (`modelconfig.yaml`)
```yaml
Agents:
  银狼:
    GPTPath: "GPT_SoVITS/pretrained_models/s1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt"
    SoVITSPath: "GPT_SoVITS/pretrained_models/s2G488k.pth"
    bgPath: "lib/bgSilverWolf.png"
    promptPath: "lib/prompt/promptSilverWolf.txt"
    refaudioPath: "lib/参考音频/训练日志(银狼).log"
```

### 默认模型
- **在线模式**：`deepseek-chat` (DeepSeek-V3)
- **离线模式**：`qwen3:8b`
- **默认角色**：`银狼`

## 故障排除

### 常见问题
1. **在线模式连接失败**：检查DeepSeek API密钥是否正确
2. **离线模式连接失败**：检查Ollama服务是否启动
3. **音频无法播放**：检查GPT-SoVITS服务是否运行
4. **角色初始化失败**：检查配置文件路径是否正确
5. **UTF-8编码错误**：确保音频数据正确编码为base64

### 调试信息
系统提供详细的调试日志：
- 🚀 线程启动状态
- ✅ 成功操作
- ❌ 错误信息
- 🎵 音频播放状态
- 🗑️ 文件清理状态
- 🌐 在线模式状态
- 🏠 离线模式状态

## 技术栈

- **后端框架**：FastAPI
- **LLM框架**：DeepSeek API (在线) / Ollama (离线)
- **音频生成**：GPT-SoVITS
- **前端框架**：PyQt5
- **音频播放**：pydub + simpleaudio
- **数据传输**：HTTP + JSON + Base64

## 性能优化

### 音频处理优化
- **分句生成**：减少单次音频生成时间
- **流式传输**：提高响应速度
- **即时清理**：减少磁盘占用
- **生产者-消费者模式**：提高并发性能

### 内存管理
- **临时文件**：播放完成后立即删除
- **Base64编码**：避免二进制数据序列化问题
- **队列管理**：控制内存中的音频数据量

### 模式切换
- **动态切换**：运行时可在在线和离线模式间切换
- **自动检测**：根据环境变量自动选择合适模式
- **错误回退**：在线模式失败时自动回退到离线模式 