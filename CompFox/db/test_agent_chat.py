"""
合规助手 Agent Chat 测试脚本
测试所有意图类型：出题、判题、解析、咨询、推荐、培训进度
"""
import asyncio
import json
from CompFox.services.agentChatService import get_agent_chat_service

service = get_agent_chat_service()
USER_ID = "test_user_001"

async def test_intent(input_text, description):
    """测试单个意图"""
    print(f"\n{'='*60}")
    print(f"【{description}】")
    print(f"用户输入: {input_text}")
    print('-'*40)

    try:
        result = await service.handle_request(
            user_input=input_text,
            user_id=USER_ID,
            is_stream=False,
            is_thinking=False,
        )
        answer = result.get('answer', str(result)) if isinstance(result, dict) else str(result)
        intent = result.get('intent', 'N/A') if isinstance(result, dict) else 'N/A'

        # 截取显示
        print(f"识别意图: {intent}")
        print(f"回复内容(前500字): {answer[:500]}")
        if isinstance(result, dict) and result.get('data'):
            data = result['data']
            if isinstance(data, dict):
                print(f"附加数据keys: {list(data.keys())}")

    except Exception as e:
        print(f"错误: {e}")

async def main():
    # 1. 出题意图
    await test_intent(
        "帮我出一道反洗钱方面的中级单选题",
        "意图1: 出题 (generate_question)"
    )

    # 2. 推荐意图
    await test_intent(
        "根据我的薄弱知识点推荐一些练习题",
        "意图2: 推荐 (recommend_questions)"
    )

    # 3. 培训进度
    await test_intent(
        "我最近的培训情况怎么样",
        "意图3: 培训进度 (learning_progress)"
    )

    # 4. 出题 - 不同场景
    await test_intent(
        "给我出一道数据安全合规的高级多选题，要难一点",
        "意图4: 出题 - 指定难度和题型"
    )

    # 5. 合规咨询
    await test_intent(
        "反洗钱法中关于客户尽职调查有哪些具体要求？",
        "意图5: 合规咨询 (chat)"
    )

    # 6. 判题意图
    await test_intent(
        "这道题我选A，帮我判断对不对",
        "意图6: 判题 (judge_answer)"
    )

    # 7. 题目解析
    await test_intent(
        "帮我解析一下反洗钱可疑交易报告的相关规定",
        "意图7: 解析 (explain_question)"
    )

    # 8. 模糊意图
    await test_intent(
        "你好，请问你能帮我做什么",
        "意图8: 模糊查询 (应识别为 chat)"
    )

    print(f"\n{'='*60}")
    print("所有测试完成")

asyncio.run(main())
