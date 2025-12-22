#!/usr/bin/env python3
"""
测试报告生成器

生成详细的HTML测试报告和覆盖率报告。
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import subprocess
import xml.etree.ElementTree as ET


class TestReportGenerator:
    """测试报告生成器"""

    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.reports_dir = self.root_dir / "reports"
        self.coverage_dir = self.root_dir / "htmlcov"

        # 确保报告目录存在
        self.reports_dir.mkdir(exist_ok=True)
        self.coverage_dir.mkdir(exist_ok=True)

    def load_junit_results(self) -> Dict[str, Any]:
        """加载JUnit XML测试结果"""
        junit_files = list(self.reports_dir.glob("*.xml"))
        results = {
            "total_tests": 0,
            "failures": 0,
            "errors": 0,
            "skipped": 0,
            "test_suites": []
        }

        for junit_file in junit_files:
            try:
                tree = ET.parse(junit_file)
                root = tree.getroot()

                for testsuite in root.findall('testsuite'):
                    suite_info = {
                        "name": testsuite.get("name", ""),
                        "tests": int(testsuite.get("tests", 0)),
                        "failures": int(testsuite.get("failures", 0)),
                        "errors": int(testsuite.get("errors", 0)),
                        "skipped": int(testsuite.get("skipped", 0)),
                        "time": float(testsuite.get("time", 0)),
                        "test_cases": []
                    }

                    results["total_tests"] += suite_info["tests"]
                    results["failures"] += suite_info["failures"]
                    results["errors"] += suite_info["errors"]
                    results["skipped"] += suite_info["skipped"]

                    # 收集测试用例详情
                    for testcase in testsuite.findall('testcase'):
                        case_info = {
                            "name": testcase.get("name", ""),
                            "classname": testcase.get("classname", ""),
                            "time": float(testcase.get("time", 0)),
                            "status": "passed"
                        }

                        # 检查失败
                        failure = testcase.find('failure')
                        if failure is not None:
                            case_info["status"] = "failed"
                            case_info["failure_message"] = failure.get("message", "")

                        # 检查错误
                        error = testcase.find('error')
                        if error is not None:
                            case_info["status"] = "error"
                            case_info["error_message"] = error.get("message", "")

                        # 检查跳过
                        skipped = testcase.find('skipped')
                        if skipped is not None:
                            case_info["status"] = "skipped"
                            case_info["skip_message"] = skipped.get("message", "")

                        suite_info["test_cases"].append(case_info)

                    results["test_suites"].append(suite_info)

            except Exception as e:
                print(f"解析JUnit文件失败 {junit_file}: {e}")

        return results

    def load_coverage_data(self) -> Dict[str, Any]:
        """加载覆盖率数据"""
        coverage_file = self.reports_dir / "coverage.xml"
        if not coverage_file.exists():
            return {}

        try:
            tree = ET.parse(coverage_file)
            root = tree.getroot()

            coverage_data = {
                "line_rate": 0.0,
                "branch_rate": 0.0,
                "packages": []
            }

            for package in root.findall('.//package'):
                package_info = {
                    "name": package.get("name", ""),
                    "line_rate": float(package.get("line-rate", 0)),
                    "branch_rate": float(package.get("branch-rate", 0)),
                    "classes": []
                }

                for cls in package.findall('.//class'):
                    class_info = {
                        "name": cls.get("name", ""),
                        "filename": cls.get("filename", ""),
                        "line_rate": float(cls.get("line-rate", 0)),
                        "branch_rate": float(cls.get("branch-rate", 0)),
                        "lines": []
                    }

                    for line in cls.findall('.//line'):
                        line_info = {
                            "number": int(line.get("number", 0)),
                            "hits": int(line.get("hits", 0))
                        }
                        class_info["lines"].append(line_info)

                    package_info["classes"].append(class_info)

                coverage_data["packages"].append(package_info)

            # 计算总体覆盖率
            if coverage_data["packages"]:
                total_line_rate = sum(p["line_rate"] for p in coverage_data["packages"])
                coverage_data["line_rate"] = total_line_rate / len(coverage_data["packages"])

            return coverage_data

        except Exception as e:
            print(f"解析覆盖率文件失败: {e}")
            return {}

    def generate_html_report(self, test_results: Dict[str, Any], coverage_data: Dict[str, Any]) -> str:
        """生成HTML报告"""
        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code2Video 测试报告</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }
        .header h1 {
            color: #2c3e50;
            margin: 0;
            font-size: 2.5em;
        }
        .header .timestamp {
            color: #7f8c8d;
            margin-top: 10px;
        }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .summary-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #3498db;
        }
        .summary-card.success {
            border-left-color: #27ae60;
        }
        .summary-card.warning {
            border-left-color: #f39c12;
        }
        .summary-card.danger {
            border-left-color: #e74c3c;
        }
        .summary-card h3 {
            margin: 0 0 10px 0;
            color: #2c3e50;
        }
        .summary-card .value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .summary-card .label {
            color: #7f8c8d;
            font-size: 0.9em;
        }
        .section {
            margin-bottom: 40px;
        }
        .section h2 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .test-suite {
            margin-bottom: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            overflow: hidden;
        }
        .test-suite-header {
            background: #f8f9fa;
            padding: 15px;
            border-bottom: 1px solid #e0e0e0;
        }
        .test-suite-header h3 {
            margin: 0;
            color: #2c3e50;
        }
        .test-suite-stats {
            margin-top: 10px;
            font-size: 0.9em;
            color: #7f8c8d;
        }
        .test-cases {
            max-height: 300px;
            overflow-y: auto;
        }
        .test-case {
            padding: 10px 15px;
            border-bottom: 1px solid #f0f0f0;
        }
        .test-case:last-child {
            border-bottom: none;
        }
        .test-case.passed {
            background-color: #d4edda;
        }
        .test-case.failed {
            background-color: #f8d7da;
        }
        .test-case.error {
            background-color: #f5c6cb;
        }
        .test-case.skipped {
            background-color: #fff3cd;
        }
        .test-case-name {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .test-case-details {
            font-size: 0.9em;
            color: #666;
        }
        .coverage-bar {
            width: 100%;
            height: 20px;
            background-color: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 10px;
        }
        .coverage-fill {
            height: 100%;
            background: linear-gradient(90deg, #e74c3c, #f39c12, #27ae60);
            transition: width 0.3s ease;
        }
        .coverage-text {
            text-align: center;
            margin-top: 5px;
            font-weight: bold;
        }
        .progress-bar {
            width: 100%;
            height: 8px;
            background-color: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 5px;
        }
        .progress-fill {
            height: 100%;
            background-color: #3498db;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            color: #7f8c8d;
        }
        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }
            .summary {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 Code2Video 测试报告</h1>
            <div class="timestamp">生成时间: {timestamp}</div>
        </div>

        <div class="summary">
            <div class="summary-card success">
                <div class="value">{total_tests}</div>
                <div class="label">总测试数</div>
            </div>
            <div class="summary-card {passed_status}">
                <div class="value">{passed_tests}</div>
                <div class="label">通过测试</div>
            </div>
            <div class="summary-card {failed_status}">
                <div class="value">{failed_tests}</div>
                <div class="label">失败测试</div>
            </div>
            <div class="summary-card {coverage_status}">
                <div class="value">{coverage_percentage:.1f}%</div>
                <div class="label">代码覆盖率</div>
            </div>
        </div>

        <div class="section">
            <h2>📊 覆盖率详情</h2>
            <div class="coverage-bar">
                <div class="coverage-fill" style="width: {coverage_percentage}%;"></div>
            </div>
            <div class="coverage-text">行覆盖率: {coverage_percentage:.1f}% | 分支覆盖率: {branch_percentage:.1f}%</div>
        </div>

        <div class="section">
            <h2>🧪 测试套件详情</h2>
            {test_suites_html}
        </div>

        <div class="section">
            <h2>📈 覆盖率分析</h2>
            {coverage_details_html}
        </div>

        <div class="footer">
            <p>报告由 Code2Video 测试系统自动生成</p>
        </div>
    </div>

    <script>
        // 添加交互功能
        document.addEventListener('DOMContentLoaded', function() {
            // 为测试用例添加点击展开功能
            const testCases = document.querySelectorAll('.test-case');
            testCases.forEach(function(testCase) {
                testCase.addEventListener('click', function() {
                    this.classList.toggle('expanded');
                });
            });
        });
    </script>
</body>
</html>
        """

        # 计算统计数据
        total_tests = test_results["total_tests"]
        failed_tests = test_results["failures"] + test_results["errors"]
        passed_tests = total_tests - failed_tests - test_results["skipped"]
        coverage_percentage = coverage_data.get("line_rate", 0) * 100
        branch_percentage = coverage_data.get("branch_rate", 0) * 100

        # 确定状态颜色
        passed_status = "success" if failed_tests == 0 else "danger"
        failed_status = "success" if failed_tests == 0 else "danger"
        coverage_status = "success" if coverage_percentage >= 80 else "warning" if coverage_percentage >= 60 else "danger"

        # 生成测试套件HTML
        test_suites_html = ""
        for suite in test_results["test_suites"]:
            status_class = "success" if suite["failures"] == 0 and suite["errors"] == 0 else "danger"

            test_cases_html = ""
            for case in suite["test_cases"][:10]:  # 只显示前10个测试用例
                test_cases_html += f"""
                <div class="test-case {case['status']}">
                    <div class="test-case-name">{case['name']}</div>
                    <div class="test-case-details">
                        类: {case['classname']} | 耗时: {case['time']:.3f}s
                    </div>
                </div>
                """

            test_suites_html += f"""
            <div class="test-suite">
                <div class="test-suite-header">
                    <h3>{suite['name']}</h3>
                    <div class="test-suite-stats">
                        测试: {suite['tests']} |
                        通过: {suite['tests'] - suite['failures'] - suite['errors'] - suite['skipped']} |
                        失败: {suite['failures']} |
                        错误: {suite['errors']} |
                        跳过: {suite['skipped']} |
                        耗时: {suite['time']:.3f}s
                    </div>
                </div>
                <div class="test-cases">
                    {test_cases_html}
                </div>
            </div>
            """

        # 生成覆盖率详情HTML
        coverage_details_html = ""
        for package in coverage_data.get("packages", [])[:5]:  # 只显示前5个包
            classes_html = ""
            for cls in package["classes"][:3]:  # 每个包只显示前3个类
                classes_html += f"""
                <tr>
                    <td>{cls['name']}</td>
                    <td>{cls['line_rate']:.1%}</td>
                    <td>{cls['branch_rate']:.1%}</td>
                    <td><a href="htmlcov/{cls['filename']}.html">查看详情</a></td>
                </tr>
                """

            coverage_details_html += f"""
            <div style="margin-bottom: 20px;">
                <h4>{package['name']} (覆盖率: {package['line_rate']:.1%})</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background-color: #f8f9fa;">
                            <th style="padding: 10px; text-align: left; border: 1px solid #dee2e6;">类名</th>
                            <th style="padding: 10px; text-align: left; border: 1px solid #dee2e6;">行覆盖率</th>
                            <th style="padding: 10px; text-align: left; border: 1px solid #dee2e6;">分支覆盖率</th>
                            <th style="padding: 10px; text-align: left; border: 1px solid #dee2e6;">详情</th>
                        </tr>
                    </thead>
                    <tbody>
                        {classes_html}
                    </tbody>
                </table>
            </div>
            """

        return html_template.format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            passed_status=passed_status,
            failed_status=failed_status,
            coverage_percentage=coverage_percentage,
            branch_percentage=branch_percentage,
            coverage_status=coverage_status,
            test_suites_html=test_suites_html,
            coverage_details_html=coverage_details_html
        )

    def generate_json_report(self, test_results: Dict[str, Any], coverage_data: Dict[str, Any]) -> str:
        """生成JSON格式的报告"""
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "generator": "Code2Video Test Report Generator",
                "version": "1.0.0"
            },
            "summary": {
                "total_tests": test_results["total_tests"],
                "passed": test_results["total_tests"] - test_results["failures"] - test_results["errors"] - test_results["skipped"],
                "failed": test_results["failures"] + test_results["errors"],
                "skipped": test_results["skipped"],
                "coverage_percentage": coverage_data.get("line_rate", 0) * 100,
                "branch_coverage_percentage": coverage_data.get("branch_rate", 0) * 100
            },
            "test_results": test_results,
            "coverage_data": coverage_data
        }

        return json.dumps(report, indent=2, ensure_ascii=False)

    def generate_summary_report(self) -> str:
        """生成简要摘要报告"""
        test_results = self.load_junit_results()
        coverage_data = self.load_coverage_data()

        summary = []
        summary.append("=" * 50)
        summary.append("Code2Video 测试报告摘要")
        summary.append("=" * 50)
        summary.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append("")

        # 测试结果摘要
        summary.append("📊 测试结果:")
        summary.append(f"  总测试数: {test_results['total_tests']}")
        summary.append(f"  通过: {test_results['total_tests'] - test_results['failures'] - test_results['errors'] - test_results['skipped']}")
        summary.append(f"  失败: {test_results['failures'] + test_results['errors']}")
        summary.append(f"  跳过: {test_results['skipped']}")
        summary.append("")

        # 覆盖率摘要
        summary.append("📈 代码覆盖率:")
        summary.append(f"  行覆盖率: {coverage_data.get('line_rate', 0) * 100:.1f}%")
        summary.append(f"  分支覆盖率: {coverage_data.get('branch_rate', 0) * 100:.1f}%")
        summary.append("")

        # 状态评估
        total_tests = test_results['total_tests']
        failed_tests = test_results['failures'] + test_results['errors']
        coverage_percentage = coverage_data.get('line_rate', 0) * 100

        summary.append("🎯 质量评估:")
        if failed_tests == 0 and coverage_percentage >= 80:
            summary.append("  ✅ 优秀: 所有测试通过，覆盖率良好")
        elif failed_tests == 0 and coverage_percentage >= 60:
            summary.append("  ⚠️  良好: 所有测试通过，但覆盖率有待提高")
        elif failed_tests > 0:
            summary.append("  ❌ 需要改进: 存在测试失败")
        else:
            summary.append("  📝 状态未知")

        return "\n".join(summary)

    def save_reports(self):
        """保存所有报告"""
        print("🔄 生成测试报告...")

        # 加载数据
        test_results = self.load_junit_results()
        coverage_data = self.load_coverage_data()

        # 生成HTML报告
        html_report = self.generate_html_report(test_results, coverage_data)
        html_file = self.reports_dir / "comprehensive_test_report.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_report)
        print(f"✅ HTML报告已生成: {html_file}")

        # 生成JSON报告
        json_report = self.generate_json_report(test_results, coverage_data)
        json_file = self.reports_dir / "test_report.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            f.write(json_report)
        print(f"✅ JSON报告已生成: {json_file}")

        # 生成摘要报告
        summary_report = self.generate_summary_report()
        summary_file = self.reports_dir / "test_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary_report)
        print(f"✅ 摘要报告已生成: {summary_file}")

        # 打印摘要
        print("\n" + summary_report)


def main():
    """主函数"""
    generator = TestReportGenerator()
    generator.save_reports()


if __name__ == "__main__":
    main()