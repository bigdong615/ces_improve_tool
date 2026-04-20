# CES Improve Tool — 客户满意度调查跟进系统设计规格

**日期：** 2026-04-20  
**状态：** 待审查  
**作者：** AI 辅助设计

---

## 1. 项目概述

### 1.1 背景

SAP Product Support 团队需要一个工具来系统化处理客户满意度调查（Customer Effort Score）。当客户对 support 服务给出低分评价时，团队需要及时识别原因、主动联系客户、改进服务质量。

### 1.2 目标

- 自动识别低分 survey（评分 < 3）并分析原因
- 按规则自动将跟进任务分配给原始 incident 处理 engineer
- 提供邮件发送和电话日历提醒功能，方便 engineer 联系客户
- 提供仪表盘展示整体满意度趋势和跟进进度
- 使用 mock 数据演示完整功能

### 1.3 使用者

团队多人协作使用。Engineer 处理分配给自己的跟进任务，Team lead 通过仪表盘监控整体进度。

### 1.4 技术栈

- **后端：** Python Flask + SQLAlchemy
- **数据库：** SQLite
- **前端：** Jinja2 模板 + Bootstrap 5（CDN）
- **邮件：** SMTP（Flask-Mail 或 smtplib）
- **日历：** icalendar 库生成 `.ics` 文件

---

## 2. 数据模型

### 2.1 customers — 客户信息

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTO | 客户 ID |
| name | TEXT | NOT NULL | 客户名称（公司名） |
| email | TEXT | NOT NULL | 联系邮箱 |
| region | TEXT | NOT NULL | 区域（APAC / EMEA / Americas） |
| contact_person | TEXT | NOT NULL | 联系人姓名 |

### 2.2 engineers — 团队成员

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTO | Engineer ID |
| name | TEXT | NOT NULL | 姓名 |
| email | TEXT | NOT NULL, UNIQUE | 邮箱（登录凭证） |
| password_hash | TEXT | NOT NULL | 密码哈希 |
| product_area | TEXT | NOT NULL | 负责产品领域 |

### 2.3 incidents — Support Case 记录

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTO | Incident ID |
| customer_id | INTEGER | FK → customers.id | 客户 |
| engineer_id | INTEGER | FK → engineers.id | 处理人 |
| product_component | TEXT | NOT NULL | 产品组件 |
| summary | TEXT | NOT NULL | 问题摘要 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| resolved_at | DATETIME | | 解决时间 |

### 2.4 surveys — 满意度调查

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTO | Survey ID |
| incident_id | INTEGER | FK → incidents.id, UNIQUE | 关联 Incident（1:1） |
| score | INTEGER | NOT NULL, CHECK(1-5) | 满意度评分 |
| comment | TEXT | | 客户文字评论 |
| submitted_at | DATETIME | NOT NULL | 提交时间 |
| ai_category | TEXT | | AI 预分类的原因标签 |
| ai_confidence | REAL | | AI 分类置信度 (0.0-1.0) |

### 2.5 followups — 跟进记录

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTO | 跟进 ID |
| survey_id | INTEGER | FK → surveys.id, UNIQUE | 关联 Survey（1:1） |
| assigned_engineer_id | INTEGER | FK → engineers.id | 分配的 Engineer |
| status | TEXT | NOT NULL, DEFAULT 'pending' | 状态：pending / in_progress / completed / escalated |
| contact_method | TEXT | | 联系方式：email / phone / both |
| engineer_category | TEXT | | Engineer 确认/修正后的原因分类 |
| notes | TEXT | | 跟进备注 |
| email_sent_at | DATETIME | | 邮件发送时间 |
| call_scheduled_at | DATETIME | | 电话预约时间 |
| completed_at | DATETIME | | 完成时间 |
| created_at | DATETIME | NOT NULL | 创建时间 |

### 2.6 reason_categories — 预设原因分类（字典表）

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTO | 分类 ID |
| code | TEXT | NOT NULL, UNIQUE | 分类代码 |
| label | TEXT | NOT NULL | 显示名称 |

**预设分类：**

| code | label |
|------|-------|
| slow_response | 响应时间慢 |
| unresolved | 问题未解决 |
| poor_communication | 沟通不畅 |
| lack_expertise | 技术能力不足 |
| process_issue | 流程问题 |
| expectation_mismatch | 期望不匹配 |
| other | 其他 |

---

## 3. 系统架构

### 3.1 项目结构

