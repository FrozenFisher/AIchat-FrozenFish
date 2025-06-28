# AI聊天系统安装指南

## 项目简介
基于GPT-SoVITS的AI聊天系统，支持多种角色，具备文本情感分析和音频生成功能。

## 文件结构
```
collection/
├── server.py              # 主服务器
├── client.py              # GUI客户端  
├── start_server.py        # 启动脚本
├── modelconfig.yaml       # 角色配置
├── requirements.txt       # Python依赖
├── setup_deepseek.py      # DeepSeek配置
├── setup_ollama.py        # Ollama配置
└── lib/                   # 资源文件
    ├── 参考音频/          # 情感音频
    ├── bg/               # 背景图片
    └── prompt/           # 提示词
```

## 安装步骤

### 1. 安装Python
- Windows: 从python.org下载，勾选"Add to PATH"
- macOS: `brew install python@3.9`
- Linux: `sudo apt install python3 python3-pip`

### 2. 安装依赖
```bash
pip install -r requirements.txt
```
windows用户：
前往[https://www.yuque.com/baicaigongchang1145haoyuangong/ib3g1e/dkxgpiy9zb96hob4#KTvnO]下载GPT-Sovits整合包
并按照教程[https://www.yuque.com/baicaigongchang1145haoyuangong/ib3g1e/xyyqrfwiu3e2bgyk]安装依赖
将附加文件里的SoVITS_weights_v2复制入整合包中的SoVITS_weights_v2
将附加文件里的GPT_weights_v2复制入整合包中的GPT_weights_v2

mac用户：
将附加文件重命名为GPT-Sovits
自行安装miniconda
打开命令行
```bash
cd '你的刚刚重命名的GPT-Sovits路径' #直接将文件夹拖入命令行窗口即可
chmod +x install.sh
./install.sh
```


### 3. 选择运行模式

#### 在线模式 (DeepSeek API)
```bash
# Windows
setup_deepseek.bat

# macOS/Linux  
python setup_deepseek.py
```

#### 离线模式 (Ollama)
```bash
# Windows
setup_ollama.bat

# macOS/Linux
python setup_ollama.py
```

### 4. 启动服务

第一个命令行界面
windows用户：
在整合包里面运行go-apiv2.bat

mac用户:
```bash
/Users/ycc/workspace/Chat/GPT-SoVITS/go-apiv2.command ; exit;
```

第二个命令行窗口

```bash
cd [你安装chat的地方]
#离线模式
python start_server.py --offline
#在线模式
python start_server.py --online
```

第三个命令行窗口
```bash
cd [你安装chat的地方]
python client.py
```

## 常见问题
- Python未找到: 重新安装并勾选PATH
- 依赖安装失败: 升级pip或使用国内镜像
- Ollama启动失败: 检查安装和端口占用
- API连接失败: 检查密钥和网络

## 系统要求

### 最低配置
- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **内存**: 8GB RAM
- **存储**: 10GB 可用空间
- **网络**: 稳定的互联网连接

### 推荐配置
- **操作系统**: Windows 11, macOS 12+, Ubuntu 20.04+
- **内存**: 16GB RAM
- **存储**: 20GB 可用空间
- **显卡**: NVIDIA GPU (用于音频生成)
- **网络**: 高速互联网连接

## 使用说明

### 基本使用
1. 启动服务器和客户端
2. 选择角色（银狼、温迪、流萤、潘兴）
3. 输入文本消息
4. 系统自动分析情感并生成对应音频

### 高级功能
- **情感分析**: 系统自动识别文本情感
- **音频生成**: 根据情感选择对应参考音频
- **多角色切换**: 支持不同角色风格
- **并发处理**: 支持多用户同时使用

## 技术支持

如遇到问题，请：
1. 查看错误日志
2. 运行测试脚本验证功能
3. 检查配置文件设置
4. 联系技术支持

## 更新日志

- v1.0: 基础功能实现
- v1.1: 添加Windows支持
- v1.2: 优化音频生成
- v1.3: 改进并发处理 