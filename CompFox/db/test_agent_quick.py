"""
合规助手快速测试 - 只测 3 个核心意图
"""
import asyncio
import json
from CompFox.services.agentChatService import get_agent_chat_service

service = get_agent_chat_service()
USER_ID = "test_user_001"

async def test(input_text, label):
    print(f"\n{'='*50}")
    print(f"【{label}】")
    print(f"输入: {input_text}")

    result = await service.handle_request(
        user_input=input_text,
        user_id=USER_ID,
        is_stream=False,
    )

    if isinstance(result, dict):
        intent = result.get('intent', '?')
        answer = result.get('answer', '')
        print(f"意图: {intent}")
        print(f"回答: {answer[:400]}")
        if 'data' in result and result['data']:
            print(f"数据: {json.dumps(result['data'], ensure_ascii=False, default=str)[:300]}")
    else:
        print(f"结果: {str(result)[:400]}")

async def main():
    await test("帮我出一道反洗钱中级单选题", "出题")
    await test("反洗钱法中客户尽职调查有哪些要求", "合规咨询")
    await test("根据我的薄弱点推荐练习题", "推荐题目")

asyncio.run(main())
