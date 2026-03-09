#!/usr/bin/env python3
"""
监控 AI 员工 - 真实实现
真实监控服务状态
"""

import os
import json
import requests
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from .base import RealAIEmployee


class MonitorAI(RealAIEmployee):
    """监控 AI - 真实系统监控"""
    
    def __init__(self):
        super().__init__("monitor", "系统监控专家")
        
        # 服务配置
        self.services = {
            "claw-id": {
                "url": os.getenv("CLAW_ID_URL", "http://localhost:3000"),
                "health_endpoint": "/health",
                "critical": True
            },
            "auto-reply": {
                "url": os.getenv("AUTO_REPLY_URL", "http://localhost:3002"),
                "health_endpoint": "/health",
                "critical": True
            },
            "payment": {
                "url": os.getenv("PAYMENT_URL", "http://localhost:3010"),
                "health_endpoint": "/health",
                "critical": True
            },
            "ai-company": {
                "url": "http://localhost:8888",
                "health_endpoint": "/health",
                "critical": False
            }
        }
    
    def check_service_health(self, name: str, config: Dict) -> Dict:
        """检查单个服务健康状态"""
        result = {
            "name": name,
            "url": config["url"],
            "status": "unknown",
            "response_time_ms": 0,
            "critical": config.get("critical", False),
            "checked_at": datetime.now().isoformat()
        }
        
        try:
            start = datetime.now()
            response = requests.get(
                f"{config['url']}{config['health_endpoint']}",
                timeout=5
            )
            elapsed = (datetime.now() - start).total_seconds() * 1000
            
            result["response_time_ms"] = round(elapsed, 2)
            result["status_code"] = response.status_code
            result["status"] = "online" if response.status_code == 200 else "error"
            
            # 尝试解析健康检查响应
            try:
                data = response.json()
                result["details"] = data
            except:
                result["details"] = response.text[:200]
        
        except requests.exceptions.Timeout:
            result["status"] = "timeout"
            result["error"] = "请求超时"
        except requests.exceptions.ConnectionError:
            result["status"] = "offline"
            result["error"] = "无法连接"
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def check_system_resources(self) -> Dict:
        """检查系统资源"""
        resources = {
            "cpu": {},
            "memory": {},
            "disk": {}
        }
        
        try:
            # CPU 使用率
            result = subprocess.run(
                ["top", "-bn1"],
                capture_output=True,
                text=True,
                timeout=5
            )
            lines = result.stdout.split("\n")
            for line in lines:
                if "%Cpu" in line:
                    parts = line.split()
                    if len(parts) > 1:
                        resources["cpu"]["usage"] = float(parts[1].replace(",", "."))
                    break
        except:
            resources["cpu"]["error"] = "无法获取"
        
        try:
            # 内存使用
            result = subprocess.run(
                ["free", "-m"],
                capture_output=True,
                text=True,
                timeout=5
            )
            lines = result.stdout.split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 3:
                    resources["memory"]["total_mb"] = int(parts[1])
                    resources["memory"]["used_mb"] = int(parts[2])
                    resources["memory"]["available_mb"] = int(parts[6]) if len(parts) > 6 else 0
        except:
            resources["memory"]["error"] = "无法获取"
        
        try:
            # 磁盘使用
            result = subprocess.run(
                ["df", "-h", "/home"],
                capture_output=True,
                text=True,
                timeout=5
            )
            lines = result.stdout.split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 5:
                    resources["disk"]["total"] = parts[1]
                    resources["disk"]["used"] = parts[2]
                    resources["disk"]["available"] = parts[3]
                    resources["disk"]["percent"] = parts[4]
        except:
            resources["disk"]["error"] = "无法获取"
        
        return resources
    
    def check_pm2_processes(self) -> Dict:
        """检查 PM2 进程"""
        processes = {}
        
        try:
            result = subprocess.run(
                ["pm2", "jlist"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                for proc in data:
                    processes[proc["name"]] = {
                        "status": proc["pm2_env"]["status"],
                        "cpu": proc["monit"]["cpu"],
                        "memory": proc["monit"]["memory"],
                        "uptime": proc["pm2_env"].get("pm_uptime", 0),
                        "restarts": proc["pm2_env"].get("restart_time", 0)
                    }
        except Exception as e:
            processes["error"] = str(e)
        
        return processes
    
    def generate_alert(self, issues: list) -> str:
        """使用 AI 生成告警分析"""
        if not issues:
            return ""
        
        context = f"发现 {len(issues)} 个系统问题"
        prompt = f"""
以下系统出现问题，请分析并给出解决方案：

{json.dumps(issues, indent=2, ensure_ascii=False)}

请返回：
1. 问题严重程度（critical/warning/info）
2. 简短分析
3. 建议的解决步骤

用简洁的中文回答。
"""
        
        return self.ask_ai(prompt, context)
    
    def run(self) -> Dict[str, Any]:
        """执行系统监控"""
        self.log("📊 开始真实系统监控...")
        
        results = {
            "services": [],
            "resources": {},
            "processes": {},
            "alerts": [],
            "ai_analysis": ""
        }
        
        issues = []
        
        # 1. 检查所有服务
        for name, config in self.services.items():
            health = self.check_service_health(name, config)
            results["services"].append(health)
            
            if health["status"] != "online":
                issues.append({
                    "type": "service",
                    "name": name,
                    "status": health["status"],
                    "critical": health["critical"]
                })
                
                self.log(f"⚠️ {name}: {health['status']}")
            else:
                self.log(f"✅ {name}: online ({health['response_time_ms']}ms)")
        
        # 2. 检查系统资源
        results["resources"] = self.check_system_resources()
        
        # 检查资源告警
        cpu_usage = results["resources"].get("cpu", {}).get("usage", 0)
        if cpu_usage > 80:
            issues.append({
                "type": "resource",
                "name": "cpu",
                "value": cpu_usage,
                "threshold": 80
            })
        
        disk_percent = results["resources"].get("disk", {}).get("percent", "0%")
        if int(disk_percent.replace("%", "")) > 90:
            issues.append({
                "type": "resource",
                "name": "disk",
                "value": disk_percent,
                "threshold": "90%"
            })
        
        # 3. 检查 PM2 进程
        results["processes"] = self.check_pm2_processes()
        
        # 检查进程重启次数
        for name, proc in results["processes"].items():
            if isinstance(proc, dict) and proc.get("restarts", 0) > 3:
                issues.append({
                    "type": "process",
                    "name": name,
                    "restarts": proc["restarts"]
                })
        
        # 4. 生成告警
        if issues:
            results["alerts"] = issues
            results["ai_analysis"] = self.generate_alert(issues)
            self.log(f"⚠️ 发现 {len(issues)} 个问题")
        else:
            self.log("✅ 所有系统正常")
        
        # 5. 保存报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "services_online": sum(1 for s in results["services"] if s["status"] == "online"),
                "services_total": len(results["services"]),
                "issues_count": len(issues)
            },
            "details": results
        }
        
        reports_dir = self.base_dir / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / f"health-{datetime.now().strftime('%Y-%m-%d')}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.log(f"📄 健康报告已保存: {report_file}")
        
        return report


if __name__ == "__main__":
    ai = MonitorAI()
    result = ai.run()
    print(json.dumps(result, indent=2, ensure_ascii=False))
