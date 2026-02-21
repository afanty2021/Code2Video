# 集成测试

> [根目录](../CLAUDE.md) > [tests](./CLAUDE.md) > **integration**

## 测试文件列表

| 文件 | 测试目标 |
|------|----------|
| `test_agent_workflow.py` | 端到端视频生成工作流 |
| `test_evaluation_system.py` | 评估系统集成测试 |

## 测试内容

### test_agent_workflow.py

- 完整视频生成流程测试
- 多章节视频生成测试
- 错误恢复和重试机制测试

### test_evaluation_system.py

- 美学评估系统端到端测试
- 教学评估系统端到端测试
- 批量评估流程测试

## 运行集成测试

```bash
# 使用 pytest
python -m pytest tests/integration/ -v

# 运行特定测试文件
python -m pytest tests/integration/test_agent_workflow.py -v

# 使用测试运行器
python tests/test_runner.py test --type integration
```

---

*最后更新：2026-02-21*
