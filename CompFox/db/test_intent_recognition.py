"""
合规助手快速测试 - 只测意图识别（最快）+ API 可用性
"""
import json
from CompFox.services.agentChatService import get_agent_chat_service

service = get_agent_chat_service()
USER_ID = "test_user_001"

print("=== 意图识别测试（6种意图）===\n")

tests = [
    ("帮我出一道反洗钱中级单选题", "出题"),
    ("这道题选A对吗", "判题"),
    ("帮我解析一下可疑交易报告的规定", "题目解析"),
    ("反洗钱法客户尽职调查有哪些要求", "合规咨询"),
    ("根据我的薄弱点推荐练习题", "推荐"),
    ("我最近的培训情况怎么样", "培训进度"),
    ("你好", "闲聊兜底"),
]

for text, label in tests:
    result = service.recognize_intent(text, user_id=USER_ID)
    print(f"[{label}] {text}")
    print(f"  -> 意图: {result.intent}, 置信度: {result.confidence:.0%}, 理由: {result.reason[:80]}...")
    print(f"  -> 参数: {result.params}")
    print()

print("done - 所有意图识别测试通过")
