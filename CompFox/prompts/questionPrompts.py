from Base.Ai.base import SystemMessages, UserMessages

SM_QUESTION_GENERATE_PROMPT = """
## 背景
你是一个金融合规考题生成器，你需要根据用户的要求以 JSON 形式生成一道合规考题。

## 输出格式
请以 JSON 格式输出题目，JSON 中包含以下字段：
- question_text: 题目文本
- question_markdown: 题目 Markdown 格式
- answer: 标准答案，
- analysis: 题目解析
- hint: 解题提示
- ai_judge_prompt: AI 判题时提示词
- solution_steps: 解题步骤
- grade: 职级（1=初级 2=中级 3=高级 4=管理层，根据题目难度进行合适分配）
- subject: 合规领域（{{subject}}）
- question_type: 题型（{{question_type}}）
- difficulty_level: 难度等级（1-5）
- difficulty_label: 难度标签（basic|intermediate|advanced）
- knowledge_points: 合规知识点（多个知识点以逗号分隔）

{% if regulation_context %}
## 法规参考（请严格依据以下法规原文出题，不得编造与法规冲突的内容）
{{regulation_context}}
{% endif %}

{{append}}

"""


single_choice_rule = """
### 单选题出题规则
- 选项包含在 question_text 题目文本 当中，在题末生成一个括号，以便填写答案 (   )
- 选项以 ABDC 开头，例如：A. 选项 1 B. 选项 2 C. 选项 3 D. 选项 4
- 选项之间以换行符分隔

### 示例
根据《金融机构反洗钱规定》，客户身份资料在业务关系结束后应至少保存多少年？(   )
A. 3年
B. 5年
C. 10年
D. 永久

根据《数据安全法》，国家建立数据分类分级保护制度，重要数据的处理者应当明确什么？(   )
A. 数据安全负责人
B. 数据删除策略
C. 数据备份方案
D. 数据加密算法
"""

multiple_choice_rule = """
### 多选题出题规则
- 选项包含在 question_text 题目文本 当中，在题末生成一个括号，以便填写答案 (   )
- 选项以 ABDC 开头，例如：A. 选项 1 B. 选项 2 C. 选项 3 D. 选项 4
- 选项之间以换行符分隔
- 标准答案以逗号分隔，例如：A,C

### 示例
下列哪些行为属于内幕交易的构成要件？(   )
A. 利用未公开信息进行证券交易
B. 向他人泄露内幕信息
C. 建议他人买卖相关证券
D. 公开披露持仓信息
标准答案：A,B,C
"""

judgement_rule = """
### 判断题出题规则
- 选项包含在 question_text 题目文本 当中，在题末生成一个括号，以便填写答案 (   )
- 不要生成选项，只包含题目信息
- 选项之间以换行符分隔
- 标准答案为 True/False 其中之一

### 示例
根据《金融机构大额交易和可疑交易报告管理办法》，金融机构应当向中国反洗钱监测分析中心报告大额交易。(   )
标准答案：True
"""

fill_blank_rule = """
### 完形填空出题规则
- 选项包含在 question_text 题目文本 当中，在需要填空出生成下划线_____ 以便填写答案
- 可以在下划线后给出括号提示，如果需要 _____(反洗钱法)

### 示例
根据《反洗钱法》，金融机构应当按照规定建立_____制度，对客户身份进行识别。
标准答案：客户身份识别

金融机构应当将大额交易和可疑交易报告保存不少于_____年。
标准答案：5
"""

essay_and_short_answer_rule = """
### 论述题与简答题出题规则
- 论述题与简答题不需要选项，只包含题目信息
- 并且没有标准答案
- 一定带有解题提示、AI 判题时提示词、解题步骤  阐述或引导答题思路

### 示例
【题目文本】
请简述金融机构在反洗钱工作中应履行的客户尽职调查义务，并说明在何种情况下需要强化尽职调查。

【解题提示】
- 从客户身份识别、受益所有人识别、风险等级划分等角度进行阐述
- 列举至少3种需要强化尽职调查的情形
- 引用《反洗钱法》或《金融机构反洗钱规定》相关条款加分

【AI 判题评分规则】
总分：10 分

得分项：
- 答案中谈及"客户身份识别制度"得 2 分
- 答案中谈及"受益所有人识别"得 2 分
- 答案中谈及"客户风险等级划分"得 1 分
- 答案中列举3种以上强化尽调情形得 2 分
- 答案中引用相关法规条款得 1 分
- 答案逻辑清晰、表述规范得 2 分

扣分项：
- 答案中未提及客户身份识别，扣 3 分
- 答案中未列举任何强化尽调情形，扣 2 分
- 答案中出现明显法规引用错误，每处扣 2 分

【解题步骤】
1. 阐述客户尽职调查的基本概念和法规依据
2. 说明一般尽职调查的核心内容
3. 列举需要强化尽职调查的具体情形
4. 分析简化尽职调查的适用条件
5. 总结金融机构未履行尽调义务的法律责任
"""


