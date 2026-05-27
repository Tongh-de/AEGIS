from Base.Config.logConfig import setup_logging

setup_logging()

import Base.Repository  # triggers register_default_connection() before any DB ops

from Base.Ai.base import SystemMessages, UserMessages
from Base.Ai.llms.qwenLlm import get_default_qwen_llm
from Base.Models.BaseParamsModel import BaseParamsModel
from CompFox.models.pojo.questionPo import QuestionPo
from CompFox.models.pojo.paperPo import PaperPo
from CompFox.models.pojo.examPo import ExamPo
from CompFox.models.pojo.answerPo import AnswerPo
from CompFox.prompts.questionPrompts import (
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
    parent_param = BaseParamsModel.get_param_by_code(parent_code, 'CompFox')

    if parent_param is None:
        # 父级参数不存在，创建父级参数
        parent = BaseParamsModel(
            code=parent_code,
            value=parent_value,
            desc=parent_desc,
            type='CompFox',
        )
        result = parent.save()
        if result != -1:
            print(f"✓ 创建父级参数成功: {parent_code}")
        else:
            print(f"✗ 创建父级参数失败: {parent_code}")
    else:
        print(f"✓ 父级参数已存在: {parent_code}")

    # 检查子参数是否已存在
    existing_items = BaseParamsModel.get_params_by_parent_code(parent_code, 'CompFox')
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
            type='CompFox',
        )
        result = params.save()
        if result != -1:
            print(f"✓ 插入成功: {item_names[item]} ({item})")
        else:
            print(f"✗ 插入失败: {item_names[item]} ({item})")

    print(f"\n参数初始化完成！")


def init_question_subjects():
    """初始化合规领域参数"""
    _init_params_with_parent(
        parent_code='compfox_subject',
        parent_value='subject',
        parent_desc='CompFox-合规领域',
        items='aml|data_security|insider_trading|market_manipulation|investor_protection|compliance_management|code_of_conduct',
        item_names={
            'aml': '反洗钱',
            'data_security': '数据安全',
            'insider_trading': '内幕交易',
            'market_manipulation': '市场操纵',
            'investor_protection': '投资者保护',
            'compliance_management': '合规管理',
            'code_of_conduct': '行为准则'
        },
        item_prefix='subject_',
        item_desc_prefix='CompFox-合规领域-'
    )


def init_question_types():
    """初始化题型参数"""
    _init_params_with_parent(
        parent_code='compfox_question_type',
        parent_value='question_type',
        parent_desc='CompFox-题型',
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
        item_desc_prefix='CompFox-题型-'
    )


def init_question_difficulty_labels():
    """初始化难度标签参数"""
    _init_params_with_parent(
        parent_code='compfox_difficulty_label',
        parent_value='difficulty_label',
        parent_desc='CompFox-难度标签',
        items='basic|intermediate|advanced',
        item_names={
            'basic': '基础',
            'intermediate': '中级',
            'advanced': '高级'
        },
        item_prefix='difficulty_label_',
        item_desc_prefix='CompFox-难度标签-'
    )


def init_question_rules():
    """初始化出题规则参数"""
    parent_code = 'compfox_question_rule'
    parent_value = 'question_rule'
    parent_desc = 'CompFox-出题规则'

    # 检查父级参数是否存在
    parent_param = BaseParamsModel.get_param_by_code(parent_code, 'CompFox')

    if parent_param is None:
        # 父级参数不存在，创建父级参数
        parent = BaseParamsModel(
            code=parent_code,
            value=parent_value,
            desc=parent_desc,
            type='CompFox',
        )
        result = parent.save()
        if result != -1:
            print(f"✓ 创建父级参数成功: {parent_code}")
        else:
            print(f"✗ 创建父级参数失败: {parent_code}")
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
    existing_items = BaseParamsModel.get_params_by_parent_code(parent_code, 'CompFox')
    existing_codes = {s['code'] for s in existing_items}

    # 遍历所有规则并插入不存在的参数
    for code, value in rules.items():
        if code in existing_codes:
            print(f"  跳过已存在: {code}")
            continue

        params = BaseParamsModel(
            code=code,
            value=value,
            desc=f'CompFox-出题规则-{code}',
            parent_code=parent_code,
            type='CompFox',
        )
        result = params.save()
        if result != -1:
            print(f"✓ 插入成功: {code}")
        else:
            print(f"✗ 插入失败: {code}")

    print(f"\n出题规则初始化完成！")


def init_knowledge_points():
    """
    让AI遍历生成合规领域的知识点 , 执行比较耗时
    """
    parent_code = 'compfox_knowledge_point'
    parent_value = 'knowledge_point'
    parent_desc = 'CompFox-合规知识点'
    items = 'aml|data_security|insider_trading|market_manipulation|investor_protection|compliance_management|code_of_conduct'
    grades = '初级|中级|高级|管理层'

    # 合规领域中文名称映射
    subject_names = {
        'aml': '反洗钱',
        'data_security': '数据安全',
        'insider_trading': '内幕交易',
        'market_manipulation': '市场操纵',
        'investor_protection': '投资者保护',
        'compliance_management': '合规管理',
        'code_of_conduct': '行为准则'
    }

    # 检查父级参数是否存在
    parent_param = BaseParamsModel.get_param_by_code(parent_code, 'CompFox')

    if parent_param is None:
        # 父级参数不存在，创建父级参数
        parent = BaseParamsModel(
            code=parent_code,
            value=parent_value,
            desc=parent_desc,
            type='CompFox',
        )
        result = parent.save()
        if result != -1:
            print(f"✓ 创建父级参数成功: {parent_code}")
        else:
            print(f"✗ 创建父级参数失败: {parent_code}")
    else:
        print(f"✓ 父级参数已存在: {parent_code}")

    # 检查已存在的子参数
    existing_items = BaseParamsModel.get_params_by_parent_code(parent_code, 'CompFox')
    existing_codes = {s['code'] for s in existing_items}

    # 获取 LLM 实例
    llm = get_default_qwen_llm()

    # 笛卡尔积：遍历所有职级和合规领域的组合
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
                # 使用 LLM 生成合规知识点
                user_prompt = f"""请帮我列举金融合规领域「{subject_cn}」中{grade}职级员工需要掌握的20个重要合规知识点。

                                    要求：
                                    1. 知识点要覆盖该合规领域的核心监管要求和操作规范
                                    2. 每个知识点要简洁明了,小于15个字
                                    3. 知识点之间用逗号分隔
                                    4. 不要包含编号或其他符号
                                    5. 直接输出知识点列表，不要有其他说明文字

                                    示例：
                                    客户身份识别,大额交易报告,可疑交易监测,客户风险等级划分

                                    请输出20个{subject_cn}({grade}职级)的合规知识点："""

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
                    desc=f'CompFox-合规知识点-{subject_cn}-{grade}',
                    parent_code=parent_code,
                    type='CompFox',
                )
                result = params.save()
                if result != -1:
                    print(f"✓ 保存成功: {subject_cn} - {grade} ({code})")
                else:
                    print(f"✗ 保存失败: {subject_cn} - {grade} ({code})")
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