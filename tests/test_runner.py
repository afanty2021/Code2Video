#!/usr/bin/env python3
"""
高级测试运行器

提供更灵活的测试配置和执行选项。
"""

import argparse
import sys
import os
import subprocess
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
import time


class TestRunner:
    """测试运行器"""

    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.src_dir = self.root_dir / "src"
        self.tests_dir = self.root_dir / "tests"
        self.reports_dir = self.root_dir / "reports"
        self.coverage_dir = self.root_dir / "htmlcov"

        # 确保报告目录存在
        self.reports_dir.mkdir(exist_ok=True)
        self.coverage_dir.mkdir(exist_ok=True)

    def run_command(self, cmd: List[str], description: str) -> bool:
        """运行命令并返回是否成功"""
        print(f"\n🔄 {description}...")
        print(f"执行命令: {' '.join(cmd)}")

        try:
            start_time = time.time()
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            duration = time.time() - start_time

            print(f"✅ {description}完成 (耗时: {duration:.2f}秒)")
            if result.stdout:
                print("输出:", result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)

            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ {description}失败")
            print("错误:", e.stderr[:500] + "..." if len(e.stderr) > 500 else e.stderr)
            return False

    def install_dependencies(self) -> bool:
        """安装依赖"""
        # 安装项目依赖
        project_req = self.src_dir / "requirements.txt"
        if project_req.exists():
            cmd = ["pip", "install", "-r", str(project_req)]
            if not self.run_command(cmd, "安装项目依赖"):
                return False

        # 安装测试依赖
        test_req = self.tests_dir / "requirements.txt"
        if test_req.exists():
            cmd = ["pip", "install", "-r", str(test_req)]
            if not self.run_command(cmd, "安装测试依赖"):
                return False

        return True

    def run_pytest(
        self,
        test_path: Optional[str] = None,
        markers: Optional[List[str]] = None,
        coverage: bool = True,
        parallel: bool = False,
        verbose: bool = True,
        html_report: bool = True
    ) -> bool:
        """运行pytest测试"""

        # 构建pytest命令
        cmd = ["python", "-m", "pytest"]

        # 添加测试路径
        if test_path:
            cmd.append(test_path)
        else:
            cmd.append(str(self.tests_dir))

        # 添加选项
        if verbose:
            cmd.append("-v")

        cmd.extend(["--tb=short", "--strict-markers", "--strict-config"])

        # 添加覆盖率选项
        if coverage:
            cmd.extend([
                "--cov=src",
                "--cov-report=html:" + str(self.coverage_dir),
                "--cov-report=term-missing",
                "--cov-report=xml:" + str(self.reports_dir / "coverage.xml")
            ])

        # 添加标记过滤器
        if markers:
            cmd.extend(["-m", " or ".join(markers)])

        # 添加并行执行
        if parallel:
            cmd.extend(["-n", "auto"])

        # 添加HTML报告
        if html_report:
            report_name = f"test_report_{int(time.time())}.html"
            cmd.extend([
                "--html", str(self.reports_dir / report_name),
                "--self-contained-html"
            ])

        # 添加JUnit XML报告
        cmd.extend(["--junitxml", str(self.reports_dir / "junit.xml")])

        # 执行测试
        return self.run_command(cmd, "运行pytest测试")

    def run_linting(self) -> bool:
        """运行代码质量检查"""
        success = True

        # 运行flake8
        cmd = ["python", "-m", "flake8", "src/", "tests/"]
        if not self.run_command(cmd, "flake8代码检查"):
            success = False

        # 运行black格式检查
        cmd = ["python", "-m", "black", "--check", "src/", "tests/"]
        if not self.run_command(cmd, "black格式检查"):
            success = False

        # 运行isort导入排序检查
        cmd = ["python", "-m", "isort", "--check-only", "src/", "tests/"]
        if not self.run_command(cmd, "isort导入排序检查"):
            success = False

        return success

    def run_type_checking(self) -> bool:
        """运行类型检查"""
        cmd = ["python", "-m", "mypy", "src/"]
        return self.run_command(cmd, "mypy类型检查")

    def run_security_check(self) -> bool:
        """运行安全检查"""
        cmd = ["python", "-m", "bandit", "-r", "src/"]
        return self.run_command(cmd, "bandit安全检查")

    def generate_test_matrix(self) -> Dict[str, Any]:
        """生成测试矩阵"""
        return {
            "test_types": {
                "unit": {
                    "path": "tests/unit/",
                    "markers": ["unit"],
                    "description": "单元测试"
                },
                "integration": {
                    "path": "tests/integration/",
                    "markers": ["integration"],
                    "description": "集成测试"
                },
                "api": {
                    "path": "tests/",
                    "markers": ["api"],
                    "description": "API测试"
                },
                "slow": {
                    "path": "tests/",
                    "markers": ["slow"],
                    "description": "慢速测试"
                }
            },
            "quality_checks": {
                "linting": "代码风格和质量检查",
                "type_checking": "类型检查",
                "security": "安全检查"
            }
        }

    def run_ci_pipeline(self) -> bool:
        """运行CI流水线"""
        print("\n🚀 开始CI流水线...")
        success = True

        # 1. 安装依赖
        if not self.install_dependencies():
            return False

        # 2. 代码质量检查
        if not self.run_linting():
            success = False

        # 3. 类型检查
        if not self.run_type_checking():
            success = False

        # 4. 安全检查
        if not self.run_security_check():
            success = False

        # 5. 运行测试
        if not self.run_pytest():
            success = False

        return success

    def clean_environment(self) -> bool:
        """清理测试环境"""
        print("\n🧹 清理测试环境...")

        # 清理Python缓存
        cleanup_commands = [
            ["find", ".", "-type", "d", "-name", "__pycache__", "-exec", "rm", "-rf", "{}", "+"],
            ["find", ".", "-type", "f", "-name", "*.pyc", "-delete"],
            ["rm", "-rf", ".pytest_cache"],
            ["rm", "-f", ".coverage"]
        ]

        for cmd in cleanup_commands:
            try:
                subprocess.run(cmd, check=False, capture_output=True)
            except:
                pass

        print("✅ 测试环境清理完成")
        return True

    def show_test_summary(self) -> None:
        """显示测试摘要"""
        print("\n📊 测试摘要:")
        print("=" * 50)

        # 统计测试文件
        test_files = list(self.tests_dir.rglob("test_*.py"))
        print(f"📁 测试文件数量: {len(test_files)}")

        # 统计测试用例
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "--collect-only", "-q"],
                capture_output=True,
                text=True,
                cwd=self.root_dir
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                test_count = len([line for line in lines if line and not line.startswith("tests/")])
                print(f"🧪 测试用例数量: {test_count}")
        except:
            print("🧪 无法统计测试用例数量")

        # 显示报告文件
        if self.reports_dir.exists():
            report_files = list(self.reports_dir.glob("*"))
            print(f"📄 报告文件数量: {len(report_files)}")

        print("=" * 50)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Code2Video高级测试运行器")
    parser.add_argument(
        "command",
        choices=["install", "test", "lint", "type-check", "security", "ci", "clean", "summary"],
        help="要执行的命令"
    )
    parser.add_argument(
        "--path",
        help="指定测试路径 (仅用于test命令)"
    )
    parser.add_argument(
        "--markers",
        nargs="+",
        help="指定测试标记 (仅用于test命令)"
    )
    parser.add_argument(
        "--no-coverage",
        action="store_true",
        help="不生成覆盖率报告 (仅用于test命令)"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="并行执行测试 (仅用于test命令)"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="静默模式 (仅用于test命令)"
    )

    args = parser.parse_args()
    runner = TestRunner()

    # 切换到项目根目录
    os.chdir(runner.root_dir)

    success = True

    if args.command == "install":
        success = runner.install_dependencies()

    elif args.command == "test":
        success = runner.run_pytest(
            test_path=args.path,
            markers=args.markers,
            coverage=not args.no_coverage,
            parallel=args.parallel,
            verbose=not args.quiet
        )

    elif args.command == "lint":
        success = runner.run_linting()

    elif args.command == "type-check":
        success = runner.run_type_checking()

    elif args.command == "security":
        success = runner.run_security_check()

    elif args.command == "ci":
        success = runner.run_ci_pipeline()

    elif args.command == "clean":
        success = runner.clean_environment()

    elif args.command == "summary":
        runner.show_test_summary()

    # 退出状态
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()