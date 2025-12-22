# Code2Video 测试套件

## 概述

Code2Video 项目现在拥有完整的测试套件，包括单元测试、集成测试和详细的测试报告系统。测试套件旨在确保代码质量、功能正确性和系统稳定性。

## 🧪 测试结构

```
tests/
├── __init__.py                    # 测试包初始化
├── conftest.py                   # pytest配置和共享夹具
├── requirements.txt               # 测试依赖
├── test_runner.py                # Python测试运行器
├── report_generator.py           # 测试报告生成器
├── fixtures/                     # 测试夹具和数据
│   └── sample_data.py           # 示例测试数据工厂
├── helpers/                      # 测试辅助工具
│   └── mock_objects.py          # 模拟对象和工具
├── data/                         # 测试数据
│   └── sample_knowledge_mapping.json
├── unit/                         # 单元测试
│   ├── test_agent.py            # 核心代理测试
│   ├── test_utils.py            # 工具函数测试
│   ├── test_eval_aes.py         # 美学评估测试
│   └── test_eval_tq.py          # 教学质量评估测试
└── integration/                  # 集成测试
    ├── test_agent_workflow.py   # 代理工作流测试
    └── test_evaluation_system.py # 评估系统测试
```

## 🚀 快速开始

### 运行所有测试

```bash
# 使用shell脚本
./run_tests.sh

# 或使用Python测试运行器
python tests/test_runner.py test

# 或直接使用pytest
python -m pytest tests/ -v
```

### 运行特定类型的测试

```bash
# 只运行单元测试
./run_tests.sh unit

# 只运行集成测试
./run_tests.sh integration

# 运行慢速测试
./run_tests.sh slow
```

### 生成测试报告

```bash
# 运行测试并生成报告
./run_tests.sh all

# 生成详细报告
python tests/report_generator.py
```

## 📊 测试覆盖范围

### 单元测试覆盖

- **`agent.py`**: TeachingVideoAgent 类的核心功能
- **`utils.py`**: 工具函数和辅助方法
- **`eval_AES.py`**: 美学评估系统
- **`eval_TQ.py`**: 教学质量评估系统

### 集成测试覆盖

- **完整工作流**: 从大纲生成到视频渲染的端到端测试
- **评估系统**: 美学评估和教学质量评估的组合测试
- **错误处理**: 各种异常情况的处理测试
- **性能测试**: 大规模数据处理和并发测试

### 测试标记

- `@pytest.mark.unit`: 单元测试
- `@pytest.mark.integration`: 集成测试
- `@pytest.mark.slow`: 慢速测试（>1秒）
- `@pytest.mark.api`: 需要API调用的测试
- `@pytest.mark.benchmark`: 性能基准测试

## 🛠️ 测试工具和配置

### 主要测试框架

- **pytest**: 主要测试框架
- **pytest-cov**: 代码覆盖率
- **pytest-mock**: 模拟对象
- **pytest-benchmark**: 性能测试

### 代码质量工具

- **flake8**: 代码风格检查
- **black**: 代码格式化
- **isort**: 导入排序
- **mypy**: 类型检查
- **bandit**: 安全检查

### 模拟和测试数据

- **MockAPIResponse**: 模拟API响应
- **MockVideoCapture**: 模拟视频处理
- **MockFileSystem**: 模拟文件系统
- **ProjectDataFactory**: 测试数据工厂

## 📈 测试报告

测试套件会生成多种格式的报告：

1. **HTML报告**: `reports/comprehensive_test_report.html`
2. **JSON报告**: `reports/test_report.json`
3. **摘要报告**: `reports/test_summary.txt`
4. **覆盖率报告**: `htmlcov/index.html`
5. **JUnit XML**: `reports/junit.xml`

### 报告内容

- 测试执行统计
- 失败/错误详情
- 代码覆盖率分析
- 性能基准数据
- 质量评估结果

## 🔄 CI/CD 集成

项目配置了完整的CI/CD流水线：

- **GitHub Actions**: 自动化测试和部署
- **多Python版本**: 3.8, 3.9, 3.10, 3.11
- **并行测试**: 加快执行速度
- **自动报告**: 生成和上传测试报告

