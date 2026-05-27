from Base.Ai.base import SystemMessages, UserMessages
from Base.Ai.llms.qwenLlm import get_default_qwen_llm
from Base.Models.BaseParamsModel import BaseParamsModel
from Education.models.pojo.questionPo import QuestionPo
from Education.models.pojo.paperPo import PaperPo
from Education.models.pojo.examPo import ExamPo
from Education.models.pojo.answerPo import AnswerPo
from Education.prompts.questionPrompts import (
    single_choice_rule,
    multiple_choice_rule,
    judgement_rule,
    fill_blank_rule,
    essay_and_short_answer_rule
)


def _init_params_with_parent(
    parent_code: str,
    parent_value: str,
    parent_desc: str,
    items: str,
    item_names: dict,
    item_prefix: str = '',
    item_desc_prefix: str = ''
):
    """
    通用参数初始化函数 - 支持父级参数和子参数的初始化

    Args:
        parent_code: 父级参数编码
        parent_value: 父级参数值
        parent_desc: 父级参数描述
        items: 子项列表，用 | 分隔
        item_names: 子项名称映射字典
        item_prefix: 子项编码前缀（默认为空）
        item_desc_prefix: 子项描述前缀（默认为空）
    """
    # 检查父级参数是否存在
    parent_param = BaseParamsModel.get_param_by_code(parent_code, 'Education')

    if parent_param is None:
        # 父级参数不存在，创建父级参数
        parent = BaseParamsModel(
            code=parent_code,
            value=parent_value,
            desc=parent_desc,
            type='Education',
        )
        parent.save()
        print(f"✓ 创建父级参数成功: {parent_code}")
    else:
        print(f"✓ 父级参数已存在: {parent_code}")

    # 检查子参数是否已存在
    existing_items = BaseParamsModel.get_params_by_parent_code(parent_code, 'Education')
    existing_codes = {s['code'] for s in existing_items}

    # 遍历所有子项并插入不存在的参数
    for item in items.split('|'):
        code = f'{item_prefix}{item}' if item_prefix else item
        if code in existing_codes:
            print(f"  跳过已存在: {item_names[item]} ({item})")
            continue

        params = BaseParamsModel(
            code=code,
            value=item,
            desc=f'{item_desc_prefix}{item_names[item]}',
            parent_code=parent_code,
            type='Education',
        )
        params.save()
        print(f"✓ 插入成功: {item_names[item]} ({item})")

    print(f"\n参数初始化完成！")


def init_question_subjects():
    """初始化教育项目的学科参数"""
    _init_params_with_parent(
        parent_code='edu_subject',
        parent_value='subject',
        parent_desc='教育项目-学科类别',
        items='chinese|math|english|physics|chemistry|biology|history|geography|politics',
        item_names={
            'chinese': '语文',
            'math': '数学',
            'english': '英语',
            'physics': '物理',
            'chemistry': '化学',
            'biology': '生物',
            'history': '历史',
            'geography': '地理',
            'politics': '政治'
        },
        item_prefix='subject_',
        item_desc_prefix='教育项目-学科类别-'
    )


def init_question_types():
    """初始化教育项目的题目类型参数"""
    _init_params_with_parent(
        parent_code='edu_question_type',
        parent_value='question_type',
        parent_desc='教育项目-题目类型',
        items='single_choice|multiple_choice|fill_blank|judgement|essay|short_answer',
        item_names={
            'single_choice': '单选题',
            'multiple_choice': '多选题',
            'fill_blank': '填空题',
            'judgement': '判断题',
            'essay': '论述题',
            'short_answer': '简答题'
        },
        item_prefix='question_type_',
        item_desc_prefix='教育项目-题目类型-'
    )


def init_question_difficulty_labels():
    """初始化教育项目的难度标签参数"""
    _init_params_with_parent(
        parent_code='edu_difficulty_label',
        parent_value='difficulty_label',
        parent_desc='教育项目-难度标签',
        items='easy|medium|hard',
        item_names={
            'easy': '简单',
            'medium': '中等',
            'hard': '困难'
        },
        item_prefix='difficulty_label_',
        item_desc_prefix='教育项目-难度标签-'
    )


