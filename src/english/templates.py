"""
English Grammar Animation Templates
英语语法动画模板

提供常用的英语语法动画模板，用于生成语法教学视频。
"""

from typing import List, Dict, Any


class GrammarAnimationTemplates:
    """英语语法动画模板集合"""

    @staticmethod
    def sentence_structure_template(sentence: str, components: Dict[str, str]) -> str:
        """
        句子结构展示模板

        Args:
            sentence: 完整句子
            components: 句子成分 {subject: "...", verb: "...", object: "..."}

        Returns:
            Manim 代码模板
        """
        return f"""
# Sentence Structure: {sentence}
# Color coding: Subject=BLUE, Verb=GREEN, Object=YELLOW, Modifier=PURPLE

def construct(self):
    sentence = Text("{sentence}", font_size=48)
    self.play(Write(sentence))

    # Highlight subject
    subject = Text("{components.get('subject', '')}", color=BLUE, font_size=36)
    subject.next_to(sentence, DOWN)
    self.play(FadeIn(subject))

    # Highlight verb
    verb = Text("{components.get('verb', '')}", color=GREEN, font_size=36)
    verb.next_to(subject, RIGHT, buff=0.5)
    self.play(FadeIn(verb))

    # Highlight object if exists
    {'''
    # Highlight object
    obj = Text("''' + components.get('object', '') + '''", color=YELLOW, font_size=36)
    obj.next_to(verb, RIGHT, buff=0.5)
    self.play(FadeIn(obj))
    ''' if components.get('object') else '# No object in this sentence'}
"""

    @staticmethod
    def tense_timeline_template(tense: str, examples: List[str]) -> str:
        """
        时态时间线模板

        Args:
            tense: 时态名称
            examples: 示例句子

        Returns:
            Manim 代码模板
        """
        examples_text = "\n".join([f'    - "{ex}"' for ex in examples])

        return f"""
# Tense Timeline: {tense}

def construct(self):
    title = Text("{tense}", font_size=60)
    self.play(Write(title))

    # Show timeline
    timeline = NumberLine(x_range=[-3, 3], include_numbers=True)
    self.play(Create(timeline))

    # Add example sentences
{examples_text}

    for example in examples:
        text = Text(example, font_size=36)
        text.next_to(timeline, DOWN)
        self.play(Write(text))
        self.wait(2)
"""

    @staticmethod
    def verb_conjugation_template(verb: str, conjugations: Dict[str, str]) -> str:
        """
        动词 conjugation 表格模板

        Args:
            verb: 动词原形
            conjugations: 人称代词 -> 形式

        Returns:
            Manim 代码模板
        """
        table_rows = "\n".join([
            f'    - "{pronoun}: {form}"'
            for pronoun, form in conjugations.items()
        ])

        return f"""
# Verb Conjugation: {verb}

def construct(self):
    title = Text(f"Conjugation: {verb}", font_size=48)
    self.play(Write(title))

    conjugations = VGroup()
{table_rows}

    for item in conjugations:
        self.play(Write(item))
        self.wait(0.5)
"""

    @staticmethod
    def comparative_template(word: str, comparative: str, superlative: str) -> str:
        """
        比较级/最高级模板

        Args:
            word: 原级
            comparative: 比较级
            superlative: 最高级

        Returns:
            Manim 代码模板
        """
        return f"""
# Comparison: {word} -> {comparative} -> {superlative}

def construct(self):
    # Show base form
    base = Text("{word}", font_size=48, color=BLUE)
    self.play(Write(base))

    # Show comparative
    comp = Text("{comparative}", font_size=48, color=GREEN)
    comp.next_to(base, DOWN)
    self.play(Write(comp))

    # Show superlative
    sup = Text("{superlative}", font_size=48, color=YELLOW)
    sup.next_to(comp, DOWN)
    self.play(Write(sup))

    # Add arrows
    arrow1 = Arrow(start=base.get_bottom(), end=comp.get_top())
    arrow2 = Arrow(start=comp.get_bottom(), end=sup.get_top())
    self.play(Create(arrow1), Create(arrow2))
"""

    @staticmethod
    def passive_voice_template(sentence: str, subject: str, verb_phrase: str, agent: str = None) -> str:
        """
        被动语态转换模板

        Args:
            sentence: 主动句
            subject: 主语
            verb_phrase: 动词短语
            agent: 施动者（可选）

        Returns:
            Manim 代码模板
        """
        agent_text = f'by {agent}' if agent else ''

        return f"""
# Passive Voice: {sentence}

def construct(self):
    # Original (active) sentence
    active = Text("Active: {subject} {verb_phrase}", font_size=36)
    self.play(Write(active))

    # Transform to passive
    passive = Text("Passive: {verb_phrase} by {subject}", font_size=36, color=GREEN)
    passive.next_to(active, DOWN)
    self.play(Write(passive))

    # Highlight transformation
    box1 = SurroundingRectangle(active, color=BLUE)
    box2 = SurroundingRectangle(passive, color=GREEN)
    self.play(Create(box1), Create(box2))
    self.wait(2)
"""


# Pre-built templates for common grammar topics
COMMON_GRAMMAR_TEMPLATES = {
    "present_simple": {
        "name": "Present Simple Tense",
        "description": "一般现在时",
        "template": GrammarAnimationTemplates.sentence_structure_template
    },
    "past_simple": {
        "name": "Past Simple Tense",
        "description": "一般过去时",
        "template": GrammarAnimationTemplates.sentence_structure_template
    },
    "present_perfect": {
        "name": "Present Perfect Tense",
        "description": "现在完成时",
        "template": GrammarAnimationTemplates.tense_timeline_template
    },
    "passive_voice": {
        "name": "Passive Voice",
        "description": "被动语态",
        "template": GrammarAnimationTemplates.passive_voice_template
    },
    "comparative": {
        "name": "Comparative & Superlative",
        "description": "比较级与最高级",
        "template": GrammarAnimationTemplates.comparative_template
    }
}