### CI流水线步骤

1. 代码质量检查 (lint, format, type-check, security)
2. 依赖安装
3. 单元测试执行
4. 集成测试执行
5. 覆盖率报告生成
6. 性能测试
7. 报告上传和存档

## 📝 编写测试

### 测试文件命名规范

- 单元测试: `test_<module_name>.py`
- 集成测试: `test_<feature_name>_workflow.py`
- 测试类: `Test<ClassName>`
- 测试方法: `test_<feature_description>`

### 测试示例

```python
import pytest
from unittest.mock import Mock, patch

@pytest.mark.unit
class TestExample:
    def test_basic_functionality(self):
        """测试基本功能"""
        # 测试代码
        assert result == expected_value

    @patch('module.external_function')
    def test_with_mock(self, mock_function):
        """使用模拟对象的测试"""
        mock_function.return_value = "mocked_value"
        # 测试代码
        mock_function.assert_called_once()

    @pytest.mark.parametrize("input_data,expected", [
        (1, 2),
        (2, 4),
        (3, 6),
    ])
    def test_parameterized(self, input_data, expected):
        """参数化测试"""
        result = function_to_test(input_data)
        assert result == expected
```

### 最佳实践

1. **测试隔离**: 每个测试应该独立运行
2. **描述性命名**: 测试名称应该清楚描述测试内容
3. **模拟外部依赖**: 使用Mock对象避免外部依赖
4. **断言清晰**: 使用有意义的断言消息
5. **边界测试**: 测试边界条件和异常情况
6. **使用夹具**: 重复使用测试数据和环境

## 🐛 调试测试

### 调试失败的测试

```bash
# 运行特定测试
python -m pytest tests/unit/test_agent.py::TestTeachingVideoAgent::test_generate_outline -v

# 使用pdb调试
python -m pytest tests/unit/test_agent.py::TestTeachingVideoAgent::test_generate_outline --pdb

# 显示详细输出
python -m pytest tests/unit/test_agent.py::TestTeachingVideoAgent::test_generate_outline -v -s

# 只运行失败的测试
python -m pytest --lf -v
```

### 常见问题

1. **导入错误**: 确保src目录在Python路径中
2. **依赖缺失**: 运行 `pip install -r tests/requirements.txt`
3. **权限问题**: 确保测试脚本有执行权限
4. **端口冲突**: 使用不同的测试配置

## 📊 测试统计

当前测试套件覆盖：

- **测试文件数**: 6个主要测试文件
- **测试用例数**: 100+ 个测试用例
- **覆盖率目标**: >80%
- **执行时间**: ~2-5分钟

## 🤝 贡献指南

### 添加新测试

1. 在相应的目录创建测试文件
2. 遵循命名规范
3. 使用适当的测试标记
4. 添加必要的模拟对象
5. 确保测试独立性

### 运行本地测试

```bash
# 安装开发依赖
pip install -r tests/requirements.txt

# 运行所有测试
./run_tests.sh

# 检查代码质量
./run_tests.sh clean all
```

### 提交前检查

```bash
# 运行完整测试套件
python tests/test_runner.py ci

# 确保所有测试通过
python -m pytest tests/ --cov=src --cov-fail-under=80
```

## 🔧 配置自定义

### pytest配置

主要配置在 `pytest.ini` 文件中：

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers --cov=src
```

### 自定义标记

在 `conftest.py` 中定义新的测试标记：

```python
def pytest_configure(config):
    config.addinivalue_line("markers", "custom: 自定义测试标记")
```

## 📚 相关资源

- [pytest官方文档](https://docs.pytest.org/)
- [pytest-cov文档](https://pytest-cov.readthedocs.io/)
- [pytest-mock文档](https://pytest-mock.readthedocs.io/)
- [测试最佳实践](https://docs.pytest.org/en/stable/best.html)

---

**注意**: 这个测试套件是Code2Video项目质量保证的重要组成部分。定期运行测试有助于保持代码质量和系统稳定性。