# WarDog CCIP HUD 原型

当前第二阶段：独立的透明 HUD，仅显示一个绿色圆环与短十字线组成的标记。坐标为模拟/手动坐标，**不是实际投弹落点**。不接入游戏，不采集屏幕，不实现 OCR、游戏数据读取或弹道计算。第一阶段的飞行数据窗口继续作为独立调试工具保留。

## Windows 安装

需要 **64 位 Python 3.11 或更新版本**。在项目根目录打开 PowerShell：

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

无需激活虚拟环境或修改 PowerShell 执行策略。运行不需要密钥、额外服务或游戏连接。

## 启动 HUD

```powershell
.\.venv\Scripts\python.exe -m wardog --hud
```

首次启动默认把标记放在主屏中心。HUD 无边框、透明、置顶、不接受焦点，使用 Qt 原生窗口级输入穿透标志及鼠标事件穿透属性。画面只有一个标记，没有仪表或文字；静止时不使用刷新定时器，只在坐标、大小或可见性变化时重绘。

优先使用游戏的**无边框窗口模式**，保持固定驾驶舱视角。本原型是普通桌面窗口，独占全屏模式的叠加显示不在保证范围内。

Windows 通知区域会出现绿色圆环托盘图标（可能在“隐藏的图标”中）。右键菜单提供：

- **校准**：打开独立校准窗口。
- **显示 / 隐藏 HUD**：切换标记可见性。
- **退出**：关闭 HUD、校准窗口和托盘图标，结束程序。

## 校准、保存与退出

直接进入校准模式：

```powershell
.\.venv\Scripts\python.exe -m wardog --hud --calibrate
```

`--calibrate` 单独使用也会启动 HUD 与校准窗口。

1. 调整“水平位置 X”和“垂直位置 Y”，标记会立即移动。
2. 调整“标记直径”（12–200），立即预览大小。
3. 使用“显示 HUD”复选框测试隐藏和恢复。
4. 点击“保存校准”，将 X、Y、直径保存到用户配置文件。下次启动自动加载；未保存的调整不持久化，显示/隐藏状态不持久化。
5. 点击“退出程序”或托盘菜单“退出”，结束程序。

有托盘时，关闭校准窗口只关闭控制界面，HUD 继续运行；通过托盘可重新打开。没有可用托盘时会自动显示校准窗口，此时关闭校准窗口也会退出程序，避免留下无法控制的 HUD。

配置位置由 Qt 的 `AppConfigLocation` 决定，Windows 通常是 `%LOCALAPPDATA%\WarDog\WarDog\hud.json`；保存成功后界面会显示实际完整路径。保存失败会显示错误，不报告成功。损坏的配置文件会保留并显示提示，临时使用屏幕中心；保存的坐标不在当前屏幕内时，也会临时回到主屏中心，重新校准并保存即可。

### 显示缩放与坐标

Qt 6 自动启用高 DPI 支持。位置和直径使用**全局桌面逻辑像素**，不是屏幕截图的物理像素。例如 150% 缩放时，40 个逻辑像素约为 60 个物理像素。X/Y 是标记中心坐标；副屏位于主屏左侧或上方时可以使用负坐标。原型不追踪游戏窗口：移动游戏窗口、更换显示器或修改缩放后，请重新校准。未来计算模块可调用 `HudOverlay.set_marker_position(x, y)` 更新位置，不需要修改绘制逻辑。

### Windows 实机检查

云端 offscreen 测试能验证绘制和配置逻辑，不能证明 Windows 桌面合成器中的真实透明、置顶或点击穿透。请在 Windows 本地检查：

1. 启动 HUD，确认圆环以外完全透明，且没有额外文字或边框。
2. 将标记移到记事本/浏览器按钮上，点击标记中心及圆环，确认底层程序收到点击且焦点不被 HUD 抢走。
3. 在无边框游戏中确认置顶、正常鼠标操作，并在 100%、125%、150%、200% 缩放下分别校准检查。
4. 移动、缩放、隐藏、恢复标记；保存后退出重启，确认参数恢复。
5. 从托盘或校准窗口退出，确认标记与托盘图标消失、Python 进程结束。

## 第一阶段调试窗口

```powershell
.\.venv\Scripts\python.exe -m wardog
```

无参数启动保留原有飞行数据显示窗口，每 100 ms 更新模拟高度（m）、速度（km/h）、俯仰角和滚转角（度），关闭窗口退出。它不是正式 HUD，也不是启动 HUD 的必要窗口。模拟曲线不代表真实飞行动力学。

## 开发与测试

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Linux / 云环境：

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m pytest -q
# 有桌面显示时才能看到实际 HUD
.venv/bin/python -m wardog --hud --calibrate
```

UI 测试默认使用 Qt `offscreen` 平台，不弹出可见窗口。覆盖第一阶段模拟数据与窗口，以及 HUD 透明绘制、窗口输入/焦点标志、位置/大小/可见性、校准保存恢复、无托盘降级、异常配置和应用退出。无桌面的 Linux 仍需 OpenGL/EGL 等 Qt 系统共享库。

## 目录结构

```text
wardog/
  __main__.py       # 默认调试窗口；--hud / --calibrate 入口
  models.py         # 第一阶段飞行数据模型
  simulation.py     # 第一阶段模拟计算
  ui/window.py      # 原有飞行数据调试窗口
  hud/
    config.py       # 校准模型、校验与 JSON 原子保存
    overlay.py      # 独立、仅标记的透明窗口
    calibration.py  # 独立手动校准界面
    application.py  # HUD 生命周期、托盘与配置加载
tests/             # 模拟、UI、校准及 HUD 测试
requirements.txt
requirements-dev.txt
```

屏幕采集、数字识别、姿态识别和弹道计算留待后续阶段；本阶段不引入这些模块，也不修改游戏文件或进程。
