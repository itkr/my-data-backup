"""
テスト実行用スクリプト
"""

import unittest
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def run_all_tests():
    """全てのテストを実行"""
    # テストディスカバリ
    loader = unittest.TestLoader()
    suite = loader.discover('.', pattern='test_*.py')
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_specific_test(test_module):
    """特定のテストモジュールを実行"""
    loader = unittest.TestLoader()
    
    # テストモジュールを直接インポートして実行
    module_path = f'test_{test_module}' if not test_module.startswith('test_') else test_module
    suite = loader.loadTestsFromName(module_path)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # 特定のテストモジュールを実行
        test_module = sys.argv[1]
        print(f"Running tests from {test_module}...")
        success = run_specific_test(test_module)
    else:
        # 全てのテストを実行
        print("Running all tests...")
        success = run_all_tests()
    
    sys.exit(0 if success else 1)
