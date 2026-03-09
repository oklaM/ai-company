#!/usr/bin/env python3
"""
市场研究 AI 员工 - 真实实现
扫描 GitHub、分析市场机会
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from .base import RealAIEmployee


class MarketResearcherAI(RealAIEmployee):
    """市场研究 AI - 真实扫描和分析"""
    
    def __init__(self):
        super().__init__("market_researcher", "市场研究专家")
        
        # GitHub Token
        self.github_token = os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            # 尝试从 .git-credentials 读取
            try:
                with open(Path.home() / ".git-credentials", "r") as f:
                    for line in f:
                        if "github" in line:
                            self.github_token = line.strip().split(":")[-1].split("@")[0]
                            break
            except:
                pass
        
        # 扫描目标
        self.scan_targets = [
            {"type": "github_issues", "repo": "openclaw/openclaw", "labels": ["enhancement", "help wanted"]},
            {"type": "github_issues", "repo": "openclaw/skills", "labels": ["enhancement"]},
            {"type": "github_trending", "language": "python", "since": "weekly"},
        ]
    
    def scan_github_issues(self, repo: str, labels: List[str]) -> List[Dict]:
        """扫描 GitHub Issues"""
        opportunities = []
        
        if not self.github_token:
            self.log("⚠️ 未配置 GITHUB_TOKEN，跳过 GitHub 扫描")
            return opportunities
        
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        for label in labels:
            url = f"https://api.github.com/repos/{repo}/issues"
            params = {"state": "open", "labels": label, "per_page": 10}
            
            try:
                response = requests.get(url, headers=headers, params=params, timeout=10)
                if response.status_code == 200:
                    issues = response.json()
                    for issue in issues:
                        opportunities.append({
                            "id": f"github_{repo.split('/')[1]}_{issue['number']}",
                            "source": f"github/{repo}",
                            "type": "github_issue",
                            "title": issue["title"],
                            "description": issue.get("body", "")[:500] if issue.get("body") else "",
                            "url": issue["html_url"],
                            "priority": "high" if "help wanted" in label else "medium",
                            "potential_revenue": self._estimate_revenue(issue["title"]),
                            "scanned_at": datetime.now().isoformat()
                        })
                    self.log(f"✅ 扫描 {repo} 标签 {label}: 发现 {len(issues)} 个 issue")
                else:
                    self.log(f"⚠️ 扫描 {repo} 失败: {response.status_code}")
            except Exception as e:
                self.log(f"❌ 扫描 {repo} 出错: {e}")
        
        return opportunities
    
    def scan_github_trending(self, language: str = "python", since: str = "weekly") -> List[Dict]:
        """扫描 GitHub Trending（通过网页抓取）"""
        opportunities = []
        
        try:
            # 使用非官方 API
            url = f"https://api.gitterapp.com/repositories?language={language}&since={since}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                repos = response.json()[:5]
                for repo in repos:
                    opportunities.append({
                        "id": f"trending_{repo.get('name', '').replace('/', '_')}",
                        "source": "github_trending",
                        "type": "trend_analysis",
                        "title": f"趋势分析: {repo.get('name', 'Unknown')}",
                        "description": repo.get("description", "")[:500],
                        "url": repo.get("url", ""),
                        "stars": repo.get("stars", 0),
                        "priority": "medium",
                        "potential_revenue": 1000,
                        "scanned_at": datetime.now().isoformat()
                    })
                self.log(f"✅ 扫描 GitHub Trending ({language}): 发现 {len(repos)} 个项目")
        except Exception as e:
            self.log(f"⚠️ GitHub Trending 扫描失败: {e}")
        
        return opportunities
    
    def _estimate_revenue(self, title: str) -> int:
        """估算潜在收入"""
        title_lower = title.lower()
        
        if any(kw in title_lower for kw in ["支付", "payment", "billing", "订阅"]):
            return 5000
        elif any(kw in title_lower for kw in ["企业", "enterprise", "team", "团队"]):
            return 3000
        elif any(kw in title_lower for kw in ["api", "sdk", "集成"]):
            return 2000
        else:
            return 1000
    
    def analyze_with_ai(self, opportunities: List[Dict]) -> List[Dict]:
        """使用 AI 或规则引擎分析机会"""
        if not opportunities:
            return []
        
        # 尝试使用 AI
        if self.ai_client:
            context = f"发现 {len(opportunities)} 个市场机会，请分析并排序。"
            prompt = f"""
