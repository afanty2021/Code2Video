"""pytest 配置文件

提供测试夹具和共享配置。
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from dataclasses import dataclass
from typing import Dict, Any, List

# 将src目录添加到Python路径
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from agent import RunConfig, Section, TeachingOutline, VideoFeedback
except ImportError as e:
    # 如果导入失败，创建简化的类用于测试
    print(f"Warning: 无法导入agent模块: {e}")

    from dataclasses import dataclass
    from typing import List, Dict, Any, Optional

    @dataclass
    class Section:
        id: str
        title: str
        lecture_lines: List[str]
        animations: List[str]

    @dataclass
    class TeachingOutline:
        topic: str
        target_audience: str
        sections: List[Dict[str, Any]]

    @dataclass
    class VideoFeedback:
        section_id: str
        video_path: str
        has_issues: bool
        suggested_improvements: List[str]
        raw_response: Optional[str] = None

    @dataclass
    class RunConfig:
        use_feedback: bool = True
        use_assets: bool = True
        api = None
        feedback_rounds: int = 2
        iconfinder_api_key: str = ""
        max_code_token_length: int = 10000
        max_fix_bug_tries: int = 10
        max_regenerate_tries: int = 10
        max_feedback_gen_code_tries: int = 3
        max_mllm_fix_bugs_tries: int = 3


@pytest.fixture
def temp_dir():
    """创建临时目录"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_api_response():
    """模拟API响应"""
    class MockResponse:
        def __init__(self, content: str):
            self.candidates = [Mock()]
            self.candidates[0].content = Mock()
            self.candidates[0].content.parts = [Mock()]
            self.candidates[0].content.parts[0].text = content

    return MockResponse


@pytest.fixture
def mock_run_config():
    """创建模拟运行配置（用于集成测试）"""
    def mock_api_func(prompt, max_tokens=10000):
        """模拟 API 返回 (response, usage) 元组"""
        return '{"topic": "test", "sections": []}', {"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}

    return RunConfig(
        use_feedback=True,
        use_assets=True,
        api=mock_api_func,
        feedback_rounds=1,
        iconfinder_api_key="test_key",
        max_fix_bug_tries=2,
        max_regenerate_tries=2,
        max_feedback_gen_code_tries=2,
        max_mllm_fix_bugs_tries=2
    )


@pytest.fixture
def sample_run_config():
    """示例运行配置"""
    return RunConfig(
        use_feedback=True,
        use_assets=True,
        api=Mock(),
        feedback_rounds=2,
        iconfinder_api_key="test_key",
        max_code_token_length=10000,
        max_fix_bug_tries=3,
        max_regenerate_tries=3,
        max_feedback_gen_code_tries=3,
        max_mllm_fix_bugs_tries=3
    )


@pytest.fixture
def sample_section():
    """示例章节"""
    return Section(
        id="section_1",
        title="导数基础",
        lecture_lines=[
            "导数是微积分的核心概念",
            "它描述了函数在某一点的变化率"
        ],
        animations=[
            "展示切线的形成过程",
            "动画演示极限概念"
        ]
    )


@pytest.fixture
def sample_teaching_outline():
    """示例教学大纲"""
    return TeachingOutline(
        topic="微积分基础",
        target_audience="大学生",
        sections=[
            {
                "id": "section_1",
                "title": "导数基础",
                "content": "导数的定义和几何意义"
            },
            {
                "id": "section_2",
                "title": "求导法则",
                "content": "基本求导公式和法则"
            }
        ]
    )


@pytest.fixture
def sample_video_feedback():
    """示例视频反馈"""
    return VideoFeedback(
        section_id="section_1",
        video_path="/tmp/test_video.mp4",
        has_issues=False,
        suggested_improvements=["提高动画流畅度"],
        raw_response="视频质量良好"
    )


@pytest.fixture
def mock_knowledge_mapping():
    """模拟知识映射"""
    return {
        "导数": "assets/reference/derivative.jpg",
        "积分": "assets/reference/integral.jpg",
        "极限": "assets/reference/limit.jpg"
    }


@pytest.fixture
def sample_manim_code():
    """示例Manim代码"""
    return '''
class DerivativeScene(Scene):
    def construct(self):
        # 创建坐标系
        axes = Axes(
            x_range=[-3, 3],
            y_range=[-2, 2],
            axis_config={"color": BLUE}
        )

        # 创建函数
        func = axes.plot(lambda x: x**2, color=RED)

        # 显示切线
        self.play(Create(axes), Create(func))
        self.wait(1)
'''


@pytest.fixture
def mock_prompts():
    """模拟提示词"""
    return {
        "outline_prompt": "生成教学大纲",
        "storyboard_prompt": "生成故事板",
        "code_prompt": "生成Manim代码"
    }


@pytest.fixture(scope="session")
def test_data_dir():
    """测试数据目录"""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_storyboard_data():
    """示例故事板数据"""
    return {
        "sections": [
            {
                "id": "section_1",
                "title": "导数定义",
                "visual_elements": [
                    {
                        "type": "graph",
                        "description": "函数曲线和切线"
                    },
                    {
                        "type": "text",
                        "content": "导数的数学定义"
                    }
                ],
                "animations": [
                    "展示切线移动过程",
                    "高亮显示导数计算"
                ]
            }
        ]
    }


@pytest.fixture
def mock_json_response():
    """模拟JSON响应"""
    def _create_response(content: str, is_json: bool = True):
        if is_json:
            return f"```json\n{content}\n```"
        return content
    return _create_response


# 测试标记
def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line(
        "markers", "unit: 单元测试"
    )
    config.addinivalue_line(
        "markers", "integration: 集成测试"
    )
    config.addinivalue_line(
        "markers", "slow: 慢速测试"
    )
    config.addinivalue_line(
        "markers", "api: 需要API的测试"
    )