#!/usr/bin/env python3
"""
AI 员工基类 - 真实 AI 实现
"""

import os
import json
import time
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class RealAIEmployee(ABC):
    """真实的 AI 员工基类"""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.version = "v1.0"
        
        # 目录设置
        self.base_dir = Path(__file__).parent.parent
        self.shared_dir = self.base_dir / "shared"
        self.logs_dir = self.base_dir / "logs"
        self.prompts_dir = self.base_dir / "prompts" / name
        
        # 确保目录存在
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化 AI 客户端
        self.ai_client = self._init_ai_client()
        
        # 加载提示词
        self.system_prompt = self._load_prompt()
    
    def _init_ai_client(self):
        """初始化 AI 客户端"""
        # 优先使用智谱 AI
        zhipuai_key = os.getenv("ZHIPUAI_API_KEY")
        if zhipuai_key:
            try:
                from zhipuai import ZhipuAI
                client = ZhipuAI(api_key=zhipuai_key)
                self.log("✅ 已连接智谱 AI")
                return ("zhipu", client)
            except ImportError:
                self.log("⚠️ zhipuai 未安装，尝试安装...")
                os.system("pip install zhipuai -q")
                try:
                    from zhipuai import ZhipuAI
                    client = ZhipuAI(api_key=zhipuai_key)
                    self.log("✅ 已连接智谱 AI")
                    return ("zhipu", client)
                except:
                    pass
        
        # 回退到 OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            try:
                import openai
                client = openai.Client(api_key=openai_key)
                self.log("✅ 已连接 OpenAI")
                return ("openai", client)
            except ImportError:
                pass
        
        self.log("❌ 未找到可用的 AI API")
        return None
    
    def _load_prompt(self) -> str:
        """加载提示词"""
        prompt_file = self.prompts_dir / "system.md"
        if prompt_file.exists():
            with open(prompt_file, "r", encoding="utf-8") as f:
                return f.read()
        
        # 返回默认提示词
        return f"""你是一个 {self.role}。

你是一个真实公司的 AI 员工，需要执行真实的工作任务。

重要原则：
1. 只返回可执行的具体行动，不要返回模糊的建议
2. 基于真实数据做决策，不要编造信息
3. 如果缺少必要信息，明确指出需要什么
4. 输出格式必须是结构化的 JSON

当前角色：{self.role}
"""
    
    def log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{self.name}] {message}"
        print(log_message)
        
        # 写入日志文件
        log_file = self.logs_dir / f"{self.name}.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_message + "\n")
    
    def ask_ai(self, prompt: str, context: str = "") -> str:
        """向 AI 提问"""
        if not self.ai_client:
            self.log("⚠️ AI 客户端未初始化，返回模拟响应")
            return self._mock_response(prompt)
        
        client_type, client = self.ai_client
        
        try:
            if client_type == "zhipu":
                response = client.chat.completions.create(
                    model="glm-4-flash",
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": f"{context}\n\n{prompt}"}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                return response.choices[0].message.content
            
            elif client_type == "openai":
                response = client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": f"{context}\n\n{prompt}"}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                return response.choices[0].message.content
        
        except Exception as e:
            self.log(f"❌ AI 调用失败: {e}")
            return self._mock_response(prompt)
    
    def _mock_response(self, prompt: str) -> str:
        """规则引擎响应（AI 不可用时）"""
        from .rule_engine import rule_engine
        
        # 使用规则引擎生成智能响应
        return json.dumps({
            "status": "rule_engine",
            "message": "使用规则引擎决策",
            "note": "配置 ZHIPUAI_API_KEY 可获得更智能的决策"
        })
    
    def load_json(self, filename: str) -> Dict[str, Any]:
        """加载 JSON 文件"""
        filepath = self.shared_dir / filename
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    
    def save_json(self, filename: str, data: Dict[str, Any]):
        """保存 JSON 文件"""
        filepath = self.shared_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @abstractmethod
    def run(self) -> Dict[str, Any]:
        """执行工作任务（子类实现）"""
        pass
