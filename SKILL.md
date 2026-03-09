---
name: ai-company
description: AI 公司自动化运营技能 - 利用 OpenClaw AI 实现完全自主的公司运营
---

# AI Company 自动化运营技能

## 概述

这是一个 **OpenClaw 原生技能**，直接使用 OpenClaw 的 AI 能力，无需额外配置 API Key。

**核心理念**：技能提供工作流和数据，OpenClaw AI 提供智能决策。

## 与 OpenClaw AI 协作方式

### 1. AI 作为 CEO 决策者

当技能运行时，OpenClaw AI（你）扮演 CEO 角色：
- 分析市场机会
- 决定开发优先级
- 审批营销内容
- 制定销售策略
- 审查财务报告

### 2. 技能提供数据和工具

技能负责：
- 扫描 GitHub Issues
- 分析代码库
- 监控系统状态
- 收集销售数据
- 生成报告

### 3. AI 做决策

关键决策由 AI 完成：
- 哪个机会最值得投入？
- 营销文案是否合适？
- 定价策略如何调整？
- 是否需要人工介入？

## 使用方式

### 在 OpenClaw 中运行

```
用户: 运行 AI 公司工作循环

AI (CEO): 
📊 阶段1: 系统监控
[技能执行] 扫描服务状态...
[AI 决策] 发现 payment 服务离线，优先级：高，建议：立即恢复

🔍 阶段2: 市场研究  
[技能执行] 扫描 GitHub Issues...
[技能数据] 发现 11 个新机会
[AI 决策] 最优先：#123 支付功能增强 - 原因：直接关联收入

💰 阶段3: 销售决策
[技能数据] 本地收入 ¥7761
[AI 决策] 建议加大营销投入，重点推广 Claw ID 企业版

✅ 工作循环完成
```

### 交互式决策

```
用户: AI 公司发现了哪些机会？

AI: 扫描到 11 个市场机会，我分析后认为最优先的是：

1. **支付功能增强** (GitHub #123)
   - 优先级：高
   - 原因：直接关联收入转化
   - 建议：本周内完成

2. **企业版 SSO** (GitHub #456)
   - 优先级：中
   - 原因：提升企业客户付费意愿
   - 建议：下个迭代

你觉得这个优先级合理吗？
```

## 技能输出格式

技能会生成结构化数据供 AI 分析：

```json
{
  "monitoring": {
    "services": {"online": 0, "total": 4},
    "issues": ["claw-id offline", "payment offline"]
  },
  "opportunities": [
    {
      "id": "github_123",
      "title": "支付功能增强",
      "source": "GitHub Issue",
      "score": 85
    }
  ],
  "sales": {
    "local_revenue": 7761,
    "transactions": 39
  },
  "pending_decisions": [
    "是否优先开发支付功能？",
    "营销预算如何分配？",
    "服务恢复优先级？"
  ]
}
```

## AI 决策权限

### 自动决策（无需人工）
- ✅ 扫描数据收集
- ✅ 生成报告
- ✅ 代码模板生成
- ✅ 日常监控

### 建议，需人工确认
- ⚠️ 提交代码到 Git
- ⚠️ 发布营销内容
- ⚠️ 调整定价
- ⚠️ 大额支出

### 必须人工批准
- 🔒 部署到生产环境
- 🔒 发送外部消息
- 🔒 财务操作

## 快速开始

### 1. 初始化 AI 公司

```bash
# 使用技能创建项目
cd /path/to/workspace
python3 /path/to/ai-company/examples/init_ai_company.py my-company
```

### 2. 在 OpenClaw 中启用

```
用户: 启用 ai-company 技能

AI: ✅ AI Company 技能已启用

当前状态：
- 项目位置: ~/workspace/my-company
- 运行模式: OpenClaw AI 决策
- 自动化: 每 30 分钟扫描一次

我可以：
1. 运行完整工作循环
2. 仅执行市场研究
3. 查看当前状态
4. 分析某个机会

需要我做什么？
```

### 3. 日常运营

```
用户: 每天早上 9 点运行 AI 公司

AI: ✅ 已设置定时任务

每天 09:00 我会：
1. 扫描 GitHub 新 Issue
2. 检查服务状态
3. 生成日报并发送给你

第一次运行将在明天 09:00
```

## 架构优势

### 对比独立程序

| 特性 | 独立程序 | OpenClaw 技能 |
|------|---------|--------------|
| AI 决策 | 需要额外 API Key | ✅ 使用 OpenClaw AI |
| 交互方式 | 命令行 | ✅ 自然语言 |
| 灵活性 | 固定逻辑 | ✅ AI 可调整 |
| 集成度 | 独立运行 | ✅ 与其他技能协作 |
| 成本 | 需付费 API | ✅ 使用现有 AI |

### 与其他技能协作

```
AI: 检测到新的 GitHub Issue 关于支付功能

[ai-company] 创建机会记录
[github-auto-reply] 自动回复感谢反馈
[coding-agent] 生成实现方案
[ai-company] 追踪开发进度

完全自动化的闭环！
```

## 配置文件

### config.yaml

```yaml
company:
  name: "My AI Company"
  
automation:
  schedule:
    market_scan: "*/30 * * * *"  # 每 30 分钟
    daily_report: "0 9 * * *"     # 每天 9 点
    
integrations:
  github:
    repos:
      - openclaw/openclaw
      - openclaw/skills
    labels:
      - enhancement
      - help wanted
      
  services:
    claw-id: "http://localhost:3000"
    auto-reply: "http://localhost:3002"
    payment: "http://localhost:3010"
    
decision_mode: "openclaw_ai"  # 使用 OpenClaw AI 决策
```

## 实际案例

### 案例 1: 发现新机会

```
[09:00] 技能扫描到 GitHub Issue #789
[09:00] AI 分析：高优先级，建议立即处理
[09:01] AI 回复用户：

"发现一个高价值机会！

GitHub Issue #789: 添加 Webhook 支持
- 需求强烈（15 👍）
- 实现难度：中等
- 预计收入影响：+20%

建议优先开发。要我生成实现方案吗？"
```

### 案例 2: 自动化营销

```
[14:00] 技能检测到 Claw ID 功能完成
[14:00] AI 生成营销文案
[14:01] AI 请求确认：

"Claw ID 企业版已就绪，我生成了营销文案：

[营销内容预览...]

是否发布到：
1. 掘金
2. 知乎  
3. 仅保存

请选择..."
```

## 下一步

1. **初始化项目** - `python3 init_ai_company.py my-company`
2. **在 OpenClaw 中启用** - "启用 ai-company 技能"
3. **设置自动化** - "每天 9 点运行工作循环"
4. **监控进展** - "查看 AI 公司日报"

---

**记住：你（OpenClaw AI）就是这家公司的 CEO！**

技能提供数据和工作流，你提供智慧和决策。