def init_question_rules():
    """初始化教育项目的出题规则参数"""
    parent_code = 'edu_question_rule'
    parent_value = 'question_rule'
    parent_desc = '教育项目-出题规则'

    # 检查父级参数是否存在
    parent_param = BaseParamsModel.get_param_by_code(parent_code, 'Education')

    if parent_param is None:
        # 父级参数不存在，创建父级参数
        parent = BaseParamsModel(
            code=parent_code,
            value=parent_value,
            desc=parent_desc,
            type='Education',
        )
        parent.save()
        print(f"✓ 创建父级参数成功: {parent_code}")
    else:
        print(f"✓ 父级参数已存在: {parent_code}")

    # 从 questionPrompts 导入的规则常量
    rules = {
        'single_choice': single_choice_rule,
        'multiple_choice': multiple_choice_rule,
        'judgement': judgement_rule,
        'fill_blank': fill_blank_rule,
        'essay': essay_and_short_answer_rule,
        'short_answer': essay_and_short_answer_rule
    }

    # 检查子参数是否已存在
    existing_items = BaseParamsModel.get_params_by_parent_code(parent_code, 'Education')
    existing_codes = {s['code'] for s in existing_items}

    # 遍历所有规则并插入不存在的参数
    for code, value in rules.items():
        if code in existing_codes:
            print(f"  跳过已存在: {code}")
            continue

        params = BaseParamsModel(
            code=code,
            value=value,
            desc=f'教育项目-出题规则-{code}',
            parent_code=parent_code,
            type='Education',
        )
        params.save()
        print(f"✓ 插入成功: {code}")

    print(f"\n出题规则初始化完成！")


def init_knowledge_points():
    """
    让AI遍历生成学科的知识点 , 执行比较耗时
    """
    parent_code = 'edu_knowledge_point'
    parent_value = 'knowledge_point'
    parent_desc = '教育项目-知识点'
    items = 'chinese|math|english|physics|chemistry|biology|history|geography|politics'
    grades = '小学|初中|高中|大学'

    # 学科中文名称映射
    subject_names = {
        'chinese': '语文',
        'math': '数学',
        'english': '英语',
        'physics': '物理',
        'chemistry': '化学',
        'biology': '生物',
        'history': '历史',
        'geography': '地理',
        'politics': '政治'
    }

    # 检查父级参数是否存在
    parent_param = BaseParamsModel.get_param_by_code(parent_code, 'Education')

    if parent_param is None:
        # 父级参数不存在，创建父级参数
        parent = BaseParamsModel(
            code=parent_code,
            value=parent_value,
            desc=parent_desc,
            type='Education',
        )
        parent.save()
        print(f"✓ 创建父级参数成功: {parent_code}")
    else:
        print(f"✓ 父级参数已存在: {parent_code}")

    # 检查已存在的子参数
    existing_items = BaseParamsModel.get_params_by_parent_code(parent_code, 'Education')
    existing_codes = {s['code'] for s in existing_items}

    # 获取 LLM 实例
    llm = get_default_qwen_llm()

    # 笛卡尔积：遍历所有年级和学科的组合
    grade_list = grades.split('|')
    subject_list = items.split('|')

    for grade in grade_list:
        for subject in subject_list:
            # 生成 code: grade_subject (例如: 小学_chinese)
            code = f'{grade}_{subject}'
            subject_cn = subject_names[subject]

            # 检查是否已存在
            if code in existing_codes:
                print(f"  跳过已存在: {subject_cn} - {grade} ({code})")
                continue

            try:
                # 使用 LLM 生成知识点
                user_prompt = f"""请帮我列举{subject_cn}{grade}的50个重要知识点。

                                    要求：
                                    1. 知识点要全面且有代表性
                                    2. 每个知识点要简洁明了,小于10个字
                                    3. 知识点之间用逗号分隔
                                    4. 不要包含编号或其他符号
                                    5. 直接输出知识点列表，不要有其他说明文字
                                    6. 单个知识点只包含文字，不要包含括号、逗号去对这个知识点进行解释
                                    
                                    示例：
                                    集合与元素,基本不等式,线性规划,三角函数的定义
                                    
                                    请输出50个{subject_cn}{grade}的知识点："""

                messages = [UserMessages(prompt=user_prompt)]
                response = llm.chat(messages)

                # 清理响应结果
                knowledge_points = response.strip()
                # 移除可能的引号或多余字符
                knowledge_points = knowledge_points.replace('\n', ' ').replace('，', ',').replace('。', '').replace('、', ',')
                # 移除首尾的标点符号
                knowledge_points = knowledge_points.strip('，。、,，')

                print(f"✓ 生成知识点: {subject_cn} - {grade}")
                print(f"  Code: {code}")
                print(f"  示例: {knowledge_points[:100]}...")

                # 保存到数据库
                params = BaseParamsModel(
                    code=code,
                    value=knowledge_points,
                    desc=f'教育项目-知识点-{subject_cn}-{grade}',
                    parent_code=parent_code,
                    type='Education',
                )
                params.save()
                print(f"✓ 保存成功: {subject_cn} - {grade} ({code})")
                print()

            except Exception as e:
                print(f"✗ 生成失败: {subject_cn} - {grade}, 错误: {e}")
                print()

    print(f"\n知识点初始化完成！")

def question_db_init():
    """初始化题目数据库"""
    QuestionPo.create_table()
    PaperPo.create_table()
    ExamPo.create_table()
    AnswerPo.create_table()
    init_question_subjects()
    init_question_types()
    init_question_difficulty_labels()
    init_question_rules()
    # 下面这个比较耗时，可以单独执行，不必初始化的时候执行
    init_knowledge_points()

if __name__ == '__main__':
    question_db_init()