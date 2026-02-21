"""
英语教学模块单元测试

注意: 由于依赖 manim 模块，部分测试需要在安装依赖后运行
"""

import pytest
from pathlib import Path
import sys

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


@pytest.mark.unit
class TestEnglishPrompts:
    """测试英语教学提示词 - 基础字符串验证"""

    def test_prompts_module_exists(self):
        """测试 prompts 模块存在"""
        from english import prompts
        assert hasattr(prompts, 'get_english_grammar_outline')
        assert hasattr(prompts, 'get_english_grammar_storyboard')
        assert hasattr(prompts, 'get_english_grammar_code')
        assert hasattr(prompts, 'get_english_grammar_feedback')

    def test_outline_function_callable(self):
        """测试大纲生成函数可调用"""
        from english.prompts import get_english_grammar_outline
        assert callable(get_english_grammar_outline)

    def test_storyboard_function_callable(self):
        """测试故事板生成函数可调用"""
        from english.prompts import get_english_grammar_storyboard
        assert callable(get_english_grammar_storyboard)

    def test_code_function_callable(self):
        """测试代码生成函数可调用"""
        from english.prompts import get_english_grammar_code
        assert callable(get_english_grammar_code)


@pytest.mark.unit
class TestEnglishModels:
    """测试英语教学数据模型"""

    def test_models_module_exists(self):
        """测试 models 模块存在"""
        from english import models
        assert hasattr(models, 'GrammarSection')
        assert hasattr(models, 'GrammarPoint')
        assert hasattr(models, 'GrammarTopic')
        assert hasattr(models, 'EnglishSentence')

    def test_grammar_point_creation(self):
        """测试 GrammarPoint 创建"""
        from english.models import GrammarPoint
        point = GrammarPoint(
            id="1",
            title="Subject-Verb Agreement",
            rule="Subject and verb must agree",
            examples=["She goes.", "They play."]
        )
        assert point.id == "1"
        assert point.title == "Subject-Verb Agreement"

    def test_grammar_section_creation(self):
        """测试 GrammarSection 创建"""
        from english.models import GrammarSection
        section = GrammarSection(
            id="1",
            title="Introduction",
            lecture_lines=["Line 1", "Line 2"],
            animations=["Anim 1"]
        )
        assert section.id == "1"
        assert len(section.lecture_lines) == 2


@pytest.mark.unit
class TestGrammarTemplates:
    """测试语法动画模板"""

    def test_templates_module_exists(self):
        """测试 templates 模块存在"""
        from english import templates
        assert hasattr(templates, 'GrammarAnimationTemplates')
        assert hasattr(templates, 'COMMON_GRAMMAR_TEMPLATES')

    def test_common_templates(self):
        """测试预置模板"""
        from english.templates import COMMON_GRAMMAR_TEMPLATES
        assert "present_simple" in COMMON_GRAMMAR_TEMPLATES
        assert "passive_voice" in COMMON_GRAMMAR_TEMPLATES

    def test_template_structure(self):
        """测试模板结构"""
        from english.templates import COMMON_GRAMMAR_TEMPLATES
        template = COMMON_GRAMMAR_TEMPLATES["present_simple"]
        assert "name" in template
        assert "description" in template
        assert "template" in template


@pytest.mark.unit
class TestEnglishModuleStructure:
    """测试模块结构"""

    def test_english_directory_exists(self):
        """测试 english 目录存在"""
        english_dir = project_root / "src" / "english"
        assert english_dir.exists()

    def test_required_files_exist(self):
        """测试必需文件存在"""
        english_dir = project_root / "src" / "english"
        required_files = ["__init__.py", "agent.py", "models.py", "prompts.py", "templates.py"]
        for f in required_files:
            assert (english_dir / f).exists(), f"Missing file: {f}"

    def test_entry_point(self):
        """测试入口点 - 验证模块导出"""
        # 验证模块导出定义（不实际导入以避免 manim 依赖）
        import src
        assert hasattr(src, '__all__')
        assert 'EnglishTeachingVideoAgent' in src.__all__
        assert 'create_english_grammar_video' in src.__all__
