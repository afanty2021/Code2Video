"""
English Grammar Teaching Video Agent
英语语法教学视频生成代理
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent import TeachingVideoAgent, RunConfig, Section
from prompts import (
    get_prompt1_outline,
    get_prompt2_storyboard,
    get_prompt3_code,
)
from english.prompts import (
    get_english_grammar_outline,
    get_english_grammar_storyboard,
    get_english_grammar_code,
    get_english_grammar_feedback,
)
from utils import extract_answer_from_response


class EnglishTeachingVideoAgent(TeachingVideoAgent):
    """
    英语语法教学视频生成代理

    继承自 TeachingVideoAgent，专门用于生成英语语法教学视频。
    """

    def __init__(
        self,
        idx: int,
        grammar_topic: str,
        folder: str = "CASES",
        cfg: Optional[RunConfig] = None,
        target_audience: str = "ESL students"
    ):
        """
        初始化英语教学视频代理

        Args:
            idx: 视频索引
            grammar_topic: 语法主题，如 "Present Perfect Tense"
            folder: 输出文件夹
            cfg: 运行配置
            target_audience: 目标受众
        """
        self.grammar_topic = grammar_topic
        self.target_audience = target_audience
        super().__init__(idx, grammar_topic, folder, cfg)

    def generate_outline(self) -> Dict[str, Any]:
        """生成英语语法教学大纲"""
        prompt = get_english_grammar_outline(
            grammar_topic=self.grammar_topic,
            target_audience=self.target_audience
        )

        response = self.cfg.api(prompt, max_tokens=self.cfg.max_code_token_length)
        content = extract_answer_from_response(response)

        import json
        outline_data = json.loads(content)
        return outline_data

    def generate_storyboard(self, outline_data: Dict[str, Any]) -> List[Dict]:
        """生成英语语法故事板"""
        prompt = get_english_grammar_storyboard(
            grammar_topic=self.grammar_topic,
            sections=outline_data.get("sections", [])
        )

        response = self.cfg.api(prompt, max_tokens=self.cfg.max_code_token_length)
        content = extract_answer_from_response(response)

        import json
        storyboard_data = json.loads(content)
        return storyboard_data.get("sections", [])

    def generate_section_code(self, section: Section) -> str:
        """生成英语语法动画代码"""
        section_dict = {
            "id": section.id,
            "title": section.title,
            "animations": section.animations
        }

        prompt = get_english_grammar_code(section_dict)

        response = self.cfg.api(prompt, max_tokens=self.cfg.max_code_token_length)
        content = extract_answer_from_response(response)

        return content

    def get_mllm_feedback(self, section: Section, video_path: str) -> Dict[str, Any]:
        """获取英语语法视频反馈"""
        prompt = get_english_grammar_feedback(
            grammar_topic=self.grammar_topic,
            video_description=f"Section: {section.title}"
        )

        response = self.cfg.api(prompt, max_tokens=5000)
        content = extract_answer_from_response(response)

        import json
        feedback = json.loads(content)
        return feedback

    def generate_video(self):
        """
        生成完整的英语语法教学视频

        覆盖父类方法，使用英语专用提示词
        """
        print(f"🎬 Generating English Grammar Video: {self.grammar_topic}")

        # Generate outline
        outline_data = self.generate_outline()
        print(f"📝 Outline generated: {outline_data.get('topic')}")

        # Generate storyboard
        sections_data = self.generate_storyboard(outline_data)
        print(f"📖 Storyboard generated: {len(sections_data)} sections")

        # Convert to Section objects
        sections = []
        for sec_data in sections_data:
            section = Section(
                id=sec_data.get("id", ""),
                title=sec_data.get("title", ""),
                lecture_lines=sec_data.get("lecture_lines", []),
                animations=sec_data.get("animations", [])
            )
            sections.append(section)

        self.sections = sections

        # Generate and render sections
        self.generate_codes()
        self.render_all_sections()

        # Merge videos
        self.merge_videos()

        print(f"✅ English Grammar Video Generated: {self.grammar_topic}")


# Convenience function for quick start
def create_english_grammar_video(
    grammar_topic: str,
    target_audience: str = "ESL students",
    api_func=None
) -> EnglishTeachingVideoAgent:
    """
    快速创建英语语法视频生成器

    Args:
        grammar_topic: 语法主题
        target_audience: 目标受众
        api_func: API调用函数

    Returns:
        EnglishTeachingVideoAgent 实例
    """
    if api_func is None:
        from gpt_request import request_claude
        api_func = request_claude

    cfg = RunConfig(
        api=api_func,
        use_feedback=True,
        use_assets=True
    )

    agent = EnglishTeachingVideoAgent(
        idx=0,
        grammar_topic=grammar_topic,
        target_audience=target_audience,
        cfg=cfg
    )

    return agent
