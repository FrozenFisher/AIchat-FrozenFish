# Windows适配说明

## Windows特有的问题和解决方案

### 1. 路径分隔符问题
**问题**: Windows使用反斜杠`\`，而Unix系统使用正斜杠`/`
**解决方案**: 项目代码已使用`pathlib.Path`处理路径，自动适配不同操作系统

### 2. 环境变量设置
**问题**: Windows环境变量设置方式不同
**解决方案**: 
- 使用`setx`命令设置永久环境变量
- 使用`set`命令设置临时环境变量
- 批处理脚本已包含自动设置功能

### 3. 进程管理
**问题**: Windows进程启动和停止方式不同
**解决方案**:
- 使用`start /B`后台启动进程
- 使用任务管理器或`taskkill`停止进程
- 批处理脚本已适配Windows进程管理

### 4. 编码问题
**问题**: Windows默认使用GBK编码，可能导致中文显示问题
**解决方案**:
- 批处理脚本开头添加`chcp 65001`设置UTF-8编码
- Python脚本使用UTF-8编码保存

### 5. 权限问题
**问题**: Windows可能需要管理员权限
**解决方案**:
- 以管理员身份运行命令提示符
- 或右键批处理文件选择"以管理员身份运行"

## Windows安装步骤

### 方法一：使用批处理脚本（推荐）

1. **安装Python**
   ```cmd
   # 下载并安装Python 3.9+
   # 务必勾选"Add Python to PATH"
   ```

2. **运行安装脚本**
   ```cmd
   # 在线模式
   setup_deepseek.bat
   
   # 离线模式
   setup_ollama.bat
   ```

3. **启动服务**
   ```cmd
   python start_server.py
   python client.py
   ```

### 方法二：手动安装

1. **安装Python依赖**
   ```cmd
   pip install -r requirements.txt
   ```

2. **配置DeepSeek API**
   ```cmd
   set DEEPSEEK_API_KEY=your_api_key_here
   python setup_deepseek.py
   ```

3. **配置Ollama**
   ```cmd
   # 下载并安装Ollama
   # 启动服务
   ollama serve
   
   # 下载模型
   ollama pull qwen3:8b
   ```

## Windows特有功能

### 1. 批处理脚本功能
- 自动检查Python安装
- 自动安装依赖包
- 自动设置环境变量
- 自动测试API连接
- 友好的错误提示

### 2. 进程管理
- 后台启动Ollama服务
- 自动检测服务状态
- 超时处理机制

### 3. 用户交互
- 中文界面支持
- 输入验证
- 错误处理

## 常见Windows问题

### Q1: 批处理脚本无法运行
**解决方案**:
1. 右键批处理文件
2. 选择"以管理员身份运行"
3. 或检查文件是否被Windows Defender阻止

### Q2: Python命令未找到
**解决方案**:
1. 重新安装Python，勾选"Add to PATH"
2. 重启命令提示符
3. 或使用完整路径：`C:\Python39\python.exe`

### Q3: 依赖包安装失败
**解决方案**:
```cmd
# 升级pip
python -m pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### Q4: Ollama安装失败
**解决方案**:
1. 访问 https://ollama.ai/download
2. 下载Windows版本
3. 以管理员身份运行安装程序

### Q5: 端口被占用
**解决方案**:
```cmd
# 查看端口占用
netstat -ano | findstr :11434

# 结束进程
taskkill /PID <进程ID> /F
```

### Q6: 防火墙阻止
**解决方案**:
1. 打开Windows防火墙设置
2. 允许Python和Ollama通过防火墙
3. 或临时关闭防火墙测试

## 性能优化建议

### 1. 系统设置
- 关闭不必要的后台程序
- 增加虚拟内存
- 使用SSD存储

### 2. Python优化
```cmd
# 使用虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装优化包
pip install psutil
```

### 3. Ollama优化
```cmd
# 设置模型缓存目录
set OLLAMA_MODELS=C:\ollama\models

# 使用GPU加速（如果有NVIDIA显卡）
set CUDA_VISIBLE_DEVICES=0
```

## 故障排除

### 1. 日志查看
```cmd
# 查看Python错误
python -u script.py

# 查看系统日志
eventvwr.msc
```

### 2. 网络诊断
```cmd
# 测试网络连接
ping api.deepseek.com
ping localhost

# 测试端口
telnet localhost 11434
```

### 3. 系统信息
```cmd
# 查看系统信息
systeminfo

# 查看Python信息
python --version
pip list
```

## 联系支持

如遇到Windows特有问题，请提供：
1. Windows版本信息
2. Python版本信息
3. 错误日志
4. 系统配置信息 