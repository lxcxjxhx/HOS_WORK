# 连点器开发者指南

## 项目结构
```
HOS_AUTO/
├── README.md           # 项目说明
├── config.json         # 配置文件
├── requirements.txt    # 依赖包列表
├── src/
│   ├── main.py         # 主程序入口
│   ├── clicker.py      # 点击模拟模块
│   ├── config.py       # 配置管理模块
│   ├── hotkey.py       # 热键监听模块
│   └── gui.py          # 图形界面模块
├── tests/
│   └── test_clicker.py # 测试文件
└── docs/
    ├── user_manual.md  # 用户手册
    └── dev_guide.md    # 开发者指南
```

## 技术栈
- 语言: Python 3.x
- 库:
  - pyautogui: 鼠标/键盘模拟
  - pynput: 热键监听
  - tkinter: GUI界面
  - threading: 多线程处理
  - pytest: 测试框架
  - pyinstaller: 打包工具

## 模块说明
### main.py
程序入口点，负责初始化各模块并协调它们的工作。

### clicker.py
核心模块，负责模拟鼠标点击操作。提供了点击启动、停止、暂停和恢复功能，支持自定义点击间隔、次数、按钮和位置。

### config.py
配置管理模块，负责加载和保存配置文件。如果配置文件不存在，会创建默认配置。

### hotkey.py
热键监听模块，负责监听用户的热键操作，并触发相应的回调函数。支持动态更新热键设置。

### gui.py
图形界面模块，提供用户交互界面。支持设置参数、启动/停止点击、应用设置等功能。

## 开发指南
### 环境设置
1. 安装Python 3.x
2. 克隆项目: git clone <repository_url>
3. 安装依赖: pip install -r requirements.txt
4. 运行: python src/main.py

### 代码规范
- 遵循PEP 8编码规范
- 使用类型提示提高代码可读性
- 添加适当的注释说明
- 保持函数和类的单一职责

### 测试
- 使用pytest运行测试: pytest tests/
- 添加新功能时，编写相应的测试用例
- 确保测试覆盖率达到80%以上

### 打包
使用PyInstaller打包为可执行文件:
```
pyinstaller --onefile --windowed src/main.py
```

## 贡献指南
1. Fork本项目
2. 创建特性分支: git checkout -b feature/xxx
3. 提交更改: git commit -m '添加xxx功能'
4. 推送分支: git push origin feature/xxx
5. 创建Pull Request

## 扩展建议
- 添加图像识别功能，支持点击特定目标
- 增加宏录制和回放功能
- 支持多鼠标/键盘设备
- 添加更多的自定义点击模式
- 开发移动端版本

## 注意事项
- 避免使用本工具进行游戏作弊或其他非法活动
- 开发过程中注意保护用户隐私
- 遵循开源许可协议