#!/usr/bin/env python3
"""Test script to verify logging functionality."""

import sys
from pathlib import Path
from datetime import datetime

# Add the package to Python path
sys.path.insert(0, str(Path(__file__).parent))

from blender_synth.utils.logger import setup_logger, create_log_directory, setup_run_logger


def test_basic_logging():
    """Test basic console logging."""
    print("\n=== Test 1: Basic Console Logging ===")
    logger = setup_logger()
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    print("✓ Basic console logging works\n")


def test_file_logging():
    """Test file logging."""
    print("=== Test 2: File Logging ===")

    # Create a test log directory
    test_dir = Path("./test_logs")
    log_file = test_dir / "test.log"

    # Create logger with file handler
    logger = setup_logger(log_file=log_file)

    logger.info("This message should appear in both console and file")
    logger.warning("Testing file logging functionality")
    logger.error("This is a test error message")

    # Verify file was created
    if log_file.exists():
        print(f"✓ Log file created: {log_file}")
        with open(log_file, 'r') as f:
            content = f.read()
            print(f"✓ Log file contains {len(content)} characters")
            print("\nLog file content:")
            print("-" * 60)
            print(content)
            print("-" * 60)
    else:
        print(f"✗ Log file not found: {log_file}")

    print()


def test_log_directory_creation():
    """Test log directory creation."""
    print("=== Test 3: Log Directory Creation ===")

    base_dir = Path("./test_output")

    # Test generation log directory
    gen_log_dir = create_log_directory(base_dir, run_type="generation")
    print(f"✓ Created generation log directory: {gen_log_dir}")

    # Test preview log directory
    preview_log_dir = create_log_directory(base_dir, run_type="preview")
    print(f"✓ Created preview log directory: {preview_log_dir}")

    # Test with custom timestamp
    custom_timestamp = "20250101_120000"
    custom_log_dir = create_log_directory(base_dir, run_type="test", timestamp=custom_timestamp)
    print(f"✓ Created custom log directory: {custom_log_dir}")

    print()


def test_run_logger():
    """Test run logger setup."""
    print("=== Test 4: Run Logger Setup ===")

    base_dir = Path("./test_output")
    log_dir = create_log_directory(base_dir, run_type="test_run")

    # Set up run logger
    logger = setup_run_logger(log_dir, run_type="test_run")

    logger.info("Starting test run")
    logger.info("Processing item 1")
    logger.info("Processing item 2")
    logger.warning("Encountered minor issue")
    logger.info("Test run complete")

    log_file = log_dir / "test_run.log"
    if log_file.exists():
        print(f"✓ Run log file created: {log_file}")
        with open(log_file, 'r') as f:
            lines = f.readlines()
            print(f"✓ Log file contains {len(lines)} lines")
    else:
        print(f"✗ Run log file not found: {log_file}")

    print()


def test_metadata_logging():
    """Test metadata logging (simulated)."""
    print("=== Test 5: Metadata Logging ===")

    import json

    base_dir = Path("./test_output")
    log_dir = create_log_directory(base_dir, run_type="metadata_test")

    # Create sample metadata
    metadata = {
        "command": "test",
        "timestamp": datetime.now().isoformat(),
        "test_parameter_1": "value1",
        "test_parameter_2": 42,
        "test_parameter_3": [1, 2, 3],
    }

    metadata_path = log_dir / "test_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"✓ Created metadata file: {metadata_path}")

    # Read and verify
    with open(metadata_path, 'r') as f:
        loaded_metadata = json.load(f)
        print(f"✓ Metadata loaded successfully")
        print("\nMetadata content:")
        print("-" * 60)
        print(json.dumps(loaded_metadata, indent=2))
        print("-" * 60)

    print()


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("BLENDER-SYNTH LOGGING TEST SUITE")
    print("=" * 60)

    try:
        test_basic_logging()
        test_file_logging()
        test_log_directory_creation()
        test_run_logger()
        test_metadata_logging()

        print("=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print("\nGenerated test directories:")
        print("  - ./test_logs/")
        print("  - ./test_output/logs/")
        print("\nYou can examine these directories to verify logging output.")
        print()

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
