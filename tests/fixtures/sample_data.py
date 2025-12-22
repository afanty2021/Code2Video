"""测试数据和固定装置

提供各种测试所需的示例数据和模拟对象。
"""

import json
import numpy as np
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any

# 导入项目模块
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from agent import Section, TeachingOutline, VideoFeedback, RunConfig


@dataclass
class SampleProject:
    """示例项目数据"""
    name: str
    topic: str
    target_audience: str
    sections: List[Dict[str, Any]]
    transcripts: List[str]
    expected_outcomes: Dict[str, float]


class ProjectDataFactory:
    """项目数据工厂"""

    @staticmethod
    def create_calculus_project() -> SampleProject:
        """创建微积分项目数据"""
        return SampleProject(
            name="微积分基础",
            topic="微积分基础",
            target_audience="大学生",
            sections=[
                {
                    "id": "section_1",
                    "title": "导数的定义",
                    "key_concepts": ["极限", "变化率", "切线斜率"],
                    "duration": "8分钟",
                    "content": "导数是微积分的核心概念，描述函数在某点的瞬时变化率"
                },
                {
                    "id": "section_2",
                    "title": "基本求导法则",
                    "key_concepts": ["幂函数", "常数倍", "四则运算"],
                    "duration": "10分钟",
                    "content": "掌握基本的求导公式和运算法则"
                },
                {
                    "id": "section_3",
                    "title": "导数的应用",
                    "key_concepts": ["极值", "优化", "物理应用"],
                    "duration": "12分钟",
                    "content": "导数在解决实际问题中的应用"
                }
            ],
            transcripts=[
                """
                欢迎来到微积分课程。今天我们学习导数的概念。

                导数描述了函数在某一点的变化率。想象一下你在开车的速度表，
                它显示的就是位移对时间的导数。

                数学上，导数的定义是：f'(x) = lim(h→0)[f(x+h) - f(x)]/h

                这个公式告诉我们如何计算导数。
                """,
                """
                现在我们学习基本的求导法则。

                对于幂函数f(x) = x^n，导数是f'(x) = n*x^(n-1)。

                例如，f(x) = x³的导数是f'(x) = 3x²。

                常数倍的导数是常数乘以原函数的导数。
                """,
                """
                导数有很多实际应用。

                在物理学中，速度是位移对时间的导数，
                加速度是速度对时间的导数。

                在优化问题中，我们可以用导数找到函数的极值点。
                """
            ],
            expected_outcomes={
                "content_accuracy": 0.9,
                "engagement_level": 0.7,
                "pedagogical_effectiveness": 0.8
            }
        )

    @staticmethod
    def create_programming_project() -> SampleProject:
        """创建编程项目数据"""
        return SampleProject(
            name="Python基础",
            topic="Python编程基础",
            target_audience="初学者",
            sections=[
                {
                    "id": "section_1",
                    "title": "变量和数据类型",
                    "key_concepts": ["变量", "字符串", "数字", "列表"],
                    "duration": "6分钟"
                },
                {
                    "id": "section_2",
                    "title": "控制结构",
                    "key_concepts": ["if语句", "循环", "条件判断"],
                    "duration": "8分钟"
                },
                {
                    "id": "section_3",
                    "title": "函数定义",
                    "key_concepts": ["def", "参数", "返回值", "作用域"],
                    "duration": "10分钟"
                }
            ],
            transcripts=[
                """
                Python是一种简洁的编程语言。

                变量就像盒子，可以存放数据。
                例如：name = "张明"，age = 20

                Python有几种基本数据类型：整数、浮点数、字符串、列表等。
                """,
                """
                控制结构让程序能够做出决策。

                if语句用于条件判断：
                if score > 90:
                    print("优秀")

                for循环用于重复执行代码。
                """,
                """
                函数是可重用的代码块。

                def greet(name):
                    return f"你好，{name}！"

                函数可以接收参数并返回结果。
                """
            ],
            expected_outcomes={
                "content_accuracy": 0.85,
                "engagement_level": 0.8,
                "pedagogical_effectiveness": 0.75
            }
        )


