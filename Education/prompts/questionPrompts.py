from Base.Ai.base import SystemMessages, UserMessages

SM_QUESTION_GENERATE_PROMPT = """
## 背景
你是一个题目生成器，你需要根据用户的要求以 JSON 形式生成一道题目。

## 输出格式
请以 JSON 格式输出题目，JSON 中包含以下字段：
- question_text: 题目文本
- question_markdown: 题目 Markdown 格式
- answer: 标准答案，
- analysis: 题目解析
- hint: 解题提示
- ai_judge_prompt: AI 判题时提示词
- solution_steps: 解题步骤
- grade: 年级（1-12, 1-6 小学 7-9 初中 10-12 高中，根据题目难度进行合适分配）
- subject: 科目（{{subject}}）
- question_type: 题型（{{question_type}}）
- difficulty_level: 难度等级（1-5）
- difficulty_label: 难度标签（easy|medium|hard）
- knowledge_points: 知识点（多个知识点以逗号分隔）

{{append}}

"""


single_choice_rule = """
### 单选题出题规则
- 选项包含在 question_text 题目文本 当中，在题末生成一个括号，以便填写答案 (   )
- 选项以 ABDC 开头，例如：A. 选项 1 B. 选项 2 C. 选项 3 D. 选项 4
- 选项之间以换行符分隔

### 示例
HTTP 协议默认使用的端口号是？(   )
A. 21
B. 443
C. 80
D. 8080

MySQL 中用于创建数据库的语句是？(   )
A. CREATE DATABASE
B. NEW DATABASE
C. ADD DATABASE
D. MAKE DATABASE
"""

multiple_choice_rule = """
### 多选题出题规则
- 选项包含在 question_text 题目文本 当中，在题末生成一个括号，以便填写答案 (   )
- 选项以 ABDC 开头，例如：A. 选项 1 B. 选项 2 C. 选项 3 D. 选项 4
- 选项之间以换行符分隔
- 标准答案以逗号分隔，例如：A,C

### 示例
下列哪些是 Python 的内置数据类型？(   )
A. list
B. array
C. dict
D. tuple
标准答案：A,C,D
"""

judgement_rule = """
### 判断题出题规则
- 选项包含在 question_text 题目文本 当中，在题末生成一个括号，以便填写答案 (   )
- 不要生成选项，只包含题目信息
- 选项之间以换行符分隔
- 标准答案为 True/False 其中之一

### 示例
Python 是一种解释型编程语言。(   )
标准答案：True
"""

fill_blank_rule = """
### 完形填空出题规则
- 选项包含在 question_text 题目文本 当中，在需要填空出生成下划线_____ 以便填写答案
- 如果是英语完形填空，可以在下划线后给出括号提示，如果需要 _____(is)

### 示例
She _____(go) to school every day.
标准答案：goes

中国的首都是_____。
标准答案：北京
"""

essay_and_short_answer_rule = """
### 论述题与简答题出题规则
- 论述题与简答题不需要选项，只包含题目信息
- 并且没有标准答案
- 一定带有解题提示、AI 判题时提示词、解题步骤  阐述或引导答题思路

### 示例
【题目文本】
请简述 Python 中列表（list）和元组（tuple）的区别，并说明各自的使用场景。

【解题提示】
- 从可变性、语法、性能、使用场景等角度进行对比
- 举例说明何时使用列表，何时使用元组

【AI 判题评分规则】
总分：10 分

得分项：
- 答案中谈及"列表可变，元组不可变"得 3 分
- 答案中谈及"列表使用 []，元组使用 ()"得 2 分
- 答案中谈及"元组性能略优于列表"得 1 分
- 答案中谈及"元组可用于保护数据不被修改"得 2 分
- 答案中给出列表使用场景示例得 1 分
- 答案中给出元组使用场景示例得 1 分

扣分项：
- 答案中未提及可变性区别，扣 3 分
- 答案中未给出任何使用场景，扣 2 分
- 答案中出现明显错误概念，每处扣 1 分

【解题步骤】
1. 说明列表和元组的基本定义
2. 对比两者的可变性差异（列表可变，元组不可变）
3. 说明语法区别（列表用 []，元组用 ()）
4. 分析性能差异（元组略快）
5. 列举各自的使用场景并给出代码示例
"""


ai_judge_prompt = """
## 背景
你是一个题目判题器，你需要根据用户的答案和题目信息，判断用户的答案是否正确。
多选题和论述题可以酌情给分，如果是数学题，直接给出准确答案也算满分 可以省略过程
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


## 输出格式
请以 JSON 格式输出判题结果，JSON 中包含以下字段：
- score: 0-1 之间的 float 数值 代表得分率， 1 代表做对，0 代表做错，0.5 代表半对半错
- ai_result: AI 判题结果，包含知识点的讲解和延伸，解题思路的介绍。800 字以内
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
你是一个题目解析助手，你的任务是从用户提供的文本中识别和提取题目信息，并转换为标准的 JSON 格式。

## 输出格式
请以 JSON 数组格式输出，每个题目对象包含以下字段：
- question_text: 题目文本（必填，**选择题需要将题干和选项合并，用换行符\\n 分隔**）
- question_markdown: 题目 Markdown 格式（可与 question_text 相同）
- answer: 标准答案（必填）
- analysis: 题目解析（可选）
- hint: 解题提示（可选）
- knowledge_points: 知识点（可选，逗号分隔）
- grade: 年级（1-12, 1-6 小学 7-9 初中 10-12 高中）
- subject: 科目（{{subject}}）
- question_type: 题型（{{question_type}}）
- difficulty_level: 难度等级（1-5）
- difficulty_label: 难度标签（easy|medium|hard）

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
6. 根据题目内容判断难度和知识点
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
- 年级范围：{{grade_range}}（如 1-6，请在此范围内分配具体年级）
- 科目：{{subject}}
- 默认难度：{{difficulty}}

请从以下文本中中提取题目：
---
{{text}}
---
"""