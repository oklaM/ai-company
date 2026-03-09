#!/usr/bin/env python3
"""
AI Company - OpenClaw 技能版
为 OpenClaw AI 提供决策数据
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def get_scan_data():
    """获取扫描数据"""
    data_file = Path(__file__).parent / "shared" / "scan_data.json"
    
    if data_file.exists():
        with open(data_file, "r", encoding="utf-8") as f:
            return json.load(f)
    
    return {"error": "No scan data available. Run scanner.py first."}


def format_for_ai(data: dict) -> str:
    """格式化数据供 AI 阅读"""
    
    output = []
    output.append("# AI Company 状态报告\n")
    output.append(f"**时间:** {data.get('timestamp', 'Unknown')}\n")
    
    # 服务状态
    monitoring = data.get("monitoring", {})
    services = monitoring.get("services", {})
    online = sum(1 for s in services.values() if s.get("status") == "online")
    total = len(services)
    
    output.append(f"\n## 📊 系统状态\n")
    output.append(f"服务: {online}/{total} 在线\n")
    
    for name, info in services.items():
        status = "✅" if info.get("status") == "online" else "❌"
        output.append(f"- {status} {name}: {info.get('status')}\n")
    
    # 市场机会
    opportunities = data.get("opportunities", [])
    output.append(f"\n## 🔍 市场机会\n")
    output.append(f"发现 {len(opportunities)} 个机会\n")
    
    for i, opp in enumerate(opportunities[:5], 1):
        output.append(f"\n{i}. **{opp.get('title')}**\n")
        output.append(f"   - 来源: {opp.get('source')}\n")
        output.append(f"   - 标签: {', '.join(opp.get('labels', []))}\n")
        output.append(f"   - URL: {opp.get('url')}\n")
    
    # 销售数据
    sales = data.get("sales", {})
    output.append(f"\n## 💰 销售数据\n")
    output.append(f"- 总收入: ¥{sales.get('total_revenue', 0)}\n")
    output.append(f"- 交易数: {sales.get('transaction_count', 0)}\n")
    
    # 待决策
    decisions = data.get("pending_decisions", [])
    if decisions:
        output.append(f"\n## ⚠️ 待决策\n")
        for d in decisions:
            output.append(f"- {d.get('question')}\n")
    
    output.append(f"\n---\n")
    output.append(f"*请 AI (CEO) 做出决策*\n")
    
    return "".join(output)


def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "scan":
            # 运行扫描
            from scanner import AICompanyScanner
            scanner = AICompanyScanner()
            data = scanner.run_scan()
            print(format_for_ai(data))
            
        elif command == "report":
            # 生成报告
            data = get_scan_data()
            print(format_for_ai(data))
            
        elif command == "json":
            # 输出 JSON
            data = get_scan_data()
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
        else:
            print(f"未知命令: {command}")
            print("用法: python main.py [scan|report|json]")
    else:
        # 默认：运行扫描并格式化
        from scanner import AICompanyScanner
        scanner = AICompanyScanner()
        data = scanner.run_scan()
        print("\n" + format_for_ai(data))


if __name__ == "__main__":
    main()