以下是扫描到的市场机会：

{json.dumps(opportunities[:10], indent=2, ensure_ascii=False)}

请分析这些机会并返回 JSON 格式：
{{
  "analyzed_opportunities": [
    {{
      "id": "原始ID",
      "priority_score": 1-100,
      "analysis": "简短分析",
      "recommended_action": "建议行动"
    }}
  ],
  "top_pick": "最优先的机会ID",
  "reasoning": "选择理由"
}}
"""
            
            response = self.ask_ai(prompt, context)
            
            try:
                result = json.loads(response)
                for analyzed in result.get("analyzed_opportunities", []):
                    for opp in opportunities:
                        if opp["id"] == analyzed["id"]:
                            opp["priority_score"] = analyzed.get("priority_score", 50)
                            opp["analysis"] = analyzed.get("analysis", "")
                            opp["recommended_action"] = analyzed.get("recommended_action", "")
                            break
                
                self.log(f"🤖 AI 分析完成，推荐: {result.get('top_pick', 'N/A')}")
                return opportunities
            except:
                pass
        
        # 使用规则引擎
        from .rule_engine import rule_engine
        self.log("📊 使用规则引擎分析机会...")
        
        for opp in opportunities:
            analysis = rule_engine.analyze_opportunity(
                opp.get("title", ""),
                opp.get("description", "")
            )
            opp["priority_score"] = analysis["priority_score"]
            opp["priority"] = analysis["priority"]
            opp["difficulty"] = analysis["difficulty"]
            opp["analysis"] = analysis["analysis"]
            opp["recommended_action"] = analysis["recommended_action"]
        
        # 按分数排序
        opportunities.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
        
        self.log(f"✅ 规则引擎分析完成")
        return opportunities
    
    def run(self) -> Dict[str, Any]:
        """执行市场研究"""
        self.log("🔍 开始真实市场研究...")
        
        all_opportunities = []
        
        # 1. 扫描 GitHub Issues
        for target in self.scan_targets:
            if target["type"] == "github_issues":
                opps = self.scan_github_issues(target["repo"], target["labels"])
                all_opportunities.extend(opps)
            elif target["type"] == "github_trending":
                opps = self.scan_github_trending(target["language"], target["since"])
                all_opportunities.extend(opps)
        
        # 2. AI 分析
        analyzed_opportunities = self.analyze_with_ai(all_opportunities)
        
        # 3. 保存结果
        opportunities_data = self.load_json("opportunities.json")
        if not opportunities_data.get("opportunities"):
            opportunities_data["opportunities"] = []
        
        # 添加新机会（去重）
        existing_ids = {o["id"] for o in opportunities_data["opportunities"]}
        for opp in analyzed_opportunities:
            if opp["id"] not in existing_ids:
                opportunities_data["opportunities"].append(opp)
                existing_ids.add(opp["id"])
        
        # 限制数量
        opportunities_data["opportunities"] = opportunities_data["opportunities"][-50:]
        opportunities_data["last_scan"] = datetime.now().isoformat()
        opportunities_data["total_count"] = len(opportunities_data["opportunities"])
        
        self.save_json("opportunities.json", opportunities_data)
        
        self.log(f"✅ 市场研究完成: 发现 {len(analyzed_opportunities)} 个新机会")
        
        return {
            "status": "success",
            "new_opportunities": len(analyzed_opportunities),
            "total_opportunities": opportunities_data["total_count"],
            "top_opportunities": sorted(analyzed_opportunities, key=lambda x: x.get("priority_score", 0), reverse=True)[:3]
        }


if __name__ == "__main__":
    ai = MarketResearcherAI()
    result = ai.run()
    print(json.dumps(result, indent=2, ensure_ascii=False))
