# 爱刷题

一个轻量级、无数据库的刷题H5应用，专为碎片化学习设计

## 🌟 项目介绍

爱刷题是一款专注于帮助用户利用碎片化时间进行学习和复习的Web应用。无论您是备考证书、学习新知识还是巩固已有技能，都可以通过这个简单易用的工具来提升学习效率。

## ✨ 最新更新

我们已推出功能更强大的爱刷题PLUS版本，包含管理后台和更美观的UI设计：
- [爱刷题PLUS--ADMIN](https://github.com/moke8/aishuati-plus-admin/) - 管理后台
- [爱刷题PLUS--WECHAT](https://github.com/moke8/aishuati-plus-wechat/) - 微信小程序前端
- [爱刷题PLUS--API](https://github.com/moke8/aishuati-plus-api/) - 后端API服务

## 🚀 特色功能

- **轻量级部署**：无后端、无数据库，仅需静态文件服务器即可运行
- **灵活的题库管理**：使用JSON格式存储题库，结构清晰，易于维护
- **便捷的导入工具**：提供Word模板和自动化转换脚本，快速创建题库
- **多样化刷题模式**：支持顺序刷题、乱序刷题、错题模式、背题模式
- **学习进度跟踪**：顺序答题和背题模式支持自动保存和恢复答题进度
- **响应式设计**：适配移动端和桌面端，随时随地学习
- **友好的用户界面**：简洁直观的操作体验，专注于学习本身

## 📁 项目结构

```
aishuati/
├── index.html      # 主页，显示题库列表
├── type.html       # 刷题模式选择页面
├── timu.html       # 刷题页面（核心功能）
├── css/            # 样式文件目录
│   ├── fonts/      # 字体文件
│   └── iview.css   # UI框架样式
├── js/             # JavaScript文件
│   ├── vue.min.js  # Vue框架
│   ├── iview.min.js# UI组件库
│   ├── axios.min.js# HTTP请求库
│   └── public.js   # 公共配置和工具函数
├── json/           # 题库存储目录
└── py-timuToJson/  # 题库转换工具
```

## 📋 使用说明

### 1. 准备工作

下载项目后，由于浏览器的安全限制，**不能直接双击HTML文件打开使用**。您需要通过以下方式运行：

- 使用任意静态文件服务器（如Nginx、Apache等）
- 使用VS Code的Live Server插件
- 使用Python的简易HTTP服务器：
  ```bash
  # Python 3.x
  python -m http.server
  
  # Python 2.x
  python -m SimpleHTTPServer
  ```

### 2. 创建题库

1. 使用`py-timuToJson`目录下的Word模板编辑题目
2. 将模板内容复制到TXT文件中
3. 运行`timu_manager.py`或`timuToJson.py`将TXT转换为JSON格式
4. 将生成的JSON文件放入`json`目录中
5. 更新`js/public.js`中的题库配置信息

### 3. 开始刷题

1. 访问主页`index.html`，选择您要学习的题库
2. 选择刷题模式（顺序、乱序、错题、背题）
3. 开始答题，系统会自动记录您的进度和错题

## 🎯 刷题模式说明

- **顺序刷题**：按照题库顺序依次做题
- **乱序刷题**：随机打乱题目顺序，适合强化记忆
- **错题模式**：只显示之前答错的题目，针对性复习
- **背题模式**：直接显示答案和解析，适合快速记忆

## 🖼️ 效果预览

[在线演示站](http://shuati.mokevip.top/)

以下是应用的界面截图：

![主页预览](https://s1.ax1x.com/2020/09/14/wD3NTA.png)
![模式选择](https://s1.ax1x.com/2020/09/14/wD8KBQ.png)
![答题界面](https://s1.ax1x.com/2020/09/14/wD8lAs.png)
![答案解析](https://s1.ax1x.com/2020/09/14/wD81Nn.png)
![进度恢复](https://s1.ax1x.com/2020/09/14/wD83hq.png)

## 💻 技术栈

- 前端：HTML5, CSS3, JavaScript, Vue.js
- UI框架：iView
- 题库存储：JSON
- 题库转换：Python
- 本地存储：localStorage（用于保存答题进度和错题）

## 🤝 贡献指南

欢迎提交Issue和Pull Request来帮助改进这个项目。如果您有任何建议或问题，请在GitHub上提出。

## 📝 许可证

该项目采用MIT许可证，详情请查看LICENSE文件。

## 🙏 鸣谢

感谢所有使用和支持这个项目的用户！您的反馈是我们不断进步的动力。