```
ces_improve_tool/
├── app.py                  # Flask 应用入口
├── config.py               # 配置（SMTP、数据库路径等）
├── models.py               # SQLAlchemy 数据模型
├── database.py             # 数据库初始化与连接
├── seed_data.py            # Mock 数据生成脚本
├── services/
│   ├── assignment.py       # 自动分配逻辑
│   ├── analyzer.py         # AI 原因分析（关键词规则引擎）
│   ├── email_service.py    # 邮件发送（SMTP）
│   └── calendar_service.py # 日历提醒（.ics 文件生成）
├── routes/
│   ├── dashboard.py        # 仪表盘页面路由
│   ├── surveys.py          # Survey 列表与详情路由
│   ├── followups.py        # 跟进管理路由
│   └── api.py              # JSON API（供前端 AJAX 调用）
├── templates/
│   ├── base.html           # 基础布局（Bootstrap 5）
│   ├── dashboard.html      # 仪表盘
│   ├── survey_list.html    # Survey 列表
│   ├── survey_detail.html  # Survey 详情 + 跟进操作
│   ├── followup_list.html  # 我的跟进任务
│   └── followup_form.html  # 跟进记录表单
├── static/
│   ├── css/style.css
│   └── js/main.js
└── requirements.txt
```

### 3.2 模块职责

| 模块 | 职责 | 依赖 |
|------|------|------|
| `assignment.py` | 低分 survey 入库时，查找 incident 原始处理 engineer，创建 followup 记录（status=pending）。若 engineer 不存在则标记 escalated | models |
| `analyzer.py` | 扫描 survey comment 文本，基于关键词库匹配预设分类，返回 `(category, confidence)` | reason_categories |
| `email_service.py` | 根据邮件模板渲染内容，通过 SMTP 发送跟进邮件给客户 | Flask-Mail 或 smtplib |
| `calendar_service.py` | 生成标准 `.ics` 日历事件文件，供 engineer 下载导入日历 | icalendar |

### 3.3 用户认证

简单 session 登录：engineer 用邮箱 + 密码登录，密码使用 `werkzeug.security` 做哈希存储。登录后通过 `session['engineer_id']` 识别当前用户。Mock 数据中密码统一为 `demo123`。

### 3.4 依赖清单

```
Flask>=3.0
Flask-SQLAlchemy
Flask-Mail
icalendar
werkzeug
```

前端通过 CDN 引入 Bootstrap 5 和 Chart.js（仪表盘图表）。

---

## 4. 核心功能流程

### 4.1 Survey 入库 → 自动分析与分配

```
Survey 提交（或 seed_data.py 导入）
    │
    ▼
score < 3 ?  ── No ──→ 存入数据库，无需跟进
    │
   Yes
    │
    ▼
analyzer.py 分析 comment 文本
    → 关键词匹配，返回 (ai_category, ai_confidence)
    → 写入 surveys 表
    │
    ▼
assignment.py 查找关联 incident 的 engineer_id
    → 创建 followup 记录（status=pending）
    → 若 engineer 不存在，标记 status=escalated
```

### 4.2 Engineer 处理跟进任务

```
Engineer 登录
    │
    ▼
"我的跟进任务" 页面
    → 显示 assigned 给自己的 followup 列表
    → 按优先级排序：score 越低越靠前
    │
    ▼
点击某条 followup → 查看详情
    → 客户信息、incident 摘要、survey 评分与评论
    → AI 预分类结果 + 置信度
    │
    ▼
Engineer 选择操作：
    ├─ "发送跟进邮件"
    │   → 选择/编辑邮件模板 → email_service 发送 → 记录 email_sent_at
    ├─ "安排电话回访"
    │   → 选择日期时间 → calendar_service 生成 .ics 下载 → 记录 call_scheduled_at
    └─ "记录跟进结果"
        → 确认/修正原因分类（从预设列表选择）
        → 填写 notes → 更新 status 为 completed
```

### 4.3 仪表盘

| 区块 | 内容 |
|------|------|
| 总览卡片 | 总 survey 数、平均分、低分比例（<3 分）、待跟进数 |
| 评分分布 | 1-5 分柱状图（Chart.js） |
| 低分原因分布 | 各原因分类的饼图（基于 engineer 确认后的分类） |
| 趋势图 | 按月平均分变化折线图 |
| 跟进状态 | pending / in_progress / completed / escalated 进度条 |
| 团队排行 | 各 engineer 的跟进完成率和平均处理时长 |

### 4.4 AI 分析规则引擎

关键词匹配规则：

```python
RULES = {
    "slow_response": ["slow", "wait", "long time", "delay", "week", "month"],
    "unresolved": ["not resolved", "still broken", "doesn't work", "not fixed", "same issue"],
    "poor_communication": ["no update", "didn't explain", "unclear", "no response", "ignored"],
    "lack_expertise": ["didn't understand", "wrong solution", "not qualified", "incorrect"],
    "process_issue": ["transferred", "escalation", "bounced around", "multiple teams"],
    "expectation_mismatch": ["expected", "promised", "should have", "disappointed"],
}
```