class VideoDataFactory:
    """视频数据工厂"""

    @staticmethod
    def create_high_quality_frames(num_frames: int = 30) -> List[np.ndarray]:
        """创建高质量视频帧"""
        frames = []
        for i in range(num_frames):
            frame = np.zeros((100, 100, 3), dtype=np.uint8)

            # 添加清晰的边缘和结构
            frame[50, :] = 255  # 水平线
            frame[:, 50] = 255  # 垂直线

            # 添加色彩变化
            if i % 3 == 0:
                frame[i*3:(i+1)*3, :] = [255, 0, 0]  # 红色
            elif i % 3 == 1:
                frame[i*3:(i+1)*3, :] = [0, 255, 0]  # 绿色
            else:
                frame[i*3:(i+1)*3, :] = [0, 0, 255]  # 蓝色

            frames.append(frame)

        return frames

    @staticmethod
    def create_low_quality_frames(num_frames: int = 30) -> List[np.ndarray]:
        """创建低质量视频帧"""
        frames = []
        for i in range(num_frames):
            # 模糊的帧
            frame = np.ones((100, 100, 3), dtype=np.uint8) * 128

            # 添加少量噪声
            noise = np.random.randint(-20, 20, (100, 100, 3))
            frame = np.clip(frame + noise, 0, 255).astype(np.uint8)

            frames.append(frame)

        return frames

    @staticmethod
    def create_mixed_quality_frames(num_frames: int = 30) -> List[np.ndarray]:
        """创建混合质量视频帧"""
        frames = []
        for i in range(num_frames):
            if i % 2 == 0:
                # 高质量帧
                frame = np.zeros((100, 100, 3), dtype=np.uint8)
                frame[50, :] = 255
                frame[:, 50] = 255
                frame[i*2:(i+1)*2, :] = [255, 200, 100]
            else:
                # 低质量帧
                frame = np.ones((100, 100, 3), dtype=np.uint8) * 150
                noise = np.random.randint(-15, 15, (100, 100, 3))
                frame = np.clip(frame + noise, 0, 255).astype(np.uint8)

            frames.append(frame)

        return frames


class APIResponseFactory:
    """API响应工厂"""

    @staticmethod
    def create_outline_response(topic: str = "微积分基础") -> str:
        """创建大纲生成API响应"""
        return json.dumps({
            "topic": topic,
            "target_audience": "大学生",
            "sections": [
                {
                    "id": "section_1",
                    "title": "基本概念",
                    "content": "介绍基本概念",
                    "key_concepts": ["概念1", "概念2"]
                },
                {
                    "id": "section_2",
                    "title": "核心理论",
                    "content": "讲解核心理论",
                    "key_concepts": ["理论1", "理论2"]
                }
            ]
        })

    @staticmethod
    def create_storyboard_response() -> str:
        """创建故事板生成API响应"""
        return json.dumps({
            "sections": [
                {
                    "id": "section_1",
                    "title": "导数定义",
                    "lecture_lines": [
                        "导数是函数的变化率",
                        "通过极限概念定义"
                    ],
                    "animations": [
                        "展示切线形成",
                        "演示极限过程"
                    ],
                    "visual_elements": [
                        {"type": "graph", "description": "函数图像"},
                        {"type": "text", "content": "导数公式"}
                    ]
                }
            ]
        })

    @staticmethod
    def create_code_response(scene_name: str = "DerivativeScene") -> str:
        """创建代码生成API响应"""
        return f'''
class {scene_name}(Scene):
    def construct(self):
        # 创建标题
        title = Text("导数的定义").scale(0.8)
        title.to_edge(UP)

        # 创建坐标系
        axes = Axes(
            x_range=[-2, 2],
            y_range=[-1, 3],
            axis_config={{"color": BLUE}}
        )

        # 创建函数曲线
        func = axes.plot(lambda x: x**2, color=RED)

        # 显示切线
        self.play(Create(axes), Create(func))
        self.play(Write(title))
        self.wait(1)
'''

    @staticmethod
    def create_feedback_response(has_issues: bool = False) -> str:
        """创建反馈API响应"""
        response = {
            "has_issues": has_issues,
            "suggested_improvements": [],
            "overall_quality": "良好" if not has_issues else "需要改进"
        }

        if has_issues:
            response["suggested_improvements"] = [
                "提高动画流畅度",
                "增加更多实例",
                "优化色彩搭配"
            ]

        return json.dumps(response)


class MockDataFactory:
    """模拟数据工厂"""

    @staticmethod
    def create_run_config() -> RunConfig:
        """创建运行配置"""
        from unittest.mock import Mock
        return RunConfig(
            use_feedback=True,
            use_assets=True,
            api=Mock(),
            feedback_rounds=2,
            iconfinder_api_key="test_api_key",
            max_code_token_length=8000,
            max_fix_bug_tries=3,
            max_regenerate_tries=3
        )

    @staticmethod
    def create_sample_section(section_id: str = "section_1") -> Section:
        """创建示例章节"""
        return Section(
            id=section_id,
            title=f"章节 {section_id}",
            lecture_lines=[f"这是{section_id}的内容", "重要的知识点"],
            animations=[f"动画{section_id}_1", f"动画{section_id}_2"]
        )

    @staticmethod
    def create_sample_outline() -> TeachingOutline:
        """创建示例教学大纲"""
        return TeachingOutline(
            topic="示例主题",
            target_audience="目标受众",
            sections=[
                {"id": "1", "title": "第一部分", "content": "第一部分内容"},
                {"id": "2", "title": "第二部分", "content": "第二部分内容"}
            ]
        )

    @staticmethod
    def create_sample_video_feedback() -> VideoFeedback:
        """创建示例视频反馈"""
        return VideoFeedback(
            section_id="section_1",
            video_path="/tmp/test_video.mp4",
            has_issues=False,
            suggested_improvements=["改进建议1"],
            raw_response="原始反馈内容"
        )


class TestDataManager:
    """测试数据管理器"""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)

    def save_project_data(self, project: SampleProject):
        """保存项目数据到文件"""
        project_file = self.data_dir / f"{project.name}.json"

        data = {
            "name": project.name,
            "topic": project.topic,
            "target_audience": project.target_audience,
            "sections": project.sections,
            "transcripts": project.transcripts,
            "expected_outcomes": project.expected_outcomes
        }

        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_project_data(self, project_name: str) -> SampleProject:
        """从文件加载项目数据"""
        project_file = self.data_dir / f"{project_name}.json"

        with open(project_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return SampleProject(
            name=data["name"],
            topic=data["topic"],
            target_audience=data["target_audience"],
            sections=data["sections"],
            transcripts=data["transcripts"],
            expected_outcomes=data["expected_outcomes"]
        )

    def generate_test_datasets(self):
        """生成测试数据集"""
        # 生成项目数据
        calculus_project = ProjectDataFactory.create_calculus_project()
        programming_project = ProjectDataFactory.create_programming_project()

        self.save_project_data(calculus_project)
        self.save_project_data(programming_project)

        # 生成API响应数据
        api_responses_dir = self.data_dir / "api_responses"
        api_responses_dir.mkdir(exist_ok=True)

        responses = {
            "outline": APIResponseFactory.create_outline_response(),
            "storyboard": APIResponseFactory.create_storyboard_response(),
            "code": APIResponseFactory.create_code_response(),
            "feedback": APIResponseFactory.create_feedback_response(),
            "feedback_with_issues": APIResponseFactory.create_feedback_response(has_issues=True)
        }

        for name, response in responses.items():
            response_file = api_responses_dir / f"{name}.json"
            with open(response_file, 'w', encoding='utf-8') as f:
                f.write(response)

        # 生成视频数据
        video_data_dir = self.data_dir / "video_data"
        video_data_dir.mkdir(exist_ok=True)

        # 保存帧数据的统计信息
        high_quality_frames = VideoDataFactory.create_high_quality_frames()
        low_quality_frames = VideoDataFactory.create_low_quality_frames()

        frame_stats = {
            "high_quality": {
                "count": len(high_quality_frames),
                "avg_brightness": np.mean([np.mean(frame) for frame in high_quality_frames]),
                "avg_contrast": np.mean([np.std(frame) for frame in high_quality_frames])
            },
            "low_quality": {
                "count": len(low_quality_frames),
                "avg_brightness": np.mean([np.mean(frame) for frame in low_quality_frames]),
                "avg_contrast": np.mean([np.std(frame) for frame in low_quality_frames])
            }
        }

        stats_file = video_data_dir / "frame_statistics.json"
        with open(stats_file, 'w') as f:
            json.dump(frame_stats, f, indent=2)


# 预定义的测试常量
TEST_CONSTANTS = {
    "MAX_TEST_DURATION": 30,  # 最大测试持续时间（秒）
    "SAMPLE_FRAME_SIZE": (100, 100),  # 示例帧大小
    "MIN_QUALITY_SCORE": 0.6,  # 最小质量分数
    "MAX_API_RETRIES": 3,  # 最大API重试次数
    "DEFAULT_FPS": 30,  # 默认帧率
    "TEST_AUDIO_SAMPLE_RATE": 44100,  # 测试音频采样率
    "MOCK_API_DELAY": 0.1,  # 模拟API延迟（秒）
}

# 常用测试断言助手
class AssertionHelpers:
    """断言助手类"""

    @staticmethod
    def assert_score_range(score: float, min_val: float = 0.0, max_val: float = 1.0):
        """断言分数在有效范围内"""
        assert isinstance(score, (int, float)), f"分数应该是数字，实际是 {type(score)}"
        assert min_val <= score <= max_val, f"分数 {score} 超出范围 [{min_val}, {max_val}]"

    @staticmethod
    def assert_required_keys(data: dict, required_keys: list):
        """断言字典包含所有必需的键"""
        missing_keys = [key for key in required_keys if key not in data]
        assert not missing_keys, f"缺少必需的键: {missing_keys}"

    @staticmethod
    def assert_video_frame_shape(frame: np.ndarray, expected_shape: tuple = None):
        """断言视频帧形状正确"""
        expected_shape = expected_shape or TEST_CONSTANTS["SAMPLE_FRAME_SIZE"] + (3,)
        assert frame.shape == expected_shape, f"帧形状 {frame.shape} 不等于期望的 {expected_shape}"

    @staticmethod
    def assert_api_response_structure(response: dict):
        """断言API响应结构正确"""
        assert isinstance(response, dict), "API响应应该是字典"
        # 可以添加更多结构检查