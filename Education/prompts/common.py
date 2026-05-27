from jinja2 import Template


def prompt_render(prompt, params):
    """
    Jinja2 模板渲染
    :param prompt: 提示词
    :param params: 参数
    :return:
    """
    template = Template(prompt)
    return template.render(params)