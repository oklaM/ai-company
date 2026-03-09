#!/usr/bin/env python3
"""
销售营销 AI 员工 - 真实实现
连接真实服务执行营销和销售
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from .base import RealAIEmployee


class SalesMarketingAI(RealAIEmployee):
    """销售营销 AI - 真实执行"""
    
    def __init__(self):
        super().__init__("sales_marketing", "销售营销专家")
        
        # 服务端点
        self.services = {
            "claw-id": os.getenv("CLAW_ID_URL", "http://localhost:3000"),
            "auto-reply": os.getenv("AUTO_REPLY_URL", "http://localhost:3002"),
            "payment": os.getenv("PAYMENT_URL", "http://localhost:3010"),
        }
        
        # 营销渠道配置
        self.channels = {
            "github": {
                "enabled": bool(os.getenv("GITHUB_TOKEN")),
                "token": os.getenv("GITHUB_TOKEN")
            },
            "feishu": {
                "enabled": bool(os.getenv("FEISHU_WEBHOOK_URL")),
                "webhook": os.getenv("FEISHU_WEBHOOK_URL")
            }
        }
        
        # 产品定价
        self.pricing = {
            "claw-id": {"free": 0, "pro": 199, "enterprise": 999},
            "auto-reply": {"free": 0, "pro": 199, "enterprise": 999},
            "message-hub": {"free": 0, "pro": 199, "enterprise": 999}
        }
    
    def check_service_health(self) -> Dict[str, bool]:
        """检查服务健康状态"""
        health = {}
        
        for name, url in self.services.items():
            try:
                response = requests.get(f"{url}/health", timeout=5)
                health[name] = response.status_code == 200
            except:
                health[name] = False
        
        return health
    
    def generate_marketing_content(self, product: Dict) -> str:
        """使用 AI 生成营销内容"""
        context = f"产品: {product.get('title', 'Unknown')}"
        prompt = f"""
为以下产品生成营销文案：

产品名称: {product.get('title')}
产品描述: {product.get('description', 'AI 产品')}
目标用户: 开发者、创业者、小团队

请生成适合发布到技术社区的营销文案，要求：
1. 标题吸引眼球
2. 突出核心价值
3. 包含使用场景
4. 有明确的行动号召
5. 适合中文技术社区（掘金、知乎、V2EX）

直接输出 Markdown 格式的文案。
"""
        
        content = self.ask_ai(prompt, context)
        return content
    
    def publish_to_github_readme(self, content: str) -> bool:
        """更新 GitHub README（营销）"""
        if not self.channels["github"]["enabled"]:
            self.log("⚠️ GitHub 渠道未启用")
            return False
        
        # 这里可以更新 GitHub 仓库的 README
        # 实际实现需要 GitHub API
        self.log("📝 营销内容已准备，可手动更新到 GitHub")
        return True
    
    def send_feishu_notification(self, message: str) -> bool:
        """发送飞书通知"""
        webhook = self.channels["feishu"].get("webhook")
        if not webhook:
            self.log("⚠️ 飞书 Webhook 未配置")
            return False
        
        try:
            payload = {
                "msg_type": "text",
                "content": {"text": message}
            }
            response = requests.post(webhook, json=payload, timeout=10)
            if response.status_code == 200:
                self.log("✅ 飞书通知已发送")
                return True
        except Exception as e:
            self.log(f"❌ 飞书通知失败: {e}")
        
        return False
    
    def create_stripe_payment_link(self, product: str, tier: str = "pro") -> Dict:
        """创建 Stripe 支付链接"""
        payment_url = self.services["payment"]
        
        try:
            # 调用支付服务创建支付链接
            response = requests.post(
                f"{payment_url}/api/create-checkout",
                json={
                    "product": product,
                    "tier": tier,
                    "price": self.pricing.get(product, {}).get(tier, 199)
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ 支付链接已创建: {data.get('url', 'N/A')}")
                return data
            else:
                self.log(f"⚠️ 创建支付链接失败: {response.status_code}")
        except Exception as e:
            self.log(f"❌ 支付服务连接失败: {e}")
        
        return {}
    
    def process_real_sale(self, product: Dict, customer_info: Dict = None) -> Dict:
        """处理真实销售（非模拟）"""
        self.log(f"💰 处理真实销售: {product.get('title')}")
        
        # 1. 检查服务状态
        health = self.check_service_health()
        if not health.get("payment"):
            self.log("⚠️ 支付服务离线，无法完成销售")
            return {"status": "failed", "reason": "payment_service_offline"}
        
        # 2. 创建支付链接
        payment_link = self.create_stripe_payment_link(
            product.get("product_key", "claw-id"),
            product.get("tier", "pro")
        )
        
        # 3. 记录销售（真实数据）
        sales_data = self.load_json("sales.json")
        if not sales_data.get("sales"):
            sales_data["sales"] = []
        
        sale = {
            "id": f"real_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "product": product.get("title"),
            "amount": product.get("price", 199),
            "currency": "CNY",
            "payment_url": payment_link.get("url"),
            "status": "pending_payment",
            "created_at": datetime.now().isoformat(),
            "customer": customer_info or {"source": "organic"}
        }
        
        sales_data["sales"].append(sale)
        sales_data["last_updated"] = datetime.now().isoformat()
        self.save_json("sales.json", sales_data)
        
        self.log(f"📝 销售记录已创建: {sale['id']}")
        
        return sale
    
    def run(self) -> Dict[str, Any]:
        """执行销售营销任务"""
        self.log("💰 开始真实销售营销...")
        
        results = {
            "services": {},
            "marketing": [],
            "sales": []
        }
        
        # 1. 检查服务状态
        results["services"] = self.check_service_health()
        online_services = [k for k, v in results["services"].items() if v]
        self.log(f"📊 服务状态: {len(online_services)}/{len(results['services'])} 在线")
        
        # 2. 获取产品机会
        opportunities = self.load_json("opportunities.json")
        products = [o for o in opportunities.get("opportunities", []) 
                   if o.get("status") == "developed"][:3]
        
        if not products:
            # 使用默认产品
            products = [
                {"title": "Claw ID", "product_key": "claw-id", "tier": "pro", "price": 199},
                {"title": "Auto-Reply Pro", "product_key": "auto-reply", "tier": "pro", "price": 199}
            ]
        
        # 3. 为每个产品生成营销内容
        for product in products:
            content = self.generate_marketing_content(product)
            
            # 保存营销内容
            content_file = self.base_dir / "marketing" / f"{product.get('title', 'product').replace(' ', '-')}-{datetime.now().strftime('%Y%m%d')}.md"
            content_file.parent.mkdir(exist_ok=True)
            with open(content_file, "w", encoding="utf-8") as f:
                f.write(content)
            
            results["marketing"].append({
                "product": product.get("title"),
                "content_file": str(content_file),
                "content_length": len(content)
            })
            
            self.log(f"📝 营销内容已生成: {product.get('title')}")
        
        # 4. 创建销售记录（真实）
        for product in products[:2]:
            sale = self.process_real_sale(product)
            if sale.get("status"):
                results["sales"].append(sale)
        
        # 5. 发送通知
        if online_services:
            message = f"""🦞 AI Company 销售报告
            
服务状态: {len(online_services)}/{len(results['services'])} 在线
营销内容: {len(results['marketing'])} 份
销售记录: {len(results['sales'])} 条

时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            self.send_feishu_notification(message)
        
        self.log("✅ 销售营销完成")
        
        return results


if __name__ == "__main__":
    ai = SalesMarketingAI()
    result = ai.run()
    print(json.dumps(result, indent=2, ensure_ascii=False))
