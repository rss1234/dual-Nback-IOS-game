# Dual N-Back Game (Python + Kivy)

这是一个使用 Python 和 Kivy 开发的双通道 N-Back 训练游戏，支持在 Windows、Linux 和 Android 平台上运行。

## 🎮 游戏说明

- **双通道 N-Back 训练**：同时训练视觉和听觉记忆。
- **随机生成刺激序列**：每次游戏都会生成新的刺激序列，增强训练效果。
- **用户交互**：通过按钮判断当前刺激是否与 N 步前相同。

## ✅ 本地运行（Windows/Linux）

1. 安装依赖：

   ```bash
   pip install -r requirements.txt

2. 运行程序：

   ```bash
   python main.py

## 📱 Android 打包（需 Linux）

1. 安装 Buildozer：

   ```bash
   pip install buildozer

2. 初始化 Buildozer 配置：

   ```bash
   buildozer init

3. 编辑 buildozer.spec 文件，设置应用名称、包名等信息。
   
4. 构建 APK：

   ```bash
   buildozer -v android debug
构建完成后，APK 文件位于 bin/ 目录下。

## 📌 TODO

- [ ] 添加声音播放功能
- [ ] 游戏设置界面（如设置 N 值、游戏时长等）
- [ ] 分数记录与排行榜功能
- [ ] iOS 构建支持（需 macOS + Xcode）


## 📄 许可证
本项目采用 MIT 许可证，详情请参阅 LICENSE 文件。