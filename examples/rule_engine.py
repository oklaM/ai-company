#!/usr/bin/env python3
"""
规则引擎 - 无 AI API 时的智能决策
"""

import re
from typing import Dict, Any, List


class RuleEngine:
    """基于规则的决策引擎"""
    
    @staticmethod
    def analyze_opportunity(title: str, description: str) -> Dict:
        """分析市场机会"""
        score = 50
        priority = "medium"
        actions = []
        
        title_lower = title.lower()
        desc_lower = description.lower()
        combined = f"{title} {description}".lower()
        
        # 关键词评分
        if any(kw in combined for kw in ["支付", "payment", "billing", "订阅"]):
            score += 20
            priority = "high"
            actions.append("优先实现支付功能，这是收入关键")
        
        if any(kw in combined for kw in ["企业", "enterprise", "team", "团队"]):
            score += 15
            actions.append("企业版功能有更高付费意愿")
        
        if any(kw in combined for kw in ["api", "sdk", "集成", "integration"]):
            score += 10
            actions.append("API 功能可扩展用户群")
        
        if any(kw in combined for kw in ["安全", "security", "auth", "认证"]):
            score += 10
            actions.append("安全功能是企业必需")
        
        if any(kw in combined for kw in ["性能", "performance", "优化"]):
            score += 5
            actions.append("性能优化提升用户体验")
        
        # 难度评估
        difficulty = "medium"
        if any(kw in combined for kw in ["简单", "easy", "minor", "小"]):
            difficulty = "low"
            score += 5
        elif any(kw in combined for kw in ["复杂", "complex", "重构", "major"]):
            difficulty = "high"
            score -= 5
        
        # 限制分数范围
        score = max(0, min(100, score))
        
        return {
            "priority_score": score,
            "priority": priority,
            "difficulty": difficulty,
            "analysis": f"基于关键词分析，优先级: {priority}",
            "recommended_action": actions[0] if actions else "评估后实施"
        }
    
    @staticmethod
    def generate_marketing_content(product: Dict) -> str:
        """生成营销内容"""
        title = product.get("title", "AI 产品")
        desc = product.get("description", "智能化解决方案")
        
        # 提取关键特性
        features = []
        if "企业" in title:
            features.extend(["SSO 单点登录", "团队协作", "企业级安全"])
        if "支付" in title or "payment" in title.lower():
            features.extend(["多种支付方式", "自动续费", "发票管理"])
        if "多平台" in title or "platform" in title.lower():
            features.extend(["跨平台同步", "统一管理", "API 集成"])
        
        if not features:
            features = ["智能自动化", "简单易用", "7x24 服务"]
        
        content = f"""# {title}

> 让 AI 为你工作

## 产品介绍

{desc}

## 核心功能

"""
        for i, feature in enumerate(features, 1):
            content += f"{i}. **{feature}** - 提升效率，节省时间\n"
        
        content += f"""
## 定价

| 版本 | 价格 | 适合 |
|------|------|------|
| 免费版 | ¥0 | 个人体验 |
| 专业版 | ¥199/月 | 专业用户 |
| 企业版 | ¥999/月 | 团队协作 |

## 立即开始

👉 [免费试用](https://claw.ai)

---

*由 AI 自动生成*
"""
        return content
    
    @staticmethod
    def analyze_system_alerts(issues: List[Dict]) -> str:
        """分析系统告警"""
        if not issues:
            return "所有系统运行正常"
        
        analysis = []
        
        for issue in issues:
            if issue["type"] == "service":
                if issue.get("critical"):
                    analysis.append(f"⚠️ 严重: {issue['name']} 服务离线，需要立即恢复")
                else:
                    analysis.append(f"ℹ️ {issue['name']} 服务离线，非关键服务")
            
            elif issue["type"] == "resource":
                analysis.append(f"📊 {issue['name']} 使用率 {issue['value']} 超过阈值 {issue['threshold']}")
            
            elif issue["type"] == "process":
                analysis.append(f"🔄 {issue['name']} 进程已重启 {issue['restarts']} 次，检查日志")
        
        return "\n".join(analysis)
    
    @staticmethod
    def generate_code_for_task(task: Dict) -> str:
        """根据任务生成代码模板"""
        title = task.get("title", "")
        desc = task.get("description", "")
        
        code = f'''#!/usr/bin/env python3
"""
{title}
自动生成于: {__import__('datetime').datetime.now().isoformat()}
"""

# TODO: 实现以下功能
# {desc}

def main():
    """主函数"""
    # 1. 初始化
    print("初始化 {title}...")
    
    # 2. 执行核心逻辑
    # TODO: 添加业务逻辑
    
    # 3. 清理
    print("完成")

if __name__ == "__main__":
    main()
'''
        return code


# 全局规则引擎实例
rule_engine = RuleEngine()
