#!/usr/bin/env python3
"""
财务 AI 员工 - 真实实现
真实追踪收入和支出
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from .base import RealAIEmployee


class FinanceAI(RealAIEmployee):
    """财务 AI - 真实财务追踪"""
    
    def __init__(self):
        super().__init__("finance", "财务专家")
        
        # Stripe API
        self.stripe_key = os.getenv("STRIPE_SECRET_KEY")
        
        # 支付服务
        self.payment_url = os.getenv("PAYMENT_URL", "http://localhost:3010")
    
    def get_stripe_balance(self) -> Dict:
        """获取 Stripe 余额（真实）"""
        if not self.stripe_key:
            return {"error": "STRIPE_SECRET_KEY 未配置"}
        
        try:
            import stripe
            stripe.api_key = self.stripe_key
            
            balance = stripe.Balance.retrieve()
            
            return {
                "available": [{
                    "currency": b["currency"],
                    "amount": b["amount"] / 100
                } for b in balance.available],
                "pending": [{
                    "currency": b["currency"],
                    "amount": b["amount"] / 100
                } for b in balance.pending]
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_stripe_charges(self, days: int = 7) -> Dict:
        """获取 Stripe 收款记录（真实）"""
        if not self.stripe_key:
            return {"error": "STRIPE_SECRET_KEY 未配置", "charges": []}
        
        try:
            import stripe
            stripe.api_key = self.stripe_key
            
            from datetime import datetime, timedelta
            
            charges = stripe.Charge.list(
                created={
                    "gte": int((datetime.now() - timedelta(days=days)).timestamp())
                },
                limit=100
            )
            
            result = {
                "total_count": len(charges.data),
                "total_amount": sum(c.amount for c in charges.data if c.status == "succeeded") / 100,
                "charges": [
                    {
                        "id": c.id,
                        "amount": c.amount / 100,
                        "currency": c.currency,
                        "status": c.status,
                        "created": datetime.fromtimestamp(c.created).isoformat(),
                        "description": c.description
                    }
                    for c in charges.data[:20]
                ]
            }
            
            return result
        except Exception as e:
            return {"error": str(e), "charges": []}
    
    def get_local_sales(self) -> Dict:
        """获取本地销售记录"""
        sales_data = self.load_json("sales.json")
        
        sales = sales_data.get("sales", [])
        
        # 统计
        total_revenue = sum(s.get("amount", 0) for s in sales if s.get("status") in ["completed", "pending_payment"])
        
        # 按产品分组
        by_product = {}
        for sale in sales:
            product = sale.get("product", "Unknown")
            by_product[product] = by_product.get(product, 0) + sale.get("amount", 0)
        
        # 按日期分组
        by_date = {}
        for sale in sales:
            date = sale.get("created_at", sale.get("date", ""))[:10]
            by_date[date] = by_date.get(date, 0) + sale.get("amount", 0)
        
        return {
            "total_revenue": total_revenue,
            "transaction_count": len(sales),
            "by_product": by_product,
            "by_date": by_date,
            "recent_sales": sales[-10:]
        }
    
    def generate_report_with_ai(self, data: Dict) -> str:
        """使用 AI 生成财务报告"""
        context = "财务数据分析"
        prompt = f"""
基于以下财务数据生成报告：

{json.dumps(data, indent=2, ensure_ascii=False)}

请生成：
1. 收入总览
2. 按产品/服务分类
3. 趋势分析
4. 建议的下一步行动

用 Markdown 格式输出中文报告。
"""
        
        return self.ask_ai(prompt, context)
    
    def run(self) -> Dict[str, Any]:
        """执行财务分析"""
        self.log("📈 开始真实财务分析...")
        
        results = {
            "stripe": {},
            "local_sales": {},
            "summary": {},
            "report": ""
        }
        
        # 1. 获取 Stripe 数据（如果配置了）
        if self.stripe_key:
            self.log("💳 获取 Stripe 数据...")
            results["stripe"]["balance"] = self.get_stripe_balance()
            results["stripe"]["charges"] = self.get_stripe_charges(days=7)
            
            if results["stripe"]["charges"].get("total_amount"):
                self.log(f"💰 Stripe 7日收入: ${results['stripe']['charges']['total_amount']}")
        else:
            self.log("⚠️ Stripe 未配置，跳过")
        
        # 2. 获取本地销售数据
        results["local_sales"] = self.get_local_sales()
        self.log(f"📊 本地销售: ¥{results['local_sales']['total_revenue']} ({results['local_sales']['transaction_count']} 笔)")
        
        # 3. 汇总
        results["summary"] = {
            "local_revenue_cny": results["local_sales"]["total_revenue"],
            "local_transactions": results["local_sales"]["transaction_count"],
            "stripe_revenue_usd": results["stripe"].get("charges", {}).get("total_amount", 0),
            "stripe_transactions": results["stripe"].get("charges", {}).get("total_count", 0),
            "currency": "CNY (local) / USD (Stripe)"
        }
        
        # 4. AI 生成报告
        results["report"] = self.generate_report_with_ai(results["summary"])
        
        # 5. 保存报告
        reports_dir = self.base_dir / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / f"finance-{datetime.now().strftime('%Y-%m-%d')}.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(f"# Claw AI 财务报告\n\n")
            f.write(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(results["report"])
        
        self.log(f"📄 财务报告已保存: {report_file}")
        
        return results


if __name__ == "__main__":
    ai = FinanceAI()
    result = ai.run()
    print(json.dumps(result, indent=2, ensure_ascii=False))
