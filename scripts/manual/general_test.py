# coding:utf-8
"""
Quick manual test script for GitHub Schedule
Tests actual functionality without making external API calls
"""

import os
import sys


def test_env_loading():
    """Test environment variable loading"""
    print("=" * 50)
    print("TEST 1: Environment Variable Loading")
    print("=" * 50)

    # Load from .env if exists
    env_file = '.env'
    if os.path.exists(env_file):
        print("✓ Found .env file")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    print(f"  Loaded: {key}")
    else:
        print("✗ No .env file found (that's OK if using GitHub Actions)")

    # Check required variables
    print("\nRequired environment variables:")
    webhook_url = os.environ.get('WECOM_WEBHOOK_URL')
    if webhook_url:
        print(f"✓ WECOM_WEBHOOK_URL is set (length: {len(webhook_url)})")
    else:
        print("✗ WECOM_WEBHOOK_URL not set")

    return webhook_url is not None


def test_git_helper():
    """Test git_helper import"""
    print("\n" + "=" * 50)
    print("TEST 2: Git Helper Module")
    print("=" * 50)

    try:
        from script.utils.git_helper import git_add_commit_push
        print("✓ Successfully imported git_add_commit_push")
        print(f"  Function: {git_add_commit_push.__name__}")
        print(f"  Module: {git_add_commit_push.__module__}")
        return True
    except ImportError as e:
        print(f"✗ Failed to import git_helper: {e}")
        return False


def test_script_loading():
    """Test script discovery and job() function"""
    print("\n" + "=" * 50)
    print("TEST 3: Script Loading")
    print("=" * 50)

    script_dir = 'script'
    if not os.path.exists(script_dir):
        print(f"✗ Script directory not found: {script_dir}")
        return False

    python_files = sorted([f for f in os.listdir(script_dir)
                          if f.endswith('.py') and not f.startswith('_')])

    print(f"✓ Found {len(python_files)} scripts:")
    all_valid = True
    for script_file in python_files:
        script_path = os.path.join(script_dir, script_file)
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()

            has_job = 'def job(' in content
            has_git_helper = 'from utils.git_helper import git_add_commit_push' in content

            # Check if it's a standalone script (doesn't need job())
            is_standalone = script_file.startswith('bigmodel') or 'test' in script_file.lower()

            # Only require job() for non-standalone scripts
            if is_standalone:
                status = "⊙"  # Standalone script icon
            elif has_job:
                status = "✓"
            else:
                status = "✗"

            print(f"  {status} {script_file}")
            if has_job:
                print(f"     - has job() function")
            if has_git_helper:
                print(f"     - uses git_helper module")
            if is_standalone:
                print(f"     - standalone utility (not called by main.py)")
            elif not has_job:
                all_valid = False

        except Exception as e:
            print(f"  ✗ {script_file}: error - {e}")
            all_valid = False

    return all_valid


def test_http_config():
    """Test HTTP timeout configuration"""
    print("\n" + "=" * 50)
    print("TEST 4: HTTP Timeout Configuration")
    print("=" * 50)

    scripts_to_check = [
        'script/1.ai-news.py',
        'script/2.wecom-robot.py',
        'script/github-trending.py'
    ]

    all_ok = True
    for script_path in scripts_to_check:
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()

            has_timeout = 'timeout=' in content
            no_assert = 'assert r.status_code' not in content and 'assert response.status_code' not in content
            has_raise = 'raise_for_status()' in content

            status = "✓" if (has_timeout and no_assert) else "✗"
            print(f"{status} {os.path.basename(script_path)}:")
            print(f"     timeout parameter: {'✓' if has_timeout else '✗'}")
            print(f"     no assert usage: {'✓' if no_assert else '✗'}")
            print(f"     raise_for_status: {'✓' if has_raise else '⚠ (optional)'}")

            if not has_timeout or not no_assert:
                all_ok = False

        except Exception as e:
            print(f"✗ {os.path.basename(script_path)}: error - {e}")
            all_ok = False

    return all_ok


def test_ai_news_fetch(dry_run=True):
    """Test AI news fetching (dry run by default)"""
    print("\n" + "=" * 50)
    print("TEST 5: AI News Script (Dry Run)")
    print("=" * 50)

    if dry_run:
        print("Running in dry-run mode (not fetching data)")

        # Just verify the script structure
        script_path = 'script/1.ai-news.py'
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()

            has_timeout = 'timeout=' in content
            has_raise = 'raise_for_status()' in content

            print(f"✓ Script structure check:")
            print(f"  - timeout parameter: {'✓' if has_timeout else '✗'}")
            print(f"  - raise_for_status: {'✓' if has_raise else '✗'}")

            return has_timeout and has_raise

        except Exception as e:
            print(f"✗ Error reading script: {e}")
            return False
    else:
        print("Note: Set dry_run=False to actually fetch data")
        return True


def main():
    """Run all manual tests"""
    print("\n" + "="*50)
    print("GITHUB SCHEDULE - MANUAL TEST")
    print("="*50)
    print(f"Time: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    results = []

    # Run tests
    results.append(("Environment Variables", test_env_loading()))
    results.append(("Git Helper Module", test_git_helper()))
    results.append(("Script Loading", test_script_loading()))
    results.append(("HTTP Configuration", test_http_config()))
    results.append(("AI News Script", test_ai_news_fetch(dry_run=True)))

    # Summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print(f"\nResult: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed! Ready to run.")
    else:
        print("\n⚠ Some tests failed. Please check the output above.")

    print("\nNext steps:")
    print("1. Set WECOM_WEBHOOK_URL environment variable")
    print("2. Run 'python main.py' to execute all scripts")
    print("3. Or run individual scripts from script/ directory")

    return 0 if passed == total else 1


if __name__ == '__main__':
    sys.exit(main())
