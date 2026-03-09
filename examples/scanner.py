#!/usr/bin/env python3
"""
AI Company 数据收集器
为 OpenClaw AI 提供决策所需的数据
"""

import os
import json
import requests
import subprocess
from datetime import datetime
from pathlib import Path


class AICompanyScanner:
    """数据收集器 - 不做决策，只提供数据"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.shared_dir = self.base_dir / "shared"
        self.shared_dir.mkdir(parents=True, exist_ok=True)
        
        # GitHub Token（可选）
        self.github_token = os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            try:
                with open(Path.home() / ".git-credentials", "r") as f:
                    for line in f:
                        if "github" in line:
                            self.github_token = line.strip().split(":")[-1].split("@")[0]
                            break
            except:
                pass
    
    def scan_github_issues(self) -> list:
        """扫描 GitHub Issues"""
        opportunities = []
        
        if not self.github_token:
            return opportunities
        
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        repos = [
            ("openclaw/openclaw", ["enhancement", "help wanted"]),
            ("openclaw/skills", ["enhancement"])
        ]
        
        for repo, labels in repos:
            for label in labels:
                try:
                    url = f"https://api.github.com/repos/{repo}/issues"
                    response = requests.get(
                        url,
                        headers=headers,
                        params={"state": "open", "labels": label, "per_page": 10},
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        for issue in response.json():
                            opportunities.append({
                                "id": f"github_{repo.split('/')[1]}_{issue['number']}",
                                "source": f"github/{repo}",
                                "type": "issue",
                                "title": issue["title"],
                                "url": issue["html_url"],
                                "labels": [l["name"] for l in issue.get("labels", [])],
                                "comments": issue.get("comments", 0),
                                "created_at": issue.get("created_at", ""),
                                "scanned_at": datetime.now().isoformat()
                            })
                except:
                    pass
        
        return opportunities
    
    def check_services(self) -> dict:
        """检查服务状态"""
        services = {
            "claw-id": os.getenv("CLAW_ID_URL", "http://localhost:3000"),
            "auto-reply": os.getenv("AUTO_REPLY_URL", "http://localhost:3002"),
            "payment": os.getenv("PAYMENT_URL", "http://localhost:3010")
        }
        
        status = {}
        for name, url in services.items():
            try:
                response = requests.get(f"{url}/health", timeout=5)
                status[name] = {
                    "url": url,
                    "status": "online" if response.status_code == 200 else "error",
                    "code": response.status_code
                }
            except:
                status[name] = {
                    "url": url,
                    "status": "offline"
                }
        
        return status
    
    def get_system_resources(self) -> dict:
        """获取系统资源"""
        resources = {}
        
        # 内存
        try:
            result = subprocess.run(["free", "-m"], capture_output=True, text=True, timeout=5)
            lines = result.stdout.split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                resources["memory"] = {
                    "total_mb": int(parts[1]),
                    "used_mb": int(parts[2]),
                    "available_mb": int(parts[6]) if len(parts) > 6 else 0
                }
        except:
            pass
        
        # 磁盘
        try:
            result = subprocess.run(["df", "-h", "/home"], capture_output=True, text=True, timeout=5)
            lines = result.stdout.split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                resources["disk"] = {
                    "total": parts[1],
                    "used": parts[2],
                    "available": parts[3],
                    "percent": parts[4]
                }
        except:
            pass
        
        return resources
    
    def get_sales_data(self) -> dict:
        """获取销售数据"""
        sales_file = self.shared_dir / "sales.json"
        
        if sales_file.exists():
            with open(sales_file, "r") as f:
                data = json.load(f)
                sales = data.get("sales", [])
                
                total = sum(s.get("amount", 0) for s in sales if s.get("status") in ["completed", "pending_payment"])
                
                return {
                    "total_revenue": total,
                    "transaction_count": len(sales),
                    "recent_sales": sales[-5:]
                }
        
        return {
            "total_revenue": 0,
            "transaction_count": 0,
            "recent_sales": []
        }
    
    def run_scan(self) -> dict:
        """执行完整扫描"""
        print("🔍 AI Company 数据扫描开始...")
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "monitoring": {
                "services": self.check_services(),
                "resources": self.get_system_resources()
            },
            "opportunities": self.scan_github_issues(),
            "sales": self.get_sales_data(),
            "pending_decisions": []
        }
        
        # 生成待决策问题
        services_online = sum(1 for s in data["monitoring"]["services"].values() if s["status"] == "online")
        services_total = len(data["monitoring"]["services"])
        
        if services_online < services_total:
            data["pending_decisions"].append({
                "type": "service_recovery",
                "question": f"{services_total - services_online} 个服务离线，恢复优先级？",
                "offline_services": [k for k, v in data["monitoring"]["services"].items() if v["status"] != "online"]
            })
        
        if data["opportunities"]:
            data["pending_decisions"].append({
                "type": "opportunity_priority",
                "question": f"发现 {len(data['opportunities'])} 个机会，优先处理哪个？",
                "opportunity_ids": [o["id"] for o in data["opportunities"][:5]]
            })
        
        # 保存数据
        data_file = self.shared_dir / "scan_data.json"
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 扫描完成")
        print(f"   服务: {services_online}/{services_total} 在线")
        print(f"   机会: {len(data['opportunities'])} 个")
        print(f"   收入: ¥{data['sales']['total_revenue']}")
        print(f"   待决策: {len(data['pending_decisions'])} 个问题")
        
        return data


def main():
    scanner = AICompanyScanner()
    data = scanner.run_scan()
    
    # 输出 JSON 供 OpenClaw AI 读取
    print("\n" + "="*60)
    print("📊 扫描数据（供 AI 决策）:")
    print("="*60)
    print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
