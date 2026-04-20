# 🎯 CES Improve Tool

**客户体验评分（CES）改善工具** — 一款面向 SAP 产品支持团队的内部 Web 应用，用于追踪客户满意度调查、自动分析低分原因，并管理跟进闭环流程。

## 📋 功能概览

### 1. 仪表盘（Dashboard）
- 调查总数、平均评分、低分占比等关键指标一览
- 评分分布图（1-5 分）
- 跟进状态分布（待处理 / 进行中 / 已完成 / 已升级）
- 低分原因分类统计（由 AI 分析 + 工程师确认）
- 月度平均评分趋势
- 团队成员跟进完成率排行榜

### 2. 调查列表与详情（Surveys）
- 查看所有客户满意度调查记录
- 支持按评分筛选
- 查看调查详情：客户信息、事件摘要、评分、客户评论、AI 分析结果

### 3. 跟进管理（Follow-ups）
- **自动分配**：评分 < 3 分的调查自动创建跟进任务，分配给原事件处理工程师
- **AI 原因分析**：基于关键词规则引擎，自动分类客户不满原因（响应慢、未解决、沟通差、技术不足、流程问题、期望偏差等）
- **邮件跟进**：内置邮件模板（初始跟进 / 解决方案更新），一键发送跟进邮件
- **电话跟进**：选择日期时间后自动生成 `.ics` 日历文件，支持导入 Outlook / 日历应用
- **完成闭环**：工程师确认原因分类、填写备注后标记完成

### 4. 用户认证
- 基于 Session 的登录/登出
- 工程师账号管理

## 🏗 技术架构

| 层级 | 技术栈 |
|------|--------|
| 后端框架 | Flask 3.0+ |
| 数据库 | SQLite + Flask-SQLAlchemy |
| 邮件服务 | Flask-Mail |
| 日历生成 | icalendar |
| 前端 | Bootstrap 5 + Jinja2 模板 |
| 密码加密 | Werkzeug (pbkdf2) |

## 📁 项目结构

```
ces_improve_tool/
├── app.py                  # Flask 应用入口 & 工厂函数
├── config.py               # 应用配置（数据库、邮件等）
├── models.py               # 数据模型（Customer, Engineer, Incident, Survey, Followup, ReasonCategory）
├── seed_data.py            # 演示数据生成脚本
├── requirements.txt        # Python 依赖
├── ces.db                  # SQLite 数据库文件
├── routes/                 # 路由/视图
│   ├── auth.py             # 登录/登出
│   ├── dashboard.py        # 仪表盘统计
│   ├── surveys.py          # 调查列表与详情
│   └── followups.py        # 跟进管理（邮件、电话、完成）
├── services/               # 业务逻辑服务
│   ├── analyzer.py         # AI 原因分析引擎（关键词规则）
│   ├── assignment.py       # 自动分配逻辑
│   ├── email_service.py    # 邮件模板渲染与发送
│   └── calendar_service.py # ICS 日历文件生成
├── templates/              # Jinja2 HTML 模板
│   ├── base.html           # 基础布局（导航栏）
│   ├── login.html          # 登录页
│   ├── dashboard.html      # 仪表盘
│   ├── survey_list.html    # 调查列表
│   ├── survey_detail.html  # 调查详情
│   ├── followup_list.html  # 跟进列表
│   └── followup_form.html  # 跟进操作表单
└── docs/                   # 设计文档
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化演示数据

```bash
python seed_data.py
```

这将创建：
- 7 个原因分类
- 10 个客户
- 5 个工程师（密码均为 `demo123`）
- 6 个月的事件和调查数据（含随机评分分布）
- 低分调查自动生成的跟进任务

### 3. 启动应用

```bash
python app.py
```

应用运行在 **http://127.0.0.1:5001**

### 4. 登录

使用任意工程师邮箱登录，密码为 `demo123`：

| 姓名 | 邮箱 | 产品领域 |
|------|------|----------|
| Zhang Wei | zhang.wei@sap.demo | ERP/FI |
| Li Ming | li.ming@sap.demo | ERP/MM |
| Wang Fang | wang.fang@sap.demo | S/4HANA |
| Chen Jie | chen.jie@sap.demo | BTP |
| Liu Yang | liu.yang@sap.demo | SuccessFactors |

## 📊 数据模型

```
Customer ──1:N──> Incident ──1:1──> Survey ──1:1──> Followup
                     ↑                                  ↑
                Engineer ──────────────────────> Engineer (assigned)
```

- **Customer**：客户信息（名称、邮箱、区域、联系人）
- **Engineer**：支持工程师（姓名、邮箱、产品领域）
- **Incident**：支持事件（客户、工程师、产品组件、摘要、时间）
- **Survey**：满意度调查（评分 1-5、评论、AI 分类、置信度）
- **Followup**：跟进任务（状态、联系方式、工程师确认分类、备注、时间记录）
- **ReasonCategory**：原因分类字典（代码 + 标签）

## 🤖 AI 原因分析

系统内置基于关键词的规则引擎，自动分析客户评论并分类：

| 分类代码 | 标签 | 关键词示例 |
|----------|------|-----------|
| `slow_response` | 响应慢 | slow, wait, delay, long time |
| `unresolved` | 未解决 | not resolved, still broken, not fixed |
| `poor_communication` | 沟通差 | no update, unclear, no response, ignored |
| `lack_expertise` | 技术不足 | wrong solution, not qualified, incorrect |
| `process_issue` | 流程问题 | transferred, bounced around, escalation |
| `expectation_mismatch` | 期望偏差 | expected, promised, disappointed, misleading |

分析结果包含分类和置信度，工程师在跟进完成时可确认或修正分类。

## 📧 邮件配置

默认使用本地 SMTP 开发服务器（端口 1025）。可通过环境变量配置真实 SMTP：

```bash
export MAIL_SERVER=smtp.example.com
export MAIL_PORT=587
export MAIL_USE_TLS=true
export MAIL_USERNAME=your-email@example.com
export MAIL_PASSWORD=your-password
export MAIL_DEFAULT_SENDER=noreply@example.com
```

开发测试时可使用 Python 内置 SMTP 调试服务器：

```bash
python -m smtpd -n -c DebuggingServer localhost:1025
```

## 📜 License

内部工具，仅供 SAP 产品支持团队使用。