匹配逻辑：
1. 将 comment 转小写
2. 统计各分类关键词命中次数
3. 命中最多的分类胜出
4. 置信度 = 最高命中数 / 总命中数
5. 无命中时分类为 `other`，置信度为 0.0

### 4.5 邮件模板

**初次跟进邮件：**

```
Subject: Follow-up on your recent SAP Support experience - Incident #{incident_id}

Dear {customer_name},

Thank you for your feedback on incident #{incident_id}. We noticed your satisfaction
rating was {score}/5 and we take this seriously.

I'm {engineer_name}, and I'd like to understand your experience better so we can
improve our service. Could we schedule a brief call to discuss?

Best regards,
{engineer_name}
SAP Product Support
```

**问题解决确认邮件：**

```
Subject: Update on your feedback - Incident #{incident_id}

Dear {customer_name},

Following our recent conversation about incident #{incident_id}, I wanted to let you
know about the steps we've taken to address your concerns:

{notes}

We value your feedback and are committed to improving our support experience.

Best regards,
{engineer_name}
SAP Product Support
```

### 4.6 日历提醒

生成标准 `.ics` 文件：
- **标题：** `[CES Follow-up] {customer_name} - Survey #{survey_id}`
- **时间：** engineer 选择的日期时间，时长 30 分钟
- **描述：** incident 摘要 + 客户评论 + 评分
- **提醒：** 提前 15 分钟通知

---

## 5. Mock 数据策略

### 5.1 数据规模

| 实体 | 数量 |
|------|------|
| Customers | 15（APAC: 5, EMEA: 5, Americas: 5） |
| Engineers | 8（各负责不同产品领域） |
| Incidents | 50（分布在过去 6 个月） |
| Surveys | 50（每个 incident 1 个） |
| Followups | ~17（仅 score < 3 的 survey） |

### 5.2 评分分布

| 评分 | 占比 | 数量 |
|------|------|------|
| 5 | 30% | 15 |
| 4 | 25% | 13 |
| 3 | 10% | 5 |
| 2 | 20% | 10 |
| 1 | 15% | 7 |

### 5.3 评论文本

每个 survey 都有英文评论，内容与评分匹配：

- **1-2 分：** 包含明确负面关键词，可被 AI 规则引擎分类
  - `"Waited 3 weeks for a response, completely unacceptable"` → slow_response
  - `"Issue still not resolved after 2 months"` → unresolved
  - `"Engineer didn't understand our SAP BW configuration"` → lack_expertise
  - `"Was transferred 4 times before someone could help"` → process_issue
- **3 分：** 混合正负面 `"Eventually resolved but took longer than expected"`
- **4-5 分：** 正面 `"Quick and professional support, issue fixed in 2 days"`

### 5.4 跟进记录状态分布

| 状态 | 数量 | 说明 |
|------|------|------|
| pending | 5 | 待处理（新任务） |
| in_progress | 5 | 进行中（已联系客户） |
| completed | 5 | 已完成（记录了原因和结果） |
| escalated | 2 | 已升级 |

### 5.5 时间分布

- Incidents 创建时间：2025-11 至 2026-04（过去 6 个月）
- Surveys 提交时间：incident 解决后 1-7 天
- Followups 创建时间：survey 提交后 1-3 天
- Completed followup 完成时间：创建后 3-14 天

### 5.6 产品组件覆盖

SAP S/4HANA、SAP BW/4HANA、SAP SuccessFactors、SAP Ariba、SAP CRM

---

## 6. 页面清单

| 页面 | 路径 | 说明 |
|------|------|------|
| 登录 | `/login` | 邮箱 + 密码登录 |
| 仪表盘 | `/` | 统计总览（需登录） |
| Survey 列表 | `/surveys` | 全部 survey 列表，支持按评分、日期筛选 |
| Survey 详情 | `/surveys/<id>` | 单条 survey 详情 + 关联 followup |
| 我的跟进 | `/followups` | 当前 engineer 的跟进任务列表 |
| 跟进详情 | `/followups/<id>` | 跟进操作：发邮件、安排电话、记录结果 |

---

## 7. 错误处理

| 场景 | 处理方式 |
|------|---------|
| SMTP 发送失败 | 页面提示错误，记录日志，不更新 email_sent_at，允许重试 |
| Incident 的 engineer 不存在 | Followup 标记为 escalated，仪表盘显示需要手动分配 |
| AI 分析无法分类 | 标记为 other，置信度 0.0，engineer 可手动分类 |
| 未登录访问 | 重定向到 `/login` |

---

## 8. 非功能性需求

- **部署方式：** `pip install -r requirements.txt && python seed_data.py && flask run`，一条命令即可启动
- **数据持久化：** SQLite 文件存储在项目根目录 `ces.db`
- **浏览器兼容：** 现代浏览器（Chrome、Firefox、Edge）
- **无外部依赖：** 不需要 Redis、PostgreSQL 或任何外部 AI API