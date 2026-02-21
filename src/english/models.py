"""
English Grammar Data Models
英语教学数据模型
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class GrammarPoint:
    """语法点"""
    id: str
    title: str
    rule: str
    examples: List[str] = field(default_factory=list)


@dataclass
class GrammarSection:
    """语法章节"""
    id: str
    title: str
    lecture_lines: List[str]
    animations: List[str]
    grammar_points: List[GrammarPoint] = field(default_factory=list)


@dataclass
class GrammarTopic:
    """语法主题"""
    topic: str
    target_audience: str
    sections: List[GrammarSection]
    difficulty: str = "intermediate"  # beginner, intermediate, advanced
    estimated_duration: int = 5  # minutes


@dataclass
class EnglishSentence:
    """英语句子（用于语法分析）"""
    text: str
    subject: str
    verb: str
    object: Optional[str] = None
    modifiers: List[str] = field(default_factory=list)
    tense: str = "present"
    voice: str = "active"  # active, passive


@dataclass
class GrammarAnimationTemplate:
    """语法动画模板"""
    template_id: str
    name: str
    description: str
    applicable_grammar: List[str]  # e.g., ["present_perfect", "passive_voice"]
    manim_code_template: str
