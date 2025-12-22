"""评估系统集成测试"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import json
import tempfile
from pathlib import Path
import sys
import os

# 添加src到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from eval_AES import AestheticEvaluator
    from eval_TQ import TeachingQualityEvaluator
except ImportError as e:
    pytest.skip(f"无法导入评估模块: {e}", allow_module_level=True)


@pytest.mark.integration
class TestEvaluationSystemIntegration:
    """测试评估系统的集成功能"""

    @pytest.fixture
    def sample_video_content(self):
        """示例视频内容"""
        return {
            "transcript": """
            欢迎来到微积分基础课程。今天我们将学习导数的概念。

            导数是微积分的核心概念之一，它描述了函数在某一点上的瞬时变化率。
            让我们通过一个具体的例子来理解导数的定义。

            考虑函数f(x) = x²，我们想求它在x = 1处的导数。
            根据导数的定义，我们需要计算极限：
            f'(1) = lim(h→0) [f(1+h) - f(1)] / h

            大家想一想，这个极限值代表了什么？
            没错，它代表了函数在x=1处的切线斜率。

            通过这个例子，我们可以看到导数的几何意义。
            """,
            "outline": {
                "topic": "导数基础",
                "target_audience": "大学生",
                "learning_objectives": [
                    "理解导数的定义",
                    "掌握基本求导方法",
                    "了解导数的几何意义"
                ],
                "sections": [
                    {
                        "id": "1",
                        "title": "导数的定义",
                        "key_concepts": ["极限", "变化率", "切线斜率"],
                        "duration": "8分钟"
                    },
                    {
                        "id": "2",
                        "title": "几何意义",
                        "key_concepts": ["切线", "曲线斜率", "图像分析"],
                        "duration": "7分钟"
                    }
                ]
            },
            "video_frames": [
                # 创建不同质量的分析帧
                np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8) for _ in range(10)
            ]
        }

    @pytest.fixture
    def high_quality_frames(self):
        """高质量视频帧"""
        frames = []
        for i in range(10):
            frame = np.zeros((100, 100, 3), dtype=np.uint8)
            # 添加清晰的边缘
            frame[50, :] = 255
            frame[:, 50] = 255
            # 添加一些颜色变化
            frame[i*10:(i+1)*10, :] = [255, 255, 0]
            frames.append(frame)
        return frames

    @pytest.fixture
    def low_quality_frames(self):
        """低质量视频帧"""
        frames = []
        for i in range(10):
            # 模糊的帧
            frame = np.ones((100, 100, 3), dtype=np.uint8) * 128
            # 添加一些噪声，但结构不清楚
            noise = np.random.randint(-10, 10, (100, 100, 3))
            frame = np.clip(frame + noise, 0, 255).astype(np.uint8)
            frames.append(frame)
        return frames

    @pytest.mark.integration
    def test_combined_evaluation_workflow(
        self,
        sample_video_content,
        high_quality_frames,
        temp_dir
    ):
        """测试组合评估工作流"""
        # 创建评估器
        aesthetic_evaluator = AestheticEvaluator()
        teaching_evaluator = TeachingQualityEvaluator()

        # 模拟视频路径
        video_path = temp_dir / "test_video.mp4"
        video_path.touch()

        # 模拟视频读取
        with patch('eval_aes.cv2.VideoCapture') as mock_cv2:
            mock_cap = Mock()
            mock_cap.isOpened.return_value = True
            mock_cap.read.return_value = (True, high_quality_frames[0])
            mock_cap.get.side_effect = [30.0, len(high_quality_frames)]
            mock_cv2.return_value = mock_cap

            # 执行美学评估
            aesthetic_result = aesthetic_evaluator.evaluate_video(str(video_path))

            # 执行教学质量评估
            teaching_result = teaching_evaluator.evaluate_teaching_quality(
                transcript=sample_video_content["transcript"],
                outline=sample_video_content["outline"],
                target_audience="大学生"
            )

            # 验证两个评估都成功
            assert isinstance(aesthetic_result, dict)
            assert isinstance(teaching_result, dict)

            # 验证美学评估结果
            required_aes_keys = [
                'overall_score', 'frame_clarity', 'color_harmony',
                'visual_balance', 'motion_smoothness', 'recommendations'
            ]
            for key in required_aes_keys:
                assert key in aesthetic_result

            # 验证教学质量评估结果
            required_tq_keys = [
                'overall_score', 'content_accuracy', 'pedagogical_effectiveness',
                'engagement_level', 'completeness', 'recommendations'
            ]
            for key in required_tq_keys:
                assert key in teaching_result

            # 验证分数范围
            assert 0 <= aesthetic_result['overall_score'] <= 1
            assert 0 <= teaching_result['overall_score'] <= 1

    @pytest.mark.integration
    def test_evaluation_consistency(
        self,
        sample_video_content,
        high_quality_frames,
        low_quality_frames,
        temp_dir
    ):
        """测试评估一致性"""
        aesthetic_evaluator = AestheticEvaluator()
        teaching_evaluator = TeachingQualityEvaluator()

        # 高质量视频评估
        high_quality_video = temp_dir / "high_quality.mp4"
        high_quality_video.touch()

        with patch('eval_aes.cv2.VideoCapture') as mock_cv2:
            mock_cap = Mock()
            mock_cap.isOpened.return_value = True
            mock_cap.read.return_value = (True, high_quality_frames[0])
            mock_cap.get.side_effect = [30.0, len(high_quality_frames)]
            mock_cv2.return_value = mock_cap

            high_quality_result = aesthetic_evaluator.evaluate_video(str(high_quality_video))

        # 低质量视频评估
        low_quality_video = temp_dir / "low_quality.mp4"
        low_quality_video.touch()

        with patch('eval_aes.cv2.VideoCapture') as mock_cv2:
            mock_cap = Mock()
            mock_cap.isOpened.return_value = True
            mock_cap.read.return_value = (True, low_quality_frames[0])
            mock_cap.get.side_effect = [30.0, len(low_quality_frames)]
            mock_cv2.return_value = mock_cap

            low_quality_result = aesthetic_evaluator.evaluate_video(str(low_quality_video))

        # 验证质量差异被正确识别
        assert high_quality_result['frame_clarity'] > low_quality_result['frame_clarity']

        # 多次评估同一内容应该得到相似结果
        with patch('eval_aes.cv2.VideoCapture') as mock_cv2:
            mock_cap = Mock()
            mock_cap.isOpened.return_value = True
            mock_cap.read.return_value = (True, high_quality_frames[0])
            mock_cap.get.side_effect = [30.0, len(high_quality_frames)]
            mock_cv2.return_value = mock_cap

            result1 = aesthetic_evaluator.evaluate_video(str(high_quality_video))
            result2 = aesthetic_evaluator.evaluate_video(str(high_quality_video))

            # 分数应该非常接近（考虑到可能的随机性）
            assert abs(result1['overall_score'] - result2['overall_score']) < 0.1

    @pytest.mark.integration
    def test_cross_domain_evaluation(
        self,
        temp_dir
    ):
        """测试跨领域评估"""
        aesthetic_evaluator = AestheticEvaluator()
        teaching_evaluator = TeachingQualityEvaluator()

        # 不同学科的内容
        domains = [
            {
                "name": "数学",
                "transcript": "函数f(x) = x²的导数是f'(x) = 2x。这是根据导数的定义计算得出的。",
                "outline": {
                    "topic": "导数计算",
                    "sections": [{"title": "基本求导", "key_concepts": ["幂函数", "求导公式"]}]
                }
            },
            {
                "name": "物理",
                "transcript": "牛顿第二定律表明F = ma。这个公式描述了力与加速度的关系。",
                "outline": {
                    "topic": "力学基础",
                    "sections": [{"title": "牛顿定律", "key_concepts": ["力", "质量", "加速度"]}]
                }
            },
            {
                "name": "编程",
                "transcript": "Python中的列表推导式提供了一种简洁的创建列表的方法。例如：[x**2 for x in range(10)]。",
                "outline": {
                    "topic": "Python基础",
                    "sections": [{"title": "列表操作", "key_concepts": ["列表推导式", "循环", "语法"]}]
                }
            }
        ]

        results = {}
        for domain in domains:
            result = teaching_evaluator.evaluate_teaching_quality(
                transcript=domain["transcript"],
                outline=domain["outline"],
                target_audience="初学者"
            )
            results[domain["name"]] = result

        # 验证所有领域都能被评估
        for domain_name, result in results.items():
            assert isinstance(result, dict)
            assert 0 <= result['overall_score'] <= 1
            assert 'recommendations' in result
            assert len(result['recommendations']) > 0

    @pytest.mark.integration
    def test_evaluation_error_handling(self, temp_dir):
        """测试评估错误处理"""
        aesthetic_evaluator = AestheticEvaluator()
        teaching_evaluator = TeachingQualityEvaluator()

        # 测试无效视频文件
        invalid_video = temp_dir / "nonexistent.mp4"

        with patch('eval_aes.cv2.VideoCapture') as mock_cv2:
            mock_cap = Mock()
            mock_cap.isOpened.return_value = False
            mock_cv2.return_value = mock_cap

            with pytest.raises(Exception):
                aesthetic_evaluator.evaluate_video(str(invalid_video))

        # 测试空内容
        empty_result = teaching_evaluator.evaluate_teaching_quality(
            transcript="",
            outline={},
            target_audience="学生"
        )

        # 空内容应该有处理，不应该崩溃
        assert isinstance(empty_result, dict)
        assert empty_result['overall_score'] == 0.0

        # 测试损坏的JSON
        with pytest.raises((json.JSONDecodeError, KeyError)):
            teaching_evaluator.evaluate_teaching_quality(
                transcript="正常内容",
                outline="不是JSON对象",
                target_audience="学生"
            )

    @pytest.mark.integration
    def test_performance_evaluation(
        self,
        sample_video_content,
        high_quality_frames,
        temp_dir
    ):
        """测试评估性能"""
        aesthetic_evaluator = AestheticEvaluator()
        teaching_evaluator = TeachingQualityEvaluator()

        # 测试大量帧的处理性能
        large_frame_set = high_quality_frames * 10  # 100帧

        video_path = temp_dir / "large_video.mp4"
        video_path.touch()

        import time

        # 美学评估性能测试
        with patch('eval_aes.cv2.VideoCapture') as mock_cv2:
            mock_cap = Mock()
            mock_cap.isOpened.return_value = True

            def mock_read():
                if hasattr(mock_read, 'frame_index'):
                    mock_read.frame_index += 1
                else:
                    mock_read.frame_index = 0

                if mock_read.frame_index < len(large_frame_set):
                    return True, large_frame_set[mock_read.frame_index]
                return False, None

            mock_cap.read = mock_read
            mock_cap.get.side_effect = [30.0, len(large_frame_set)]
            mock_cv2.return_value = mock_cap

            start_time = time.time()
            aesthetic_result = aesthetic_evaluator.evaluate_video(str(video_path))
            aesthetic_time = time.time() - start_time

            # 教学质量评估性能测试
            start_time = time.time()
            teaching_result = teaching_evaluator.evaluate_teaching_quality(
                transcript=sample_video_content["transcript"],
                outline=sample_video_content["outline"],
                target_audience="大学生"
            )
            teaching_time = time.time() - start_time

            # 验证性能要求
            assert aesthetic_time < 30  # 美学评估应该在30秒内完成
            assert teaching_time < 10   # 教学评估应该在10秒内完成

            # 验证结果的正确性
            assert aesthetic_result['overall_score'] >= 0
            assert teaching_result['overall_score'] >= 0


@pytest.mark.integration
class TestEvaluationReportGeneration:
    """测试评估报告生成"""

    @pytest.fixture
    def evaluation_results(self):
        """示例评估结果"""
        return {
            "aesthetic": {
                "overall_score": 0.85,
                "frame_clarity": 0.90,
                "color_harmony": 0.80,
                "visual_balance": 0.85,
                "motion_smoothness": 0.85,
                "recommendations": [
                    "保持当前的清晰度水平",
                    "可以适当增加色彩对比度"
                ]
            },
            "teaching": {
                "overall_score": 0.78,
                "content_accuracy": 0.90,
                "pedagogical_effectiveness": 0.75,
                "engagement_level": 0.70,
                "completeness": 0.80,
                "recommendations": [
                    "增加更多互动元素",
                    "提供更多实例说明",
                    "适当简化复杂概念"
                ]
            }
        }

    @pytest.mark.integration
    def test_comprehensive_report_generation(
        self,
        evaluation_results,
        temp_dir
    ):
        """测试综合报告生成"""
        report_path = temp_dir / "evaluation_report.json"

        # 生成综合报告
        comprehensive_report = {
            "video_id": "test_video_001",
            "topic": "导数基础",
            "evaluation_date": "2025-12-22",
            "evaluator_version": "1.0.0",
            "aesthetic_evaluation": evaluation_results["aesthetic"],
            "teaching_quality_evaluation": evaluation_results["teaching"],
            "overall_assessment": {
                "combined_score": (evaluation_results["aesthetic"]["overall_score"] +
                                 evaluation_results["teaching"]["overall_score"]) / 2,
                "strengths": [
                    "内容准确度很高",
                    "视频质量良好",
                    "概念覆盖完整"
                ],
                "areas_for_improvement": [
                    "提高教学互动性",
                    "优化视觉表现"
                ],
                "recommendation_priority": [
                    {"priority": "high", "item": "增加互动环节"},
                    {"priority": "medium", "item": "改善色彩设计"},
                    {"priority": "low", "item": "微调动画时长"}
                ]
            }
        }

        # 保存报告
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_report, f, ensure_ascii=False, indent=2)

        # 验证报告生成
        assert report_path.exists()

        # 读取并验证报告内容
        with open(report_path, 'r', encoding='utf-8') as f:
            loaded_report = json.load(f)

        assert loaded_report["video_id"] == "test_video_001"
        assert "overall_assessment" in loaded_report
        assert "combined_score" in loaded_report["overall_assessment"]

    @pytest.mark.integration
    def test_batch_evaluation_report(
        self,
        evaluation_results,
        temp_dir
    ):
        """测试批量评估报告"""
        # 模拟多个视频的评估结果
        batch_results = []
        for i in range(5):
            result = {
                "video_id": f"video_{i:03d}",
                "topic": f"主题_{i}",
                "aesthetic_score": 0.8 + i * 0.02,
                "teaching_score": 0.75 + i * 0.03,
                "evaluation_timestamp": f"2025-12-22T{10+i}:00:00Z"
            }
            batch_results.append(result)

        # 生成批量报告
        batch_report = {
            "batch_id": "batch_001",
            "evaluation_date": "2025-12-22",
            "total_videos": len(batch_results),
            "summary_statistics": {
                "average_aesthetic_score": sum(r["aesthetic_score"] for r in batch_results) / len(batch_results),
                "average_teaching_score": sum(r["teaching_score"] for r in batch_results) / len(batch_results),
                "highest_rated_video": max(batch_results, key=lambda x: x["aesthetic_score"] + x["teaching_score"]),
                "lowest_rated_video": min(batch_results, key=lambda x: x["aesthetic_score"] + x["teaching_score"])
            },
            "detailed_results": batch_results
        }

        # 保存批量报告
        report_path = temp_dir / "batch_evaluation_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(batch_report, f, ensure_ascii=False, indent=2)

        # 验证批量报告
        assert report_path.exists()

        with open(report_path, 'r', encoding='utf-8') as f:
            loaded_report = json.load(f)

        assert loaded_report["total_videos"] == 5
        assert "summary_statistics" in loaded_report
        assert len(loaded_report["detailed_results"]) == 5