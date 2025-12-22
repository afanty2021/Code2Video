#!/bin/bash

# Code2Video 测试运行脚本
# 提供便捷的测试执行和报告生成功能

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python和pip
check_dependencies() {
    print_info "检查依赖..."

    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 未安装"
        exit 1
    fi

    if ! command -v pip &> /dev/null; then
        print_error "pip 未安装"
        exit 1
    fi

    print_success "依赖检查完成"
}

# 安装测试依赖
install_test_dependencies() {
    print_info "安装测试依赖..."

    # 安装项目依赖
    if [ -f "src/requirements.txt" ]; then
        pip install -r src/requirements.txt
    fi

    # 安装测试依赖
    if [ -f "tests/requirements.txt" ]; then
        pip install -r tests/requirements.txt
    fi

    print_success "测试依赖安装完成"
}

# 创建必要的目录
setup_directories() {
    print_info "设置测试目录..."

    mkdir -p reports
    mkdir -p htmlcov
    mkdir -p .pytest_cache

    print_success "测试目录设置完成"
}

# 运行单元测试
run_unit_tests() {
    print_info "运行单元测试..."

    python -m pytest tests/unit/ \
        -v \
        --tb=short \
        --cov=src \
        --cov-report=html:htmlcov \
        --cov-report=term-missing \
        --cov-report=xml:reports/coverage.xml \
        --html=reports/unit_tests.html \
        --self-contained-html \
        --junitxml=reports/unit_tests.xml \
        -m "unit" \
        --strict-markers

    if [ $? -eq 0 ]; then
        print_success "单元测试通过"
    else
        print_error "单元测试失败"
        return 1
    fi
}

# 运行集成测试
run_integration_tests() {
    print_info "运行集成测试..."

    python -m pytest tests/integration/ \
        -v \
        --tb=short \
        --cov=src \
        --cov-append \
        --cov-report=html:htmlcov \
        --cov-report=term-missing \
        --html=reports/integration_tests.html \
        --self-contained-html \
        --junitxml=reports/integration_tests.xml \
        -m "integration" \
        --strict-markers

    if [ $? -eq 0 ]; then
        print_success "集成测试通过"
    else
        print_error "集成测试失败"
        return 1
    fi
}

# 运行所有测试
run_all_tests() {
    print_info "运行所有测试..."

    python -m pytest tests/ \
        -v \
        --tb=short \
        --cov=src \
        --cov-report=html:htmlcov \
        --cov-report=term-missing \
        --cov-report=xml:reports/coverage.xml \
        --html=reports/all_tests.html \
        --self-contained-html \
        --junitxml=reports/all_tests.xml \
        --strict-markers

    if [ $? -eq 0 ]; then
        print_success "所有测试通过"
    else
        print_error "测试失败"
        return 1
    fi
}

# 运行慢速测试
run_slow_tests() {
    print_info "运行慢速测试..."

    python -m pytest tests/ \
        -v \
        --tb=short \
        -m "slow" \
        --durations=10 \
        --html=reports/slow_tests.html \
        --self-contained-html

    if [ $? -eq 0 ]; then
        print_success "慢速测试通过"
    else
        print_error "慢速测试失败"
        return 1
    fi
}

# 生成测试报告
generate_reports() {
    print_info "生成测试报告..."

    # 检查是否有覆盖率报告
    if [ -f "htmlcov/index.html" ]; then
        print_info "覆盖率报告已生成: htmlcov/index.html"
    fi

    # 检查是否有测试报告
    if ls reports/*.html 1> /dev/null 2>&1; then
        print_info "测试报告已生成在 reports/ 目录中"
    fi

    # 生成摘要报告
    python -c "
import json
import os
from pathlib import Path

def generate_summary():
    reports_dir = Path('reports')
    summary = {
        'test_run_timestamp': '$(date -u +%Y-%m-%dT%H:%M:%SZ)',
        'reports_generated': []
    }

    # 列出所有HTML报告
    for report_file in reports_dir.glob('*.html'):
        summary['reports_generated'].append(report_file.name)

    # 检查覆盖率
    if Path('htmlcov/index.html').exists():
        summary['coverage_report'] = 'htmlcov/index.html'

    # 保存摘要
    with open(reports_dir / 'test_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)

    print('测试摘要报告已生成: reports/test_summary.json')

generate_summary()
"

    print_success "测试报告生成完成"
}

# 清理测试环境
clean_test_environment() {
    print_info "清理测试环境..."

    # 清理Python缓存
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true

    # 清理测试缓存
    rm -rf .pytest_cache

    # 保留覆盖率报告和测试报告，但清理其他临时文件
    find . -name ".coverage" -delete 2>/dev/null || true

    print_success "测试环境清理完成"
}

# 显示帮助信息
show_help() {
    echo "Code2Video 测试运行脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  unit           运行单元测试"
    echo "  integration    运行集成测试"
    echo "  all            运行所有测试（默认）"
    echo "  slow           运行慢速测试"
    echo "  install        安装测试依赖"
    echo "  clean          清理测试环境"
    echo "  report         生成测试报告"
    echo "  help           显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0              # 运行所有测试"
    echo "  $0 unit         # 只运行单元测试"
    echo "  $0 integration  # 只运行集成测试"
    echo "  $0 clean all    # 清理后运行所有测试"
}

# 主函数
main() {
    local command=${1:-all}

    # 解析命令行参数
    case $command in
        "unit")
            check_dependencies
            setup_directories
            run_unit_tests
            generate_reports
            ;;
        "integration")
            check_dependencies
            setup_directories
            run_integration_tests
            generate_reports
            ;;
        "all")
            check_dependencies
            setup_directories
            run_all_tests
            generate_reports
            ;;
        "slow")
            check_dependencies
            setup_directories
            run_slow_tests
            generate_reports
            ;;
        "install")
            check_dependencies
            install_test_dependencies
            ;;
        "clean")
            clean_test_environment
            ;;
        "report")
            generate_reports
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "未知选项: $command"
            show_help
            exit 1
            ;;
    esac

    print_success "脚本执行完成"
}

# 处理组合命令
if [ $# -gt 1 ]; then
    for arg in "$@"; do
        main $arg
    done
else
    main "$@"
fi