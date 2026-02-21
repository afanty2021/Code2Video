# 单元测试

> [根目录](../CLAUDE.md) > [tests](./CLAUDE.md) > **unit**

## 测试文件列表

| 文件 | 测试目标 | 测试类 |
|------|----------|--------|
| `test_agent.py` | 核心代理 TeachingVideoAgent 功能 | `TestSection`, `TestTeachingOutline`, `TestVideoFeedback`, `TestRunConfig`, `TestTeachingVideoAgent` |
| `test_utils.py` | 工具函数（路径处理、视频处理等） | `TestUtilsFunctions` |
| `test_eval_aes.py` | 美学评估系统 | `TestVideoEvaluator` |
| `test_eval_tq.py` | 教学质量评估系统 | `TestSelectiveKnowledgeUnlearning` |

## 测试类详情

### test_agent.py

```python
@pytest.mark.unit
class TestSection:
    """测试 Section 数据类"""
    def test_section_creation(self)
    def test_section_empty_lists(self)

@pytest.mark.unit
class TestTeachingOutline:
    """测试 TeachingOutline 数据类"""
    def test_teaching_outline_creation(self)

@pytest.mark.unit
class TestVideoFeedback:
    """测试 VideoFeedback 数据类"""
    def test_video_feedback_creation(self)
    def test_video_feedback_with_defaults(self)

@pytest.mark.unit
class TestRunConfig:
    """测试 RunConfig 数据类"""
    def test_run_config_defaults(self)
    def test_run_config_custom_values(self)

@pytest.mark.unit
class TestTeachingVideoAgent:
    """测试 TeachingVideoAgent 类"""
    def test_agent_initialization(self)
    def test_generate_outline(self)
    def test_generate_storyboard(self)
    def test_generate_section_code(self)
    def test_debug_and_fix_code_success(self)
    def test_get_mllm_feedback(self)
    def test_optimize_with_feedback_no_issues(self)
```

## 运行单元测试

```bash
# 使用 pytest
python -m pytest tests/unit/ -v

# 运行特定测试类
python -m pytest tests/unit/test_agent.py::TestTeachingVideoAgent -v

# 使用测试运行器
python tests/test_runner.py test --type unit
```

---

*最后更新：2026-02-21*
