# WarDog 飞行数据演示

第一阶段是独立的 Python / PySide6 桌面演示：显示随时间变化的模拟高度、速度、俯仰角和滚转角。当前不连接真实游戏，不包含屏幕采集、OCR 或游戏 HUD 叠加。

## Windows 运行

需要 **64 位 Python 3.11 或更新版本**（本次在 Python 3.12 验证）。在项目根目录打开 PowerShell：

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m wardog
```

无需激活虚拟环境或修改 PowerShell 执行策略。窗口每 100 ms 更新一次模拟数据，关闭窗口退出。高度单位为米，速度为 km/h，俯仰角和滚转角为度。运行不需要密钥、额外服务或游戏。

## 开发和测试

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

UI 测试默认使用 Qt 的 `offscreen` 平台，验证窗口创建、数值与单位显示、定时更新和关闭。它不会打开可见桌面窗口；实际窗口外观需要在 Windows 桌面上人工检查。

Linux / 云环境中可使用：

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
# 有桌面显示时启动
.venv/bin/python -m wardog
```

无桌面的 Linux 环境仅运行 offscreen 测试即可；Qt 仍需系统提供 OpenGL/EGL 等共享库。

## 目录结构

```text
wardog/
  __main__.py       # 应用入口
  models.py         # 不可变飞行数据模型，字段带单位
  simulation.py     # 独立、确定性的模拟计算
  ui/
    window.py       # PySide6 显示与刷新
tests/            # 模型、计算和 UI 基本测试
requirements.txt   # 运行依赖
requirements-dev.txt # 测试依赖
```

计算模块只依赖数据模型，不依赖 Qt。UI 消费模型，由单调计时器驱动模拟计算；后续可通过独立的数据来源替换模拟器。当前曲线仅用于演示，不代表真实飞行动力学或弹道计算。
