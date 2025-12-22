"""模拟对象和辅助工具

提供各种测试所需的模拟对象和辅助函数。
"""

import json
import numpy as np
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
import contextlib

# 导入项目模块
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


class MockAPIResponse:
    """模拟API响应"""

    def __init__(self, content: str, success: bool = True):
        self.content = content
        self.success = success

    def __call__(self, *args, **kwargs):
        if self.success:
            return self.content
        else:
            raise Exception("API调用失败")


class MockVideoCapture:
    """模拟视频捕获"""

    def __init__(self, frames: List[np.ndarray], fps: float = 30.0):
        self.frames = frames
        self.fps = fps
        self.current_frame = 0
        self.is_opened_value = True

    def isOpened(self) -> bool:
        return self.is_opened_value

    def read(self) -> tuple[bool, Optional[np.ndarray]]:
        if self.current_frame < len(self.frames):
            frame = self.frames[self.current_frame]
            self.current_frame += 1
            return True, frame
        else:
            return False, None

    def get(self, property_id: int) -> float:
        if property_id == 0:  # CAP_PROP_POS_FRAMES
            return float(self.current_frame)
        elif property_id == 1:  # CAP_PROP_FRAME_COUNT
            return float(len(self.frames))
        elif property_id == 5:  # CAP_PROP_FPS
            return self.fps
        else:
            return 0.0

    def release(self):
        self.is_opened_value = False


class MockManimRenderer:
    """模拟Manim渲染器"""

    def __init__(self, should_succeed: bool = True):
        self.should_succeed = should_succeed
        self.rendered_scenes = []

    def render_scene(self, scene_name: str, code: str, output_path: str) -> bool:
        self.rendered_scenes.append({
            "scene_name": scene_name,
            "code": code,
            "output_path": output_path
        })
        return self.should_succeed


class MockFileSystem:
    """模拟文件系统操作"""

    def __init__(self):
        self.files = {}
        self.directories = set()

    def add_file(self, path: str, content: str = ""):
        """添加文件到模拟文件系统"""
        self.files[path] = content
        # 确保父目录存在
        parent = str(Path(path).parent)
        while parent != "/":
            self.directories.add(parent)
            parent = str(Path(parent).parent)

    def add_directory(self, path: str):
        """添加目录到模拟文件系统"""
        self.directories.add(path)

    def exists(self, path: str) -> bool:
        """检查文件或目录是否存在"""
        return path in self.files or path in self.directories

    def read_file(self, path: str) -> str:
        """读取文件内容"""
        if path in self.files:
            return self.files[path]
        raise FileNotFoundError(f"文件不存在: {path}")

    def write_file(self, path: str, content: str):
        """写入文件内容"""
        self.files[path] = content
        parent = str(Path(path).parent)
        while parent != "/":
            self.directories.add(parent)
            parent = str(Path(parent).parent)

    def list_files(self, directory: str) -> List[str]:
        """列出目录中的文件"""
        return [path for path in self.files.keys() if path.startswith(directory)]


class MockProcessPool:
    """模拟进程池"""

    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers
        self.submitted_tasks = []

    def submit(self, func: Callable, *args, **kwargs):
        """提交任务到进程池"""
        task = {
            "func": func,
            "args": args,
            "kwargs": kwargs,
            "result": None
        }
        self.submitted_tasks.append(task)
        return MockFuture(task)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class MockFuture:
    """模拟Future对象"""

    def __init__(self, task: dict):
        self.task = task
        self._result = None
        self._exception = None

    def set_result(self, result):
        """设置结果"""
        self._result = result

    def set_exception(self, exception):
        """设置异常"""
        self._exception = exception

    def result(self, timeout: Optional[float] = None):
        """获取结果"""
        if self._exception:
            raise self._exception
        return self._result

    def done(self) -> bool:
        """检查是否完成"""
        return self._result is not None or self._exception is not None


