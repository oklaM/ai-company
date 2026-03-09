#!/usr/bin/env python3
"""
销售 AI 员工
负责自动销售和营销
"""

import json
from datetime import datetime
from pathlib import Path


class SalesAI:
    """销售 AI 员工"""

    def __init__(self):
        self.name = "sales"
        self.role = "销售营销专家"
        self.version = "v1.0"
        self.shared_dir = Path(__file__).parent.parent / "shared"
        self.logs_dir = Path(__file__).parent.parent / "logs"
        self.content_dir = Path(__file__).parent.parent / "marketing"

    def log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{self.name}] {message}"
        print(log_message)

        log_file = self.logs_dir / f"{self.name}.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")

    def get_developed_products(self) -> list:
        """获取已开发的产品"""
        opp_file = self.shared_dir / "opportunities.json"
        products = []

        if opp_file.exists():
            with open(opp_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            for opp in data.get("opportunities", []):
                if opp.get("status") == "developed":
                    products.append(opp)

        return products

    def generate_marketing_content(self, product: dict) -> str:
        """生成营销内容"""
        title = product.get("title", "产品")
        desc = product.get("description", "")

        content = f"""# {title} - 营销文案

**生成时间:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 痛点分析

客户面临的问题：
- 效率低下
- 成本高昂
- 体验不佳

## 解决方案

{desc}

## 核心优势

- ✅ **高效** - 自动化处理，节省时间
- ✅ **省钱** - 降低运营成本
- ✅ **易用** - 简单上手，无需培训

## 定价

| 版本 | 价格 | 适合 |
|------|------|------|
| 免费版 | ¥0 | 个人用户 |
| 专业版 | ¥199/月 | 小团队 |
| 企业版 | ¥999/月 | 大企业 |

## 行动号召

立即开始使用，提升您的效率！

👉 [免费试用](https://claw.ai)

---

*由 AI Sales 员工自动生成*
"""
        return content

    def save_marketing_content(self, product_name: str, content: str):
        """保存营销内容"""
        self.content_dir.mkdir(exist_ok=True)

        filename = f"{product_name.replace(' ', '-').lower()}-{datetime.now().strftime('%Y%m%d')}.md"
        content_file = self.content_dir / filename

        with open(content_file, "w", encoding="utf-8") as f:
            f.write(content)

        self.log(f"营销内容已保存: {filename}")

    def create_sales_record(self, product: dict, amount: int = 199):
        """创建销售记录（模拟）"""
        sales_file = self.shared_dir / "sales.json"

        if sales_file.exists():
            with open(sales_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {"sales": []}

        # 模拟销售
        sale = {
            "id": f"sale_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "product": product.get("title", "Unknown"),
            "amount": amount,
            "date": datetime.now().isoformat(),
            "customer": f"customer_{len(data['sales']) + 1}",
            "status": "completed"
        }

        data["sales"].append(sale)

        with open(sales_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.log(f"💰 销售成功: {sale['product']} - ¥{amount}")

        return sale

    def run(self):
        """运行销售任务"""
        self.log("开始销售工作...")

        # 获取已开发的产品
        products = self.get_developed_products()

        if products:
            for product in products[:3]:  # 最多处理3个
                # 生成营销内容
                content = self.generate_marketing_content(product)
                self.save_marketing_content(product.get("title", "product"), content)

                # 模拟销售
                sale = self.create_sales_record(product)
        else:
            self.log("没有已开发的产品可销售")
            # 生成通用营销内容
            content = self.generate_marketing_content({
                "title": "Claw AI 产品套件",
                "description": "AI 智能体基础设施，让每个 AI 都有独立身份"
            })
            self.save_marketing_content("claw-ai-suite", content)

        self.log("销售工作完成")


if __name__ == "__main__":
    ai = SalesAI()
    ai.run()
