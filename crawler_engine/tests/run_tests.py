#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試運行腳本
提供便捷的測試執行命令和選項
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from typing import List, Optional

# 添加項目根目錄到Python路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class TestRunner:
    """測試運行器"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent.parent
        
    def run_unit_tests(self, verbose: bool = False, coverage: bool = False) -> int:
        """運行單元測試"""
        cmd = ["pytest", "-m", "unit"]
        if verbose:
            cmd.append("-v")
        if coverage:
            cmd.extend(["--cov=crawler_engine", "--cov-report=html", "--cov-report=term"])
        
        return self._run_command(cmd)
    
    def run_integration_tests(self, verbose: bool = False) -> int:
        """運行集成測試"""
        cmd = ["pytest", "-m", "integration"]
        if verbose:
            cmd.append("-v")
        
        return self._run_command(cmd)
    
    def run_e2e_tests(self, verbose: bool = False) -> int:
        """運行端到端測試"""
        cmd = ["pytest", "-m", "e2e"]
        if verbose:
            cmd.append("-v")
        
        return self._run_command(cmd)
    
    def run_performance_tests(self, verbose: bool = False) -> int:
        """運行性能測試"""
        cmd = ["pytest", "-m", "performance"]
        if verbose:
            cmd.append("-v")
        
        return self._run_command(cmd)
    
    def run_smoke_tests(self, verbose: bool = False) -> int:
        """運行冒煙測試"""
        cmd = ["pytest", "-m", "smoke"]
        if verbose:
            cmd.append("-v")
        
        return self._run_command(cmd)
    
    def run_fast_tests(self, verbose: bool = False, coverage: bool = False) -> int:
        """運行快速測試"""
        cmd = ["pytest", "-m", "fast"]
        if verbose:
            cmd.append("-v")
        if coverage:
            cmd.extend(["--cov=crawler_engine", "--cov-report=html", "--cov-report=term"])
        
        return self._run_command(cmd)
    
    def run_all_tests(self, verbose: bool = False, coverage: bool = False, parallel: bool = False) -> int:
        """運行所有測試"""
        cmd = ["pytest"]
        if verbose:
            cmd.append("-v")
        if coverage:
            cmd.extend(["--cov=crawler_engine", "--cov-report=html", "--cov-report=term"])
        if parallel:
            cmd.extend(["-n", "auto"])
        
        return self._run_command(cmd)
    
    def run_specific_test(self, test_path: str, verbose: bool = False) -> int:
        """運行特定測試"""
        cmd = ["pytest", test_path]
        if verbose:
            cmd.append("-v")
        
        return self._run_command(cmd)
    
    def run_tests_by_keyword(self, keyword: str, verbose: bool = False) -> int:
        """根據關鍵字運行測試"""
        cmd = ["pytest", "-k", keyword]
        if verbose:
            cmd.append("-v")
        
        return self._run_command(cmd)
    
    def generate_coverage_report(self) -> int:
        """生成覆蓋率報告"""
        cmd = [
            "pytest", 
            "--cov=crawler_engine", 
            "--cov-report=html", 
            "--cov-report=term",
            "--cov-report=xml"
        ]
        
        return self._run_command(cmd)
    
    def generate_html_report(self) -> int:
        """生成HTML測試報告"""
        cmd = [
            "pytest", 
            "--html=report.html", 
            "--self-contained-html"
        ]
        
        return self._run_command(cmd)
    
    def run_with_profiling(self) -> int:
        """運行測試並進行性能分析"""
        cmd = [
            "pytest", 
            "--profile",
            "--profile-svg"
        ]
        
        return self._run_command(cmd)
    
    def check_test_dependencies(self) -> bool:
        """檢查測試依賴"""
        required_packages = [
            "pytest",
            "pytest-asyncio",
            "pytest-cov",
            "pytest-html",
            "pytest-xdist",
            "pytest-benchmark",
            "pytest-mock"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"缺少以下測試依賴包: {', '.join(missing_packages)}")
            print(f"請運行: pip install {' '.join(missing_packages)}")
            return False
        
        print("所有測試依賴已安裝")
        return True
    
    def _run_command(self, cmd: List[str]) -> int:
        """運行命令"""
        print(f"運行命令: {' '.join(cmd)}")
        
        # 設置環境變量
        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.project_root)
        env["TESTING"] = "1"
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.test_dir,
                env=env,
                check=False
            )
            return result.returncode
        except KeyboardInterrupt:
            print("\n測試被用戶中斷")
            return 1
        except Exception as e:
            print(f"運行測試時發生錯誤: {e}")
            return 1

def main():
    """主函數"""
    parser = argparse.ArgumentParser(description="爬蟲引擎測試運行器")
    parser.add_argument("-v", "--verbose", action="store_true", help="詳細輸出")
    parser.add_argument("-c", "--coverage", action="store_true", help="生成覆蓋率報告")
    parser.add_argument("-p", "--parallel", action="store_true", help="並行運行測試")
    parser.add_argument("--check-deps", action="store_true", help="檢查測試依賴")
    
    # 測試類型選項
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument("--unit", action="store_true", help="運行單元測試")
    test_group.add_argument("--integration", action="store_true", help="運行集成測試")
    test_group.add_argument("--e2e", action="store_true", help="運行端到端測試")
    test_group.add_argument("--performance", action="store_true", help="運行性能測試")
    test_group.add_argument("--smoke", action="store_true", help="運行冒煙測試")
    test_group.add_argument("--fast", action="store_true", help="運行快速測試")
    test_group.add_argument("--all", action="store_true", help="運行所有測試")
    
    # 特定測試選項
    parser.add_argument("-t", "--test", help="運行特定測試文件或函數")
    parser.add_argument("-k", "--keyword", help="根據關鍵字運行測試")
    
    # 報告選項
    parser.add_argument("--html-report", action="store_true", help="生成HTML報告")
    parser.add_argument("--profile", action="store_true", help="運行性能分析")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # 檢查依賴
    if args.check_deps:
        return 0 if runner.check_test_dependencies() else 1
    
    # 運行特定測試
    if args.test:
        return runner.run_specific_test(args.test, args.verbose)
    
    if args.keyword:
        return runner.run_tests_by_keyword(args.keyword, args.verbose)
    
    # 生成報告
    if args.html_report:
        return runner.generate_html_report()
    
    if args.profile:
        return runner.run_with_profiling()
    
    # 運行測試
    if args.unit:
        return runner.run_unit_tests(args.verbose, args.coverage)
    elif args.integration:
        return runner.run_integration_tests(args.verbose)
    elif args.e2e:
        return runner.run_e2e_tests(args.verbose)
    elif args.performance:
        return runner.run_performance_tests(args.verbose)
    elif args.smoke:
        return runner.run_smoke_tests(args.verbose)
    elif args.fast:
        return runner.run_fast_tests(args.verbose, args.coverage)
    elif args.all:
        return runner.run_all_tests(args.verbose, args.coverage, args.parallel)
    else:
        # 默認運行快速測試
        print("未指定測試類型，運行快速測試...")
        return runner.run_fast_tests(args.verbose, args.coverage)

if __name__ == "__main__":
    sys.exit(main())