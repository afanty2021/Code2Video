"""agent.py 模块的单元测试"""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
import tempfile
import json

# 导入被测试的模块
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from agent import (
        Section,
        TeachingOutline,
        VideoFeedback,
        RunConfig,
        TeachingVideoAgent
    )
except ImportError as e:
    print(f"Warning: 无法导入agent模块: {e}")

    # 使用conftest中定义的简化类
    pass


@pytest.mark.unit
class TestSection:
    """测试 Section 数据类"""

    def test_section_creation(self):
        """测试Section对象创建"""
        section = Section(
            id="test_section",
            title="测试章节",
            lecture_lines=["第一行", "第二行"],
            animations=["动画1", "动画2"]
        )

        assert section.id == "test_section"
        assert section.title == "测试章节"
        assert len(section.lecture_lines) == 2
        assert len(section.animations) == 2

    def test_section_empty_lists(self):
        """测试空列表的Section"""
        section = Section(
            id="empty",
            title="空章节",
            lecture_lines=[],
            animations=[]
        )

        assert section.lecture_lines == []
        assert section.animations == []


@pytest.mark.unit
class TestTeachingOutline:
    """测试 TeachingOutline 数据类"""

    def test_teaching_outline_creation(self):
        """测试TeachingOutline对象创建"""
        sections = [
            {"id": "1", "title": "第一章"},
            {"id": "2", "title": "第二章"}
        ]

        outline = TeachingOutline(
            topic="数学基础",
            target_audience="大学生",
            sections=sections
        )

        assert outline.topic == "数学基础"
        assert outline.target_audience == "大学生"
        assert len(outline.sections) == 2


@pytest.mark.unit
class TestVideoFeedback:
    """测试 VideoFeedback 数据类"""

    def test_video_feedback_creation(self):
        """测试VideoFeedback对象创建"""
        feedback = VideoFeedback(
            section_id="section_1",
            video_path="/tmp/video.mp4",
            has_issues=True,
            suggested_improvements=["改进1", "改进2"],
            raw_response="原始反馈"
        )

        assert feedback.section_id == "section_1"
        assert feedback.has_issues is True
        assert len(feedback.suggested_improvements) == 2

    def test_video_feedback_with_defaults(self):
        """测试带默认值的VideoFeedback"""
        feedback = VideoFeedback(
            section_id="section_2",
            video_path="/tmp/video2.mp4",
            has_issues=False,
            suggested_improvements=[]
        )

        assert feedback.raw_response is None


@pytest.mark.unit
class TestRunConfig:
    """测试 RunConfig 数据类"""

    def test_run_config_defaults(self):
        """测试RunConfig默认值"""
        config = RunConfig()

        assert config.use_feedback is True
        assert config.use_assets is True
        assert config.feedback_rounds == 2
        assert config.max_fix_bug_tries == 10

    def test_run_config_custom_values(self):
        """测试自定义RunConfig值"""
        mock_api = Mock()
        config = RunConfig(
            use_feedback=False,
            api=mock_api,
            feedback_rounds=5,
            iconfinder_api_key="test_key"
        )

        assert config.use_feedback is False
        assert config.api is mock_api
        assert config.feedback_rounds == 5
        assert config.iconfinder_api_key == "test_key"


