#!/usr/bin/env python3
"""
开发者 AI 员工 - 真实实现
实际编写代码和提交
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

from .base import RealAIEmployee


class DeveloperAI(RealAIEmployee):
    """开发者 AI - 真实编写代码"""
    
    def __init__(self):
        super().__init__("developer", "开发专家")
        
        # 项目目录
        self.projects_dir = Path("/home/rowan/clawd")
        self.products_dir = self.projects_dir / "products"
    
    def analyze_codebase(self, project_path: Path) -> Dict:
        """分析代码库"""
        analysis = {
            "files": [],
            "languages": {},
            "todos": [],
            "issues": []
        }
        
        if not project_path.exists():
            return analysis
        
        # 统计文件
        for ext in ["*.py", "*.js", "*.ts", "*.md"]:
            for file in project_path.rglob(ext):
                if "node_modules" in str(file) or ".git" in str(file):
                    continue
                
                analysis["files"].append(str(file.relative_to(project_path)))
                
                # 统计语言
                lang = file.suffix[1:] if file.suffix else "unknown"
                analysis["languages"][lang] = analysis["languages"].get(lang, 0) + 1
                
                # 查找 TODO
                try:
                    with open(file, "r", encoding="utf-8", errors="ignore") as f:
                        for i, line in enumerate(f, 1):
                            if "TODO" in line or "FIXME" in line:
                                analysis["todos"].append({
                                    "file": str(file.relative_to(project_path)),
                                    "line": i,
                                    "content": line.strip()
                                })
                except:
                    pass
        
        return analysis
    
    def generate_code(self, task: Dict) -> str:
        """使用 AI 生成代码"""
        context = f"任务: {task.get('title', 'Unknown')}"
        prompt = f"""
请为以下任务生成代码：

任务标题: {task.get('title')}
任务描述: {task.get('description', '实现功能')}
技术栈: Python/Node.js

要求：
1. 代码简洁高效
2. 包含错误处理
3. 添加必要注释
4. 遵循最佳实践

直接输出代码，使用 ```python 或 ```javascript 包裹。
"""
        
        code = self.ask_ai(prompt, context)
        return code
    
    def implement_feature(self, opportunity: Dict) -> Dict:
        """实现功能"""
        self.log(f"🔧 实现功能: {opportunity.get('title')}")
        
        result = {
            "opportunity_id": opportunity.get("id"),
            "status": "pending",
            "files_created": [],
            "files_modified": [],
            "commits": []
        }
        
        # 1. 分析现有代码库
        if "企业版" in opportunity.get("title", ""):
            project_path = self.products_dir / "claw-id"
        elif "支付" in opportunity.get("title", ""):
            project_path = self.products_dir / "payment"
        elif "多平台" in opportunity.get("title", ""):
            project_path = self.products_dir / "auto-reply"
        else:
            project_path = self.projects_dir
        
        analysis = self.analyze_codebase(project_path)
        self.log(f"📊 分析代码库: {len(analysis['files'])} 文件, {len(analysis['todos'])} TODO")
        
        # 2. 生成代码
        code = self.generate_code(opportunity)
        
        # 3. 保存生成的代码
        code_dir = self.base_dir / "generated_code" / datetime.now().strftime("%Y%m%d")
        code_dir.mkdir(parents=True, exist_ok=True)
        
        code_file = code_dir / f"{opportunity.get('id', 'unknown')}.py"
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(f"# 自动生成 - {opportunity.get('title')}\n")
            f.write(f"# 时间: {datetime.now().isoformat()}\n\n")
            f.write(code)
        
        result["files_created"].append(str(code_file))
        self.log(f"✅ 代码已生成: {code_file}")
        
        # 4. 提交到 Git（如果有变更）
        try:
            # 检查是否有实际变更
            diff = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.projects_dir,
                capture_output=True,
                text=True
            )
            
            if diff.stdout.strip():
                # 有变更，提交
                subprocess.run(["git", "add", "."], cwd=self.projects_dir, check=True)
                commit_msg = f"feat: {opportunity.get('title', 'AI generated code')}"
                subprocess.run(["git", "commit", "-m", commit_msg], cwd=self.projects_dir, check=True)
                
                result["commits"].append(commit_msg)
                self.log(f"✅ 代码已提交: {commit_msg}")
            else:
                self.log("📝 无代码变更需要提交")
        except Exception as e:
            self.log(f"⚠️ Git 操作失败: {e}")
        
        result["status"] = "completed"
        return result
    
    def run(self) -> Dict[str, Any]:
        """执行开发任务"""
        self.log("🔧 开始真实开发工作...")
        
        results = {
            "analysis": {},
            "implementations": [],
            "stats": {}
        }
        
        # 1. 分析主项目
        results["analysis"]["clawd"] = self.analyze_codebase(self.projects_dir)
        self.log(f"📊 Clawd 项目: {len(results['analysis']['clawd']['files'])} 文件")
        
        # 2. 获取待开发机会
        opportunities = self.load_json("opportunities.json")
        pending = [o for o in opportunities.get("opportunities", []) 
                  if o.get("status") != "developed"][:3]
        
        # 3. 实现每个机会
        for opp in pending:
            impl = self.implement_feature(opp)
            results["implementations"].append(impl)
            
            # 更新机会状态
            opp["status"] = "developed"
            opp["developed_at"] = datetime.now().isoformat()
        
        # 4. 保存更新后的机会
        self.save_json("opportunities.json", opportunities)
        
        # 5. 统计
        results["stats"] = {
            "files_analyzed": len(results["analysis"]["clawd"]["files"]),
            "todos_found": len(results["analysis"]["clawd"]["todos"]),
            "features_implemented": len(results["implementations"])
        }
        
        self.log(f"✅ 开发完成: 实现了 {len(results['implementations'])} 个功能")
        
        return results


if __name__ == "__main__":
    ai = DeveloperAI()
    result = ai.run()
    print(json.dumps(result, indent=2, ensure_ascii=False))
