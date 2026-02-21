"""
English Grammar Teaching Prompts
英语语法教学提示词模板
"""

def get_english_grammar_outline(grammar_topic: str, target_audience: str = "ESL students") -> str:
    """
    生成英语语法教学大纲

    Args:
        grammar_topic: 语法主题，例如 "Present Perfect Tense"
        target_audience: 目标受众

    Returns:
        完整的提示词
    """
    return f"""You are an expert English grammar teacher. Create a comprehensive teaching outline for the grammar topic: "{grammar_topic}".

Target audience: {target_audience}

Create a teaching outline with the following structure:
{{
    "topic": "{grammar_topic}",
    "target_audience": "{target_audience}",
    "sections": [
        {{
            "id": "1",
            "title": "Introduction/Overview",
            "lecture_lines": ["..."],
            "animations": ["..."]
        }},
        {{
            "id": "2",
            "title": "Rule Explanation",
            "lecture_lines": ["..."],
            "animations": ["..."]
        }},
        {{
            "id": "3",
            "title": "Examples",
            "lecture_lines": ["..."],
            "animations": ["..."]
        }},
        {{
            "id": "4",
            "title": "Practice",
            "lecture_lines": ["..."],
            "animations": ["..."]
        }}
    ]
}}

Requirements:
1. All lecture_lines must be in English
2. Include clear grammar rules
3. Provide at least 3 example sentences
4. animations should describe visual elements that help explain the grammar

Output ONLY valid JSON without any markdown formatting."""


def get_english_grammar_storyboard(grammar_topic: str, sections: list) -> str:
    """
    生成英语语法故事板

    Args:
        grammar_topic: 语法主题
        sections: 章节列表

    Returns:
        完整的提示词
    """
    sections_json = "\n".join([f'{{"id": "{s["id"]}", "title": "{s["title"]}"}}' for s in sections])

    return f"""Create a detailed storyboard for teaching English grammar: "{grammar_topic}"

The outline sections are:
{sections_json}

For each section, provide detailed visual descriptions for animations:
- What text elements should appear
- What visual aids (diagrams, highlights) help explain the grammar
- How to animate sentence structures
- Color coding for different sentence components

Storyboard format:
{{
    "sections": [
        {{
            "id": "1",
            "title": "...",
            "animations": [
                {{
                    "scene": "...",
                    "elements": ["..."],
                    "transition": "fade_in",
                    "timing": 3
                }}
            ]
        }}
    ]
}}

Output ONLY valid JSON without any markdown formatting."""


def get_english_grammar_code(section: dict, base_class: str = "Scene") -> str:
    """
    生成英语语法动画代码

    Args:
        section: 章节数据
        base_class: 基础场景类

    Returns:
        完整的提示词
    """
    section_id = section.get("id", "1")
    title = section.get("title", "Grammar Lesson")
    animations = section.get("animations", [])

    animations_text = "\n".join([f"- {a}" for a in animations])

    return f"""You are a Manim expert. Generate Python code for an English grammar teaching animation.

Section: {title}
Section ID: {section_id}

Animation descriptions:
{animations_text}

Requirements:
1. Use Manim Community Edition v0.19.0
2. Use English text for all displays (Text objects)
3. Highlight grammar components with different colors:
   - Subject: BLUE
   - Verb: GREEN
   - Object: YELLOW
   - Modifier: PURPLE
4. Use appropriate animations to show grammar structure
5. Add clear explanations in English
6. Use proper Manim syntax

Example structure:
```python
from manim import *

class GrammarSection{title.replace(" ", "")}(Scene):
    def construct(self):
        # Animation code here
```

Generate ONLY the Python code without explanations."""


def get_english_grammar_feedback(grammar_topic: str, video_description: str) -> str:
    """
    获取英语语法视频反馈

    Args:
        grammar_topic: 语法主题
        video_description: 视频描述

    Returns:
        完整的提示词
    """
    return f"""Evaluate this English grammar teaching video about "{grammar_topic}".

Video description:
{video_description}

Evaluate based on:
1. Grammar accuracy - Are the grammar rules correct?
2. Clarity - Is the explanation easy to understand?
3. Visual aids - Do the animations help explain the grammar?
4. Engagement - Is the content engaging for students?
5. Examples - Are the example sentences appropriate?

Provide feedback in JSON format:
{{
    "has_issues": true/false,
    "grammar_accuracy": "rating 1-5",
    "clarity": "rating 1-5",
    "visual_aids": "rating 1-5",
    "engagement": "rating 1-5",
    "examples": "rating 1-5",
    "suggested_improvements": ["..."]
}}

Output ONLY valid JSON."""


def get_english_grammar_debug(error_msg: str, code: str) -> str:
    """
    调试英语语法动画代码

    Args:
        error_msg: 错误信息
        code: 现有代码

    Returns:
        完整的提示词
    """
    return f"""Fix the Manim code error for English grammar animation.

Error message:
{error_msg}

Current code:
{code}

Requirements:
1. Fix the syntax or runtime error
2. Maintain the grammar teaching purpose
3. Use Manim CE v0.19.0 syntax

Output ONLY the fixed Python code."""