@pytest.mark.unit
class TestTeachingVideoAgent:
    """测试 TeachingVideoAgent 类"""

    @pytest.fixture
    def agent_with_mocks(self, sample_run_config, temp_dir):
        """创建带有模拟对象的TeachingVideoAgent实例"""
        with patch('agent.get_output_dir') as mock_get_output_dir, \
             patch('builtins.open', mock_open(read_data='{"test": "mapping"}')), \
             patch('json.load', return_value={"test": "mapping"}), \
             patch('agent.ScopeRefineFixer') as mock_scope_fixer, \
             patch('agent.GridPositionExtractor') as mock_extractor:

            mock_get_output_dir.return_value = temp_dir / "output"

            agent = TeachingVideoAgent(
                idx=1,
                knowledge_point="微积分",
                folder="CASES",
                cfg=sample_run_config
            )

            return agent

    def test_agent_initialization(self, agent_with_mocks):
        """测试代理初始化"""
        agent = agent_with_mocks

        assert agent.learning_topic == "微积分"
        assert agent.idx == 1
        assert agent.folder == "CASES"
        assert agent.use_feedback is True
        assert agent.feedback_rounds == 2

    @pytest.mark.unit
    @patch('agent.get_prompt1_outline')
    def test_generate_outline(self, mock_prompt, agent_with_mocks, sample_teaching_outline):
        """测试生成教学大纲"""
        # 设置模拟API响应
        mock_api_response = '{"topic": "微积分", "sections": [{"id": "1", "title": "导数"}]}'
        agent_with_mocks.cfg.api.return_value = mock_api_response

        # 模拟get_prompt1_outline函数
        mock_prompt.return_value = "测试提示词"

        # 模拟extract_answer_from_response函数
        with patch('agent.extract_answer_from_response', return_value=mock_api_response), \
             patch('json.loads', return_value={"topic": "微积分", "sections": [{"id": "1", "title": "导数"}]}), \
             patch('agent.topic_to_safe_name', return_value="微积分"), \
             patch('os.makedirs'):

            result = agent_with_mocks.generate_outline()

            assert isinstance(result, TeachingOutline)
            assert result.topic == "微积分"
            assert len(result.sections) == 1

    @pytest.mark.unit
    @patch('agent.get_prompt2_storyboard')
    def test_generate_storyboard(self, mock_prompt, agent_with_mocks, sample_teaching_outline):
        """测试生成故事板"""
        # 设置模拟API响应
        mock_api_response = '{"sections": [{"id": "1", "title": "导数", "animations": ["动画1"]}]}'
        agent_with_mocks.cfg.api.return_value = mock_api_response
        mock_prompt.return_value = "测试故事板提示词"

        with patch('agent.extract_answer_from_response', return_value=mock_api_response), \
             patch('json.loads', return_value={"sections": [{"id": "1", "title": "导数", "animations": ["动画1"]}]}):

            result = agent_with_mocks.generate_storyboard()

            assert isinstance(result, list)
            assert len(result) == 1
            assert result[0].id == "1"
            assert result[0].title == "导数"

    @pytest.mark.unit
    def test_generate_section_code(self, agent_with_mocks, sample_section):
        """测试生成章节代码"""
        mock_api_response = '''
```python
class TestScene(Scene):
    def construct(self):
        pass
```
'''

        agent_with_mocks.cfg.api.return_value = mock_api_response

        with patch('agent.get_prompt3_code') as mock_prompt, \
             patch('agent.extract_answer_from_response', return_value=mock_api_response), \
             patch('agent.save_code_to_file', return_value=True) as mock_save:

            mock_prompt.return_value = "测试代码生成提示词"

            result = agent_with_mocks.generate_section_code(sample_section)

            assert isinstance(result, str)
            assert "TestScene" in result
            mock_save.assert_called_once()

    @pytest.mark.unit
    def test_debug_and_fix_code_success(self, agent_with_mocks):
        """测试调试和修复代码成功"""
        with patch('agent.run_manim_script', return_value=True) as mock_run:
            result = agent_with_mocks.debug_and_fix_code("section_1")

            assert result is True
            mock_run.assert_called_once()

    @pytest.mark.unit
    def test_debug_and_fix_code_with_retries(self, agent_with_mocks):
        """测试调试和修复代码需要重试"""
        # 第一次失败，第二次成功
        with patch('agent.run_manim_script') as mock_run:
            mock_run.side_effect = [False, True]

            with patch('agent.get_prompt5_debug') as mock_debug_prompt, \
                 patch.object(agent_with_mocks.cfg.api, '__call__') as mock_api, \
                 patch('agent.extract_answer_from_response', return_value="fixed code"), \
                 patch('agent.save_code_to_file', return_value=True):

                mock_debug_prompt.return_value = "调试提示词"
                mock_api.return_value = "mock debug response"

                result = agent_with_mocks.debug_and_fix_code("section_1")

                assert result is True
                assert mock_run.call_count == 2

    @pytest.mark.unit
    def test_get_mllm_feedback(self, agent_with_mocks, sample_section):
        """测试获取MLLM反馈"""
        mock_feedback_response = '''
        {
            "has_issues": true,
            "suggested_improvements": ["改进1", "改进2"]
        }
        '''

        agent_with_mocks.cfg.api.return_value = mock_feedback_response

        with patch('agent.get_prompt4_feedback') as mock_prompt, \
             patch('agent.extract_answer_from_response', return_value=mock_feedback_response), \
             patch('json.loads', return_value={"has_issues": True, "suggested_improvements": ["改进1", "改进2"]}):

            result = agent_with_mocks.get_mllm_feedback(sample_section, "/tmp/video.mp4")

            assert isinstance(result, VideoFeedback)
            assert result.section_id == sample_section.id
            assert result.has_issues is True
            assert len(result.suggested_improvements) == 2

    @pytest.mark.unit
    def test_optimize_with_feedback_no_issues(self, agent_with_mocks, sample_section):
        """测试优化反馈但没有问题"""
        feedback = VideoFeedback(
            section_id=sample_section.id,
            video_path="/tmp/video.mp4",
            has_issues=False,
            suggested_improvements=[]
        )

        result = agent_with_mocks.optimize_with_feedback(sample_section, feedback)
        assert result is True  # 没有问题，直接返回True

    @pytest.mark.unit
    def test_optimize_with_feedback_has_issues(self, agent_with_mocks, sample_section):
        """测试有问题的反馈优化"""
        feedback = VideoFeedback(
            section_id=sample_section.id,
            video_path="/tmp/video.mp4",
            has_issues=True,
            suggested_improvements=["需要改进动画"]
        )

        agent_with_mocks.cfg.api.return_value = "optimized code"

        with patch('agent.get_prompt3_code') as mock_prompt, \
             patch('agent.extract_answer_from_response', return_value="optimized code"), \
             patch('agent.save_code_to_file', return_value=True) as mock_save, \
             patch('agent.render_section', return_value=True) as mock_render:

            mock_prompt.return_value = "优化提示词"

            result = agent_with_mocks.optimize_with_feedback(sample_section, feedback)

            assert result is True
            mock_save.assert_called_once()
            mock_render.assert_called_once()

    @pytest.mark.unit
    def test_generate_codes_parallel(self, agent_with_mocks, sample_section):
        """测试并行生成代码"""
        sections = [sample_section]

        agent_with_mocks.cfg.api.return_value = "generated code"

        with patch.object(agent_with_mocks, 'generate_section_code', return_value="code") as mock_gen:
            result = agent_with_mocks.generate_codes()

            assert isinstance(result, dict)
            assert sample_section.id in result
            mock_gen.assert_called_once_with(sample_section)

    @pytest.mark.unit
    def test_render_section_success(self, agent_with_mocks, sample_section):
        """测试渲染章节成功"""
        with patch.object(agent_with_mocks, 'debug_and_fix_code', return_value=True) as mock_debug:
            result = agent_with_mocks.render_section(sample_section)

            assert result is True
            mock_debug.assert_called_once_with(sample_section.id)

    @pytest.mark.unit
    def test_render_section_failure(self, agent_with_mocks, sample_section):
        """测试渲染章节失败"""
        with patch.object(agent_with_mocks, 'debug_and_fix_code', return_value=False) as mock_debug:
            result = agent_with_mocks.render_section(sample_section)

            assert result is False
            mock_debug.assert_called_once_with(sample_section.id)

    @pytest.mark.unit
    def test_get_serializable_state(self, agent_with_mocks):
        """测试获取可序列化状态"""
        with patch.object(agent_with_mocks, 'generate_outline') as mock_outline, \
             patch.object(agent_with_mocks, 'generate_storyboard') as mock_storyboard:

            mock_outline.return_value = TeachingOutline("topic", "audience", [])
            mock_storyboard.return_value = []

            state = agent_with_mocks.get_serializable_state()

            assert "learning_topic" in state
            assert "idx" in state
            assert "outline" in state
            assert "storyboard" in state


@pytest.mark.unit
class TestTeachingVideoAgentIntegration:
    """TeachingVideoAgent集成测试"""

    @pytest.mark.unit
    def test_full_workflow_simulation(self, sample_run_config, temp_dir):
        """测试完整工作流模拟"""
        # 这里只测试各方法的调用流程，不测试实际的API调用
        with patch('agent.get_output_dir') as mock_get_output_dir, \
             patch('builtins.open', mock_open(read_data='{"test": "mapping"}')), \
             patch('json.load', return_value={"test": "mapping"}), \
             patch('agent.ScopeRefineFixer'), \
             patch('agent.GridPositionExtractor'):

            mock_get_output_dir.return_value = temp_dir / "output"

            agent = TeachingVideoAgent(
                idx=1,
                knowledge_point="测试主题",
                folder="CASES",
                cfg=sample_run_config
            )

            # 验证初始状态
            assert agent.learning_topic == "测试主题"
            assert agent.idx == 1
            assert hasattr(agent, 'cfg')

            # 验证目录创建
            assert mock_get_output_dir.called


@pytest.mark.unit
class TestAgentErrorHandling:
    """测试代理的错误处理"""

    def test_api_failure_handling(self, sample_run_config, temp_dir):
        """测试API失败的处理"""
        with patch('agent.get_output_dir') as mock_get_output_dir, \
             patch('builtins.open', mock_open(read_data='{"test": "mapping"}')), \
             patch('json.load', return_value={"test": "mapping"}), \
             patch('agent.ScopeRefineFixer'), \
             patch('agent.GridPositionExtractor'):

            mock_get_output_dir.return_value = temp_dir / "output"

            agent = TeachingVideoAgent(
                idx=1,
                knowledge_point="测试",
                folder="CASES",
                cfg=sample_run_config
            )

            # 模拟API抛出异常
            agent.cfg.api.side_effect = Exception("API Error")

            with pytest.raises(Exception):
                agent.generate_outline()