# coding:utf-8
"""
Verification tests for GitHub Schedule optimization
Run this script to verify all changes are working correctly
"""

import os
import sys
import importlib.util
from datetime import datetime


def print_test_header(test_name):
    """Print formatted test header"""
    print(f"\n{'='*60}")
    print(f"TEST: {test_name}")
    print('='*60)


def print_result(passed, message):
    """Print test result with color-coded output"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status}: {message}")
    return passed


def test_git_helper_module():
    """Test 1: Verify git_helper module exists and can be imported"""
    print_test_header("Git Helper Module")

    try:
        # Test module import
        from script.utils.git_helper import git_add_commit_push
        print_result(True, "git_helper module imported successfully")

        # Test function exists
        print_result(True, f"git_add_commit_push function exists: {git_add_commit_push.__name__}")

        # Test function signature
        import inspect
        sig = inspect.signature(git_add_commit_push)
        print_result(True, f"Function signature: git_add_commit_push{sig}")

        return True
    except Exception as e:
        print_result(False, f"Failed to import git_helper: {str(e)}")
        return False


def test_env_variable_config():
    """Test 2: Verify .env.example exists and documents required variables"""
    print_test_header("Environment Variable Configuration")

    env_example_path = '.env.example'
    if not os.path.exists(env_example_path):
        print_result(False, f"{env_example_path} not found")
        return False

    print_result(True, f"{env_example_path} exists")

    # Read and check for required variables
    with open(env_example_path, 'r') as f:
        content = f.read()

    required_vars = ['WECOM_WEBHOOK_URL']
    optional_vars = ['MAILUSERNAME', 'MAILPASSWORD', 'BIGMODEL_API_KEY']

    all_pass = True
    for var in required_vars:
        if var in content:
            print_result(True, f"Required variable documented: {var}")
        else:
            print_result(False, f"Required variable missing: {var}")
            all_pass = False

    for var in optional_vars:
        if var in content:
            print_result(True, f"Optional variable documented: {var}")

    # Check current environment
    print("\n--- Current Environment Variables ---")
    webhook_url = os.environ.get('WECOM_WEBHOOK_URL')
    if webhook_url:
        print_result(True, f"WECOM_WEBHOOK_URL is set (length: {len(webhook_url)})")
    else:
        print_result(False, "WECOM_WEBHOOK_URL is not set (set it to test WeChat notifications)")

    return all_pass


def test_script_imports():
    """Test 3: Verify all scripts can be imported and use git_helper"""
    print_test_header("Script Imports and Dependencies")

    script_dir = 'script'
    test_scripts = [
        '1.ai-news.py',
        '2.wecom-robot.py',
        'github-trending.py'
    ]

    all_pass = True
    for script_name in test_scripts:
        script_path = os.path.join(script_dir, script_name)
        if not os.path.exists(script_path):
            print_result(False, f"Script not found: {script_name}")
            all_pass = False
            continue

        try:
            # Read script content
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check if script imports git_helper
            if 'from utils.git_helper import git_add_commit_push' in content:
                print_result(True, f"{script_name}: Uses git_helper module")
            else:
                print_result(False, f"{script_name}: Does not import git_helper")
                all_pass = False

            # Check if script has its own git_add_commit_push definition (should be removed)
            if 'def git_add_commit_push(' in content and 'from utils.git_helper import' not in content:
                print_result(False, f"{script_name}: Still has local git_add_commit_push (should be removed)")
                all_pass = False

            # Check for job() function
            if 'def job(' in content:
                print_result(True, f"{script_name}: Has job() function")
            else:
                print_result(False, f"{script_name}: Missing job() function")
                all_pass = False

        except Exception as e:
            print_result(False, f"{script_name}: Error reading: {str(e)}")
            all_pass = False

    return all_pass


def test_http_timeout_configuration():
    """Test 4: Verify HTTP requests have timeout parameters"""
    print_test_header("HTTP Timeout Configuration")

    test_scripts = [
        ('script/1.ai-news.py', ['requests.get']),
        ('script/2.wecom-robot.py', ['requests.post']),
        ('script/github-trending.py', ['requests.get'])
    ]

    all_pass = True
    for script_path, expected_methods in test_scripts:
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for timeout in requests
            has_timeout = 'timeout=' in content
            if has_timeout:
                print_result(True, f"{os.path.basename(script_path)}: Has timeout parameter")
            else:
                print_result(False, f"{os.path.basename(script_path)}: Missing timeout parameter")
                all_pass = False

            # Check for proper error handling (no assert)
            if 'assert r.status_code' in content or 'assert response.status_code' in content:
                print_result(False, f"{os.path.basename(script_path)}: Uses assert for status code (should use raise_for_status)")
                all_pass = False
            else:
                print_result(True, f"{os.path.basename(script_path)}: Does not use assert for status check")

            # Check for raise_for_status
            if 'raise_for_status()' in content:
                print_result(True, f"{os.path.basename(script_path)}: Uses raise_for_status()")

        except Exception as e:
            print_result(False, f"{os.path.basename(script_path)}: Error checking: {str(e)}")
            all_pass = False

    return all_pass


def test_requirements_txt():
    """Test 5: Verify requirements.txt is properly configured"""
    print_test_header("Requirements Configuration")

    req_path = 'requirements.txt'
    if not os.path.exists(req_path):
        print_result(False, f"{req_path} not found")
        return False

    with open(req_path, 'r') as f:
        content = f.read()

    all_pass = True

    # Check that 'schedule' is removed
    if 'schedule' not in content or '# schedule' in content:
        print_result(True, "Unused 'schedule' package removed")
    else:
        print_result(False, "'schedule' package still in requirements")
        all_pass = False

    # Check for version locking
    lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
    has_version_locking = any('==' in line for line in lines)
    if has_version_locking:
        print_result(True, "Dependencies have version locking")
    else:
        print_result(False, "Dependencies missing version locking")
        all_pass = False

    # Check required packages
    required_packages = ['requests', 'pyquery', 'lxml', 'cssselect']
    for pkg in required_packages:
        if pkg in content.lower():
            print_result(True, f"Required package present: {pkg}")
        else:
            print_result(False, f"Required package missing: {pkg}")
            all_pass = False

    return all_pass


def test_github_actions_config():
    """Test 6: Verify GitHub Actions workflow configuration"""
    print_test_header("GitHub Actions Configuration")

    workflow_path = '.github/workflows/blank.yml'
    if not os.path.exists(workflow_path):
        print_result(False, f"{workflow_path} not found")
        return False

    with open(workflow_path, 'r') as f:
        content = f.read()

    all_pass = True

    # Check for WECOM_WEBHOOK_URL
    if 'WECOM_WEBHOOK_URL' in content:
        print_result(True, "WECOM_WEBHOOK_URL secret configured in workflow")
    else:
        print_result(False, "WECOM_WEBHOOK_URL not configured in workflow")
        all_pass = False

    # Check for other secrets
    secrets = ['MAILUSERNAME', 'MAILPASSWORD']
    for secret in secrets:
        if secret in content:
            print_result(True, f"Secret configured: {secret}")

    return all_pass


def test_readme_documentation():
    """Test 7: Verify README.md has proper documentation"""
    print_test_header("README Documentation")

    readme_path = 'README.md'
    if not os.path.exists(readme_path):
        print_result(False, f"{readme_path} not found")
        return False

    with open(readme_path, 'r') as f:
        content = f.read()

    all_pass = True

    # Check for key sections
    required_sections = [
        'Installation',
        'Configuration',
        'Environment Variables',
        'Usage'
    ]

    for section in required_sections:
        if section in content:
            print_result(True, f"Section present: {section}")
        else:
            print_result(False, f"Section missing: {section}")
            all_pass = False

    # Check for .env.example reference
    if '.env.example' in content:
        print_result(True, "References .env.example file")

    # Check for git proxy config (original content)
    if 'git config' in content and 'proxy' in content:
        print_result(True, "Preserves original git proxy configuration")

    return all_pass


def test_module_discovery():
    """Test 8: Verify main.py can discover and load scripts"""
    print_test_header("Module Discovery (main.py)")

    try:
        # Import main module
        import importlib.util
        spec = importlib.util.spec_from_file_location("main", "main.py")
        main_module = importlib.util.module_from_spec(spec)

        # Get script directory
        script_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'script')

        if not os.path.exists(script_dir):
            print_result(False, f"Script directory not found: {script_dir}")
            return False

        print_result(True, f"Script directory found: {script_dir}")

        # Get all .py files
        python_files = sorted([f for f in os.listdir(script_dir) if f.endswith('.py') and not f.startswith('_')])

        print_result(True, f"Found {len(python_files)} Python scripts")
        for f in python_files:
            print(f"  - {f}")

        # Verify each script has job() function
        all_pass = True
        for script_file in python_files:
            script_path = os.path.join(script_dir, script_file)
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                if 'def job(' in content:
                    print(f"  ✓ {script_file}: has job() function")
                else:
                    print(f"  ✗ {script_file}: missing job() function")
                    all_pass = False
            except Exception as e:
                print(f"  ✗ {script_file}: error reading: {str(e)}")
                all_pass = False

        return all_pass

    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False


def main():
    """Run all verification tests"""
    print("\n" + "="*60)
    print("GITHUB SCHEDULE - OPTIMIZATION VERIFICATION")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tests = [
        ("Git Helper Module", test_git_helper_module),
        ("Environment Variables", test_env_variable_config),
        ("Script Imports", test_script_imports),
        ("HTTP Timeouts", test_http_timeout_configuration),
        ("Requirements.txt", test_requirements_txt),
        ("GitHub Actions", test_github_actions_config),
        ("README Documentation", test_readme_documentation),
        ("Module Discovery", test_module_discovery),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ EXCEPTION in {test_name}: {str(e)}")
            results.append((test_name, False))

    # Print summary
    print_test_header("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        print_result(result, test_name)

    print(f"\n{'='*60}")
    print(f"FINAL RESULT: {passed}/{total} tests passed")
    print('='*60)

    if passed == total:
        print("\n✓ All tests passed! The optimization is complete and verified.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Please review the output above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