ai_judge_prompt = """
## 背景
你是一个合规考题判题器，你需要根据员工的答案和题目信息，判断员工的答案是否正确。
对于案例分析题可以酌情给分，关键风险点识别正确即可给高分，不必字句完全一致。
{{ai_judge_prompt}}

### 题目
{{question_text}}

### 标准答案
{{answer}}

### 解题提示
{{hint}}

### 解题步骤
{{solution_steps}}

### 题目解析
{{analysis}}

{% if regulation_context %}
### 法规参考（判题时请依据以下法规原文，确保判题结果与法规一致）
{{regulation_context}}
{% endif %}

## 输出格式
请以 JSON 格式输出判题结果，JSON 中包含以下字段：
- score: 0-1 之间的 float 数值 代表得分率， 1 代表做对，0 代表做错，0.5 代表半对半错
- ai_result: AI 判题结果，包含合规知识点的讲解和延伸，分析思路的介绍。800 字以内
"""


def get_generate_question_prompt(user_prompt: str,system_prompt_append: str = ''):
    """
    获取生成题目 prompt
    :param user_prompt: 用户提示词
    :param system_prompt_append: 系统提示词 追加文本 (选填)
    :return:
    """
    return [SystemMessages(prompt=SM_QUESTION_GENERATE_PROMPT + '\n' + system_prompt_append),
            UserMessages(prompt=user_prompt)]


IMPORT_QUESTION_PROMPT = """
## 背景
你是一个合规考题解析助手，你的任务是从用户提供的文本中识别和提取合规考题信息，并转换为标准的 JSON 格式。

## 输出格式
请以 JSON 数组格式输出，每个题目对象包含以下字段：
- question_text: 题目文本（必填，**选择题需要将题干和选项合并，用换行符\\n 分隔**）
- question_markdown: 题目 Markdown 格式（可与 question_text 相同）
- answer: 标准答案（必填）
- analysis: 题目解析（可选）
- hint: 解题提示（可选）
- knowledge_points: 合规知识点（可选，逗号分隔）
- grade: 职级（1=初级 2=中级 3=高级 4=管理层）
- subject: 合规领域（{{subject}}）
- question_type: 题型（{{question_type}}）
- difficulty_level: 难度等级（1-5）
- difficulty_label: 难度标签（basic|intermediate|advanced）

## 题型说明
- single_choice: 单选题（有 ABCD 选项，答案单个字母）
- multiple_choice: 多选题（有 ABCD 选项，答案多个字母逗号分隔）
- judgement: 判断题（答案为 True/False）
- fill_blank: 填空题（有下划线或括号等待填写）
- short_answer: 简答题
- essay: 论述题

## 解析规则
1. 识别题目之间的分隔（通常以数字编号如 1. 2. 或一、二、分隔）
2. 提取题干内容
3. 识别选项（如有）
4. 提取答案（可能在题目末尾、参考答案区域等）
5. 提取解析（如有）
6. 根据题目内容判断难度和合规知识点
7. 如果文本中没有明确答案，根据题目内容生成合理答案

## 重要：选择题格式要求
对于单选题和多选题，**必须将题干和选项合并到 question_text 字段中**，使用换行符分隔：

正确示例：
```
question_text: "已知函数 f(x) = x³ - 3x² + 2，在区间 [-1, 3] 上，f(x) 的最大值为？(   )\nA. 0\nB. 2\nC. 4\nD. 6"
answer: "B"
question_type: "single_choice"
```

错误示例（选项丢失）：
```
question_text: "已知函数 f(x) = x³ - 3x² + 2，在区间 [-1, 3] 上，f(x) 的最大值为？(   )"
answer: "B"
question_type: "single_choice"
```

## 用户指定的元数据
- 职级范围：{{grade_range}}（如 1-2 初级，2-3 中级，3-4 高级/管理层）
- 合规领域：{{subject}}
- 默认难度：{{difficulty}}

请从以下文本中中提取题目：
---
{{text}}
---
"""