class MockTimer:
    """模拟计时器"""

    def __init__(self):
        self.start_time = 0
        self.elapsed_time = 0

    def start(self):
        """开始计时"""
        import time
        self.start_time = time.time()

    def stop(self) -> float:
        """停止计时并返回经过的时间"""
        import time
        self.elapsed_time = time.time() - self.start_time
        return self.elapsed_time

    @contextlib.contextmanager
    def measure(self):
        """测量代码块执行时间的上下文管理器"""
        self.start()
        try:
            yield
        finally:
            self.stop()


class TestEnvironmentBuilder:
    """测试环境构建器"""

    def __init__(self):
        self.mocks = {}
        self.patches = []

    def add_mock_api(self, responses: List[str]):
        """添加模拟API"""
        mock_api = Mock()
        mock_api.side_effect = responses
        self.mocks['api'] = mock_api
        return self

    def add_mock_filesystem(self):
        """添加模拟文件系统"""
        mock_fs = MockFileSystem()
        self.mocks['filesystem'] = mock_fs
        return self

    def add_mock_video_capture(self, frames: List[np.ndarray]):
        """添加模拟视频捕获"""
        mock_capture = MockVideoCapture(frames)
        self.mocks['video_capture'] = mock_capture
        return self

    def add_mock_manim_renderer(self, should_succeed: bool = True):
        """添加模拟Manim渲染器"""
        mock_renderer = MockManimRenderer(should_succeed)
        self.mocks['manim_renderer'] = mock_renderer
        return self

    def add_mock_process_pool(self):
        """添加模拟进程池"""
        mock_pool = MockProcessPool()
        self.mocks['process_pool'] = mock_pool
        return self

    def build(self):
        """构建测试环境"""
        return TestEnvironment(self.mocks, self.patches)


class TestEnvironment:
    """测试环境"""

    def __init__(self, mocks: dict, patches: list):
        self.mocks = mocks
        self.patches = patches
        self.active_patches = []

    def __enter__(self):
        """进入测试环境"""
        # 应用所有补丁
        for patch_obj in self.patches:
            active_patch = patch_obj.start()
            self.active_patches.append(active_patch)

        return self.mocks

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出测试环境"""
        # 停止所有补丁
        for active_patch in self.active_patches:
            active_patch.stop()
        self.active_patches.clear()


class MockDataGenerator:
    """模拟数据生成器"""

    @staticmethod
    def generate_api_responses(count: int, template_func: Callable) -> List[str]:
        """生成API响应"""
        responses = []
        for i in range(count):
            response = template_func(index=i)
            responses.append(response)
        return responses

    @staticmethod
    def generate_video_frames(count: int, pattern: str = "random") -> List[np.ndarray]:
        """生成视频帧"""
        frames = []
        for i in range(count):
            if pattern == "random":
                frame = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
            elif pattern == "gradient":
                frame = np.zeros((100, 100, 3), dtype=np.uint8)
                frame[:, :, 0] = i * 8 % 256  # 红色渐变
                frame[:, :, 1] = (i * 4) % 256  # 绿色渐变
                frame[:, :, 2] = (i * 2) % 256  # 蓝色渐变
            elif pattern == "pattern":
                frame = np.zeros((100, 100, 3), dtype=np.uint8)
                # 创建简单的图案
                frame[i % 100, :] = 255
                frame[:, (i * 3) % 100] = 128
            else:
                frame = np.zeros((100, 100, 3), dtype=np.uint8)
            frames.append(frame)
        return frames

    @staticmethod
    def generate_transcript(topic: str, length: int = 100) -> str:
        """生成转录文本"""
        sentences = [
            f"今天我们学习{topic}的基础知识。",
            f"{topic}是这个领域的核心概念。",
            "让我们通过具体的例子来理解。",
            "这个概念在实际应用中非常重要。",
            "大家要重点掌握基本原理和方法。"
        ]

        transcript = ""
        for i in range(length):
            transcript += sentences[i % len(sentences)] + "\n"

        return transcript


class AssertionHelper:
    """断言辅助工具"""

    @staticmethod
    def assert_valid_evaluation_result(result: dict):
        """断言有效的评估结果"""
        required_keys = ['overall_score', 'recommendations']
        for key in required_keys:
            assert key in result, f"评估结果缺少必需的键: {key}"

        # 检查分数范围
        score_keys = [key for key in result.keys() if 'score' in key]
        for score_key in score_keys:
            score = result[score_key]
            assert isinstance(score, (int, float)), f"{score_key} 应该是数字"
            assert 0 <= score <= 1, f"{score_key} 应该在0-1范围内，实际值: {score}"

    @staticmethod
    def assert_api_call_count(mock_api: Mock, expected_count: int):
        """断言API调用次数"""
        assert mock_api.call_count == expected_count, f"期望API调用{expected_count}次，实际{mock_api.call_count}次"

    @staticmethod
    def assert_file_operations(mock_fs: MockFileSystem, expected_files: List[str]):
        """断言文件操作"""
        for file_path in expected_files:
            assert mock_fs.exists(file_path), f"文件应该存在: {file_path}"

    @staticmethod
    def assert_video_rendering(mock_renderer: MockManimRenderer, expected_scenes: List[str]):
        """断言视频渲染"""
        rendered_scenes = [scene["scene_name"] for scene in mock_renderer.rendered_scenes]
        for scene_name in expected_scenes:
            assert scene_name in rendered_scenes, f"场景应该被渲染: {scene_name}"


class PerformanceTracker:
    """性能跟踪器"""

    def __init__(self):
        self.measurements = {}

    def start_measurement(self, name: str):
        """开始测量"""
        import time
        if name not in self.measurements:
            self.measurements[name] = {"start_time": None, "end_time": None, "duration": None}
        self.measurements[name]["start_time"] = time.time()

    def end_measurement(self, name: str):
        """结束测量"""
        import time
        if name in self.measurements and self.measurements[name]["start_time"]:
            self.measurements[name]["end_time"] = time.time()
            self.measurements[name]["duration"] = (
                self.measurements[name]["end_time"] - self.measurements[name]["start_time"]
            )

    def get_duration(self, name: str) -> Optional[float]:
        """获取测量时长"""
        return self.measurements.get(name, {}).get("duration")

    def assert_performance(self, name: str, max_duration: float):
        """断言性能要求"""
        duration = self.get_duration(name)
        assert duration is not None, f"没有找到测量: {name}"
        assert duration <= max_duration, f"{name} 耗时 {duration:.2f}s，超过最大限制 {max_duration:.2f}s"

    @contextlib.contextmanager
    def measure(self, name: str):
        """测量上下文管理器"""
        self.start_measurement(name)
        try:
            yield
        finally:
            self.end_measurement(name)


# 便捷的装饰器
def with_mock_api(responses: List[str]):
    """使用模拟API的装饰器"""
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            mock_api = Mock()
            mock_api.side_effect = responses
            with patch('agent.api', mock_api):
                return test_func(*args, mock_api=mock_api, **kwargs)
        return wrapper
    return decorator


def with_mock_video(frames: List[np.ndarray]):
    """使用模拟视频的装饰器"""
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            mock_capture = MockVideoCapture(frames)
            with patch('cv2.VideoCapture', return_value=mock_capture):
                return test_func(*args, video_capture=mock_capture, **kwargs)
        return wrapper
    return decorator


def with_temp_directory():
    """使用临时目录的装饰器"""
    def decorator(test_func):
        def wrapper(*args, **kwargs):
            import tempfile
            with tempfile.TemporaryDirectory() as temp_dir:
                return test_func(*args, temp_dir=temp_dir, **kwargs)
        return wrapper
    return decorator