"""提示词模块

包含用于生成教学视频内容的各种提示词模板。
"""

def get_prompt1_outline(topic: str = None, target_audience: str = "大学生", reference_image_path: str = None) -> str:
    """生成教学大纲的提示词"""
    ref_img_section = f"\n\n参考图片路径：{reference_image_path}" if reference_image_path else ""
    return f"""
你是一个专业的教学内容设计师。请为主题"{topic}"创建一个详细的教学大纲。

目标受众：{target_audience}{ref_img_section}

请生成一个包含以下内容的大纲：
1. 主题概述
2. 学习目标
3. 章节划分
4. 每个章节的重点内容
5. 预计学习时间

请以JSON格式返回结果。
"""

def get_prompt2_storyboard(topic: str = None, sections: list = None) -> str:
    """生成故事板的提示词"""
    return f"""
你是一个专业的教育视频制作师。基于以下教学大纲创建详细的故事板。

主题：{topic}
章节：{sections}

请为每个章节创建：
1. 讲解文本内容
2. 动画和视觉元素描述
3. 关键概念的可视化方式
4. 过渡和连接元素

请以JSON格式返回结果。
"""

def get_prompt3_code(
    section: dict = None,
    base_class: str = "Scene",
    regenerate_note: str = ""
) -> str:
    """生成Manim代码的提示词"""
    return f"""
你是一个专业的Manim动画开发者。请为以下章节内容创建高质量的Manim动画代码。

章节信息：
{section}

基础类：{base_class}

{regenerate_note}

要求：
1. 代码必须能直接运行
2. 包含必要的导入
3. 动画流畅且教学效果良好
4. 代码清晰易懂
5. 包含适当的注释

请返回完整的Python代码，格式如下：

```python
class YourSceneName(Scene):
    def construct(self):
        # 你的代码
```
"""

def get_prompt4_feedback(
    section: dict = None,
    video_path: str = None,
    round_number: int = 1
) -> str:
    """获取MLLM反馈的提示词"""
    return f"""
你是一个专业的教育视频质量评估专家。请评估以下教学视频的质量。

章节信息：{section}
视频路径：{video_path}
评估轮次：{round_number}

请从以下维度评估：
1. 教学内容的准确性
2. 视觉呈现效果
3. 动画流畅度
4. 教学有效性
5. 整体观看体验

请指出存在的问题并提供改进建议。

请以JSON格式返回结果：
{{
    "has_issues": true/false,
    "suggested_improvements": ["建议1", "建议2"],
    "overall_quality": "良好/一般/需要改进"
}}
"""


def get_regenerate_note(attempt: int, MAX_REGENERATE_TRIES: int = 3) -> str:
    """生成代码重新生成的提示注释"""
    return f"""
注意：这是第 {attempt}/{MAX_REGENERATE_TRIES} 次尝试生成代码。
如果上次生成的代码有问题，请根据错误信息进行修复。
确保生成的代码语法正确，可以直接运行。
"""


def get_prompt5_debug(
    section_id: str = None,
    error_message: str = "",
    original_code: str = ""
) -> str:
    """调试和修复代码的提示词"""
    return f"""
你是一个专业的Python和Manim调试专家。请修复以下代码中的错误。

章节ID：{section_id}
错误信息：{error_message}
原始代码：
{original_code}

请分析错误原因并提供修复后的代码。
确保修复后的代码：
1. 语法正确
2. 逻辑合理
3. 能够正常运行
4. 保持原有功能

请返回修复后的完整代码。
"""

def get_prompt6_assets(storyboard: dict = None) -> str:
    """外部资源处理的提示词"""
    return f"""
你是一个专业的教育资源整合专家。请为以下故事板建议合适的外部资源。

故事板内容：
{storyboard}

请提供：
1. 建议的图片资源类型
2. 图标和插图建议
3. 可用的外部资源库
4. 资源整合方案

请以JSON格式返回结果。
"""

def get_prompt_download_assets(storyboard: dict = None) -> str:
    """下载外部资源的提示词"""
    return f"""
基于以下故事板，请分析需要下载的外部资源：

故事板内容：
{storyboard if storyboard else {}}

请识别：
1. 需要的图片类型和描述
2. 搜索关键词
3. 推荐的下载源
4. 资源命名建议

请以JSON格式返回结果。
"""

def get_prompt_place_assets(storyboard: dict = None, assets_dir: str = None) -> str:
    """放置外部资源的提示词"""
    return f"""
基于以下故事板和已下载的资源，请指导如何在Manim代码中正确放置这些资源：

故事板内容：
{storyboard if storyboard else {}}
资源目录：{assets_dir}

请提供：
1. 资源放置的具体方法
2. 代码修改建议
3. 文件路径修正
4. Manim对象创建指导

请以JSON格式返回结果，包含具体的代码修改建议。
"""


def get_prompt4_layout_feedback(section: dict = None, position_table: str = None) -> str:
    """获取布局反馈的提示词"""
    return f"""
你是一个专业的Manim代码布局分析专家。请分析以下章节代码的布局问题。

章节信息：{section}

代码元素位置表：
{position_table}

请分析以下布局问题：
1. 元素是否超出画面边界
2. 元素是否相互重叠
3. 元素位置是否合理
4. 是否有元素被遮挡

请以JSON格式返回结果：
{{
    "layout": {{
        "has_issues": true/false,
        "improvements": [
            {{"problem": "问题描述", "solution": "解决方案"}}
        ]
    }}
}}
"""