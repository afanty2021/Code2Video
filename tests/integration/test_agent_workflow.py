"""TeachingVideoAgent 完整工作流集成测试"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
from pathlib import Path
import sys
import os

# 添加src到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from agent import TeachingVideoAgent, RunConfig, Section, TeachingOutline


@pytest.mark.integration
class TestTeachingVideoAgentWorkflow:
    """测试 TeachingVideoAgent 完整工作流"""

    @pytest.fixture
    def mock_environment(self, temp_dir):
        """设置模拟环境"""
        # 创建必要的目录结构
        base_dir = temp_dir / "CASES"
        base_dir.mkdir(parents=True)

        # 创建 output 目录（测试需要的）
        output_dir = base_dir / "output"
        output_dir.mkdir(parents=True)

        assets_dir = temp_dir / "assets"
        assets_dir.mkdir(parents=True)

        json_dir = temp_dir / "json_files"
        json_dir.mkdir(parents=True)

        reference_dir = assets_dir / "reference"
        reference_dir.mkdir()

        # 创建知识映射文件
        knowledge_mapping = {
            "微积分": "assets/reference/calculus.jpg",
            "导数": "assets/reference/derivative.jpg",
            "函数": "assets/reference/function.jpg"
        }

        mapping_file = json_dir / "long_video_ref_mapping.json"
        with open(mapping_file, 'w') as f:
            json.dump(knowledge_mapping, f)

        # 创建参考图片文件
        for img_name in knowledge_mapping.values():
            img_path = temp_dir / img_name
            img_path.parent.mkdir(parents=True, exist_ok=True)
            img_path.touch()

        return {
            "base_dir": str(base_dir),
            "assets_dir": str(assets_dir),
            "knowledge_mapping": knowledge_mapping,
            "output_dir": str(output_dir)
        }

    @pytest.fixture
    def mock_run_config(self):
        """创建模拟运行配置"""
        mock_api = Mock()
        return RunConfig(
            use_feedback=True,
            use_assets=True,
            api=mock_api,
            feedback_rounds=1,  # 减少反馈轮次以加快测试
            iconfinder_api_key="test_key",
            max_fix_bug_tries=2,  # 减少重试次数
            max_regenerate_tries=2,
            max_feedback_gen_code_tries=2,
            max_mllm_fix_bugs_tries=2
        )

    @pytest.fixture
    def sample_responses(self):
        """示例API响应"""
        return {
            "outline_response": {
                "topic": "微积分基础",
                "target_audience": "大学生",
                "sections": [
                    {
                        "id": "section_1",
                        "title": "导数的定义",
                        "content": "导数是微积分的核心概念",
                        "key_concepts": ["极限", "变化率"]
                    },
                    {
                        "id": "section_2",
                        "title": "求导法则",
                        "content": "基本的求导方法和公式",
                        "key_concepts": ["幂函数", "四则运算"]
                    }
                ]
            },
            "storyboard_response": {
                "sections": [
                    {
                        "id": "section_1",
                        "title": "导数的定义",
                        "lecture_lines": [
                            "导数描述了函数在某点的瞬时变化率",
                            "它是通过极限的概念定义的"
                        ],
                        "animations": [
                            "展示切线逐渐形成的过程",
                            "动画演示极限概念"
                        ]
                    }
                ]
            },
            "code_response": '''
class DerivativeDefinitionScene(Scene):
    def construct(self):
        # 创建坐标系
        axes = Axes(
            x_range=[-2, 2],
            y_range=[-1, 3],
            axis_config={"color": BLUE}
        )

        # 创建函数曲线
        func = axes.plot(lambda x: x**2, color=RED)

        # 显示切线
        self.play(Create(axes), Create(func))
        self.wait(1)
''',
            "feedback_response": {
                "has_issues": False,
                "suggested_improvements": [],
                "overall_quality": "良好"
            }
        }

    @pytest.mark.integration
    @patch('agent.get_output_dir')
    @patch('agent.ScopeRefineFixer')
    @patch('agent.GridPositionExtractor')
    def test_complete_workflow_success(
        self,
        mock_extractor,
        mock_scope_fixer,
        mock_get_output_dir,
        mock_environment,
        mock_run_config,
        sample_responses
    ):
        """测试完整的成功工作流"""
        # 设置路径模拟
        mock_get_output_dir.return_value = Path(mock_environment["base_dir"]) / "output"

        # 创建代理
        agent = TeachingVideoAgent(
            idx=1,
            knowledge_point="微积分基础",
            folder=mock_environment["base_dir"],
            cfg=mock_run_config
        )

        # 设置API响应 - 返回 (response, usage) 元组格式
        # 顺序: outline, storyboard, 增强(可能有), code
        mock_api = mock_run_config.api
        mock_api.side_effect = [
            (json.dumps(sample_responses["outline_response"]), {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}),
            (json.dumps(sample_responses["storyboard_response"]), {"prompt_tokens": 200, "completion_tokens": 100, "total_tokens": 300}),
            (json.dumps(sample_responses["storyboard_response"]), {"prompt_tokens": 150, "completion_tokens": 75, "total_tokens": 225}),  # 增强 storyboard
            (sample_responses["code_response"], {"prompt_tokens": 300, "completion_tokens": 150, "total_tokens": 450}),
            (json.dumps(sample_responses["feedback_response"]), {"prompt_tokens": 150, "completion_tokens": 75, "total_tokens": 225})
        ]

        # 模拟辅助函数
        def mock_path_exists(self):
            """Path.exists() 方法的 mock"""
            return True

        with patch('agent.extract_answer_from_response') as mock_extract, \
             patch('agent.run_manim_script', return_value=True) as mock_manim, \
             patch('agent.subprocess.run') as mock_subprocess, \
             patch('agent.stitch_videos', return_value=True) as mock_stitch:

            # 模拟 subprocess.run 返回成功和错误
            def mock_run(*args, **kwargs):
                result = Mock()
                result.returncode = 0
                result.stdout = "Video rendered successfully"
                result.stderr = ""  # 空错误表示成功
                return result
            mock_subprocess.side_effect = mock_run

            # 设置提取函数的行为
            def extract_side_effect(response):
                return response
            mock_extract.side_effect = extract_side_effect

            # 步骤1：生成大纲
            outline = agent.generate_outline()
            assert isinstance(outline, TeachingOutline)
            assert outline.topic == "微积分基础"
            assert len(outline.sections) > 0

            # 步骤2：生成故事板
            storyboard = agent.generate_storyboard()
            assert isinstance(storyboard, list)
            assert len(storyboard) > 0

            # 步骤3：生成代码
            codes = agent.generate_codes()
            assert isinstance(codes, dict)
            assert len(codes) > 0

            # 步骤4：渲染章节
            for section in storyboard:
                success = agent.render_section(section)
                assert success is True

            # 验证调用次数
            assert mock_save.call_count > 0
            assert mock_manim.call_count > 0

    @pytest.mark.integration
    @patch('agent.get_output_dir')
    @patch('agent.ScopeRefineFixer')
    @patch('agent.GridPositionExtractor')
    def test_workflow_with_debugging(
        self,
        mock_extractor,
        mock_scope_fixer,
        mock_get_output_dir,
        mock_environment,
        mock_run_config,
        sample_responses
    ):
        """测试需要调试的工作流"""
        mock_get_output_dir.return_value = Path(mock_environment["base_dir"]) / "output"

        agent = TeachingVideoAgent(
            idx=1,
            knowledge_point="微积分基础",
            folder=mock_environment["base_dir"],
            cfg=mock_run_config
        )

        # 设置API响应，包括调试修复 - 返回 (response, usage) 元组格式
        mock_api = mock_run_config.api
        mock_api.side_effect = [
            (json.dumps(sample_responses["outline_response"]), {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}),
            (json.dumps(sample_responses["storyboard_response"]), {"prompt_tokens": 200, "completion_tokens": 100, "total_tokens": 300}),
            ("invalid code", {"prompt_tokens": 300, "completion_tokens": 150, "total_tokens": 450}),  # 初始代码有误
            ("fixed code", {"prompt_tokens": 300, "completion_tokens": 150, "total_tokens": 450}),   # 修复后的代码
            (json.dumps(sample_responses["feedback_response"]), {"prompt_tokens": 150, "completion_tokens": 75, "total_tokens": 225})
        ]

        with patch('agent.extract_answer_from_response') as mock_extract, \
             patch('agent.save_code_to_file', return_value=True) as mock_save, \
             patch('agent.run_manim_script') as mock_manim, \
             patch('os.path.exists', return_value=True), \
             patch('agent.stitch_videos', return_value=True):

            mock_extract.side_effect = lambda x: x
            # 第一次运行失败，第二次成功
            mock_manim.side_effect = [False, True]

            # 生成故事板
            storyboard = agent.generate_storyboard()

            # 渲染章节（需要调试）
            section = storyboard[0]
            success = agent.render_section(section)

            # 验证调试过程被调用
            assert mock_manim.call_count >= 2  # 至少尝试了两次
            assert success is True

    @pytest.mark.integration
    @patch('agent.get_output_dir')
    @patch('agent.ScopeRefineFixer')
    @patch('agent.GridPositionExtractor')
    def test_workflow_with_feedback_optimization(
        self,
        mock_extractor,
        mock_scope_fixer,
        mock_get_output_dir,
        mock_environment,
        mock_run_config,
        sample_responses
    ):
        """测试带反馈优化的工作流"""
        # 配置需要反馈
        mock_run_config.use_feedback = True
        mock_run_config.feedback_rounds = 1

        mock_get_output_dir.return_value = Path(mock_environment["base_dir"]) / "output"

        agent = TeachingVideoAgent(
            idx=1,
            knowledge_point="微积分基础",
            folder=mock_environment["base_dir"],
            cfg=mock_run_config
        )

        # 设置有问题的反馈响应
        problematic_feedback = {
            "has_issues": True,
            "suggested_improvements": ["提高动画流畅度", "增加更多示例"],
            "overall_quality": "一般"
        }

        mock_api = mock_run_config.api
        mock_api.side_effect = [
            (json.dumps(sample_responses["outline_response"]), {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}),
            (json.dumps(sample_responses["storyboard_response"]), {"prompt_tokens": 200, "completion_tokens": 100, "total_tokens": 300}),
            (sample_responses["code_response"], {"prompt_tokens": 300, "completion_tokens": 150, "total_tokens": 450}),
            (json.dumps(problematic_feedback), {"prompt_tokens": 150, "completion_tokens": 75, "total_tokens": 225}),  # 第一次反馈有问题
            ("optimized code", {"prompt_tokens": 300, "completion_tokens": 150, "total_tokens": 450}),  # 优化后的代码
            (json.dumps(sample_responses["feedback_response"]), {"prompt_tokens": 150, "completion_tokens": 75, "total_tokens": 225})  # 第二次反馈
        ]

        with patch('agent.extract_answer_from_response') as mock_extract, \
             patch('agent.save_code_to_file', return_value=True) as mock_save, \
             patch('agent.run_manim_script', return_value=True) as mock_manim, \
             patch('os.path.exists', return_value=True), \
             patch('agent.stitch_videos', return_value=True):

            mock_extract.side_effect = lambda x: x

            # 生成故事板
            storyboard = agent.generate_storyboard()
            section = storyboard[0]

            # 执行反馈优化
            feedback = agent.get_mllm_feedback(section, "/tmp/test.mp4")
            assert feedback.has_issues is True

            # 优化代码
            optimized = agent.optimize_with_feedback(section, feedback)
            assert optimized is True

            # 验证优化过程
            assert mock_save.call_count > 1  # 至少保存了两次代码

    @pytest.mark.integration
    @patch('agent.get_output_dir')
    @patch('agent.ScopeRefineFixer')
    @patch('agent.GridPositionExtractor')
    def test_workflow_parallel_code_generation(
        self,
        mock_extractor,
        mock_scope_fixer,
        mock_get_output_dir,
        mock_environment,
        mock_run_config,
        sample_responses
    ):
        """测试并行代码生成"""
        mock_get_output_dir.return_value = Path(mock_environment["base_dir"]) / "output"

        agent = TeachingVideoAgent(
            idx=1,
            knowledge_point="微积分基础",
            folder=mock_environment["base_dir"],
            cfg=mock_run_config
        )

        # 创建多章节的故事板
        multi_section_storyboard = [
            Section(
                id="section_1",
                title="导数定义",
                lecture_lines=["导数的定义"],
                animations=["动画1"]
            ),
            Section(
                id="section_2",
                title="求导法则",
                lecture_lines=["求导法则"],
                animations=["动画2"]
            ),
            Section(
                id="section_3",
                title="应用实例",
                lecture_lines=["应用实例"],
                animations=["动画3"]
            )
        ]

        mock_api = mock_run_config.api
        mock_api.side_effect = [
            (sample_responses["code_response"], {"prompt_tokens": 300, "completion_tokens": 150, "total_tokens": 450}) for _ in range(3)
        ]

        with patch('agent.extract_answer_from_response') as mock_extract, \
             patch('agent.save_code_to_file', return_value=True) as mock_save, \
             patch('agent.generate_storyboard', return_value=multi_section_storyboard):

            mock_extract.side_effect = lambda x: x

            # 并行生成代码
            codes = agent.generate_codes()

            # 验证结果
            assert len(codes) == 3
            assert all(section.id in codes for section in multi_section_storyboard)
            assert mock_save.call_count == 3

    @pytest.mark.integration
    def test_error_handling_and_recovery(
        self,
        mock_environment,
        mock_run_config
    ):
        """测试错误处理和恢复"""
        with patch('agent.get_output_dir') as mock_get_output_dir, \
             patch('agent.ScopeRefineFixer'), \
             patch('agent.GridPositionExtractor'):

            mock_get_output_dir.return_value = Path(mock_environment["base_dir"]) / "output"

            agent = TeachingVideoAgent(
                idx=1,
                knowledge_point="微积分基础",
                folder=mock_environment["base_dir"],
                cfg=mock_run_config
            )

            # 测试API错误
            mock_run_config.api.side_effect = Exception("API Error")

            with pytest.raises(Exception):
                agent.generate_outline()

            # 测试文件操作错误
            mock_run_config.api.side_effect = None
            mock_run_config.api.return_value = '{"test": "response"}'

            with patch('agent.extract_answer_from_response', return_value='{"test": "response"}'), \
                 patch('os.makedirs', side_effect=OSError("Permission denied")):

                with pytest.raises(OSError):
                    agent._setup_output_directories()

    @pytest.mark.integration
    @patch('agent.get_output_dir')
    @patch('agent.ScopeRefineFixer')
    @patch('agent.GridPositionExtractor')
    def test_state_serialization(
        self,
        mock_extractor,
        mock_scope_fixer,
        mock_get_output_dir,
        mock_environment,
        mock_run_config,
        sample_responses
    ):
        """测试状态序列化"""
        mock_get_output_dir.return_value = Path(mock_environment["base_dir"]) / "output"

        agent = TeachingVideoAgent(
            idx=1,
            knowledge_point="微积分基础",
            folder=mock_environment["base_dir"],
            cfg=mock_run_config
        )

        # 模拟部分工作流完成
        with patch('agent.generate_outline') as mock_outline, \
             patch('agent.generate_storyboard') as mock_storyboard:

            mock_outline.return_value = TeachingOutline(
                topic="微积分基础",
                target_audience="大学生",
                sections=sample_responses["outline_response"]["sections"]
            )
            mock_storyboard.return_value = [
                Section(
                    id="section_1",
                    title="导数定义",
                    lecture_lines=["内容"],
                    animations=["动画"]
                )
            ]

            # 获取序列化状态
            state = agent.get_serializable_state()

            # 验证状态包含必要信息
            required_keys = [
                "learning_topic",
                "idx",
                "folder",
                "outline",
                "storyboard"
            ]

            for key in required_keys:
                assert key in state, f"状态中缺少键: {key}"

            # 验证状态可以被JSON序列化
            json_str = json.dumps(state, default=str)
            assert isinstance(json_str, str)

            # 验证可以反序列化
            restored_state = json.loads(json_str)
            assert restored_state["learning_topic"] == "微积分基础"


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceAndScalability:
    """性能和可扩展性测试"""

    @pytest.mark.integration
    @patch('agent.get_output_dir')
    @patch('agent.ScopeRefineFixer')
    @patch('agent.GridPositionExtractor')
    def test_large_project_handling(
        self,
        mock_extractor,
        mock_scope_fixer,
        mock_get_output_dir,
        temp_dir,
        mock_run_config
    ):
        """测试大型项目处理"""
        # 创建必要的目录结构（包含 CASES）
        base_dir = temp_dir / "CASES"
        base_dir.mkdir(parents=True)

        # 创建 JSON 文件（agent.py 需要）
        json_dir = temp_dir / "json_files"
        json_dir.mkdir(parents=True)
        ref_mapping = json_dir / "long_video_ref_mapping.json"
        ref_mapping.write_text("{}")

        mock_get_output_dir.return_value = base_dir / "output"

        # 创建大量章节的项目
        agent = TeachingVideoAgent(
            idx=1,
            knowledge_point="高等数学完整课程",
            folder=str(temp_dir),
            cfg=mock_run_config
        )

        # 模拟大量章节
        large_outline = TeachingOutline(
            topic="高等数学",
            target_audience="大学生",
            sections=[
                {
                    "id": f"section_{i}",
                    "title": f"第{i}章",
                    "content": f"第{i}章的内容"
                }
                for i in range(20)  # 20个章节
            ]
        )

        large_storyboard = [
            Section(
                id=f"section_{i}",
                title=f"第{i}章",
                lecture_lines=[f"第{i}章的内容"],
                animations=[f"动画{i}"]
            )
            for i in range(20)
        ]

        with patch('agent.generate_outline', return_value=large_outline), \
             patch('agent.generate_storyboard', return_value=large_storyboard), \
             patch('agent.extract_answer_from_response'), \
             patch('agent.save_code_to_file', return_value=True), \
             patch('agent.run_manim_script', return_value=True):

            # 测试生成大量代码的性能
            import time
            start_time = time.time()

            codes = agent.generate_codes()

            end_time = time.time()
            execution_time = end_time - start_time

            # 验证结果
            assert len(codes) == 20
            assert execution_time < 30  # 应该在30秒内完成

            # 测试状态序列化的性能
            start_time = time.time()
            state = agent.get_serializable_state()
            end_time = time.time()

            assert end_time - start_time < 5  # 状态序列化应该很快
            assert len(state["storyboard"]) == 20