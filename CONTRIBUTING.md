# Contributing to Blender-Synth

Thank you for your interest in contributing to Blender-Synth! This document provides guidelines and information for contributors.

## Development Setup

### 1. Clone and Install
```bash
git clone <repository-url>
cd blender-synth

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
pip install -r requirements-dev.txt
```

### 2. Set up environment variables
```bash
export LD_LIBRARY_PATH=/usr/lib/wsl/lib:/usr/local/cuda/lib64:$LD_LIBRARY_PATH
```

## Project Structure

```
blender-synth/
├── blender_synth/          # Main package - all production code
│   ├── core/               # Scene management, camera, physics
│   ├── objects/            # Model loading and management  
│   ├── pipeline/           # Generation pipeline and config
│   ├── annotation/         # YOLO annotation generation
│   ├── randomization/      # Domain randomization
│   └── utils/              # Utility functions
├── tests/                  # All test files (test_*.py)
├── scripts/                # Utility and debug scripts
│   ├── utils/              # Production utilities
│   └── debug/              # Development/debug scripts
├── examples/               # Example usage scripts
└── configs/                # Configuration templates
```

## Code Organization

### Where to Put New Code

- **Production code**: `blender_synth/` package
  - Core functionality: `blender_synth/core/`
  - New features: Create appropriate subdirectory
  - Utilities: `blender_synth/utils/`

- **Tests**: `tests/` directory
  - Name: `test_<feature>.py`
  - Include docstrings explaining what is tested

- **Utilities**: `scripts/utils/`
  - Production-ready helper scripts
  - Can be run with standard Python

- **Debug scripts**: `scripts/debug/`  
  - Development/debugging only
  - Require BlenderProc to run

- **Examples**: `examples/`
  - User-facing example scripts
  - Well-commented and documented

## Coding Standards

### Python Style
- Follow PEP 8
- Use type hints where appropriate
- Write docstrings for all public functions/classes
- Maximum line length: 100 characters

### Example Function
```python
def generate_annotations(
    seg_data: np.ndarray,
    objects: List[bproc.types.MeshObject]
) -> List[str]:
    """Generate YOLO annotations from segmentation data.
    
    Args:
        seg_data: Segmentation map from renderer
        objects: List of objects to annotate
        
    Returns:
        List of YOLO format annotation strings
    """
    # Implementation
    pass
```

### Git Workflow
1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and commit with clear messages
3. Test your changes thoroughly
4. Submit a pull request with description

### Commit Messages
Format:
```
<type>: <short description>

<optional longer description>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test additions/changes
- `refactor`: Code refactoring
- `style`: Formatting, missing semicolons, etc.
- `chore`: Maintenance tasks

Example:
```
fix: Ensure annotations are generated for all visible objects

Added validation and retry logic to guarantee 100% annotation
success rate. Objects that fall off surface are now detected
and scenes are regenerated automatically.
```

## Testing

### Running Tests
```bash
# Run a specific test
blenderproc run tests/test_generation.py

# Or using helper script
./run_blender_synth.sh tests/test_generation.py
```

### Writing Tests
- Place in `tests/` directory
- Name files `test_<feature>.py`
- Test edge cases and error conditions
- Include docstrings

Example test structure:
```python
"""Tests for annotation generation."""

import blenderproc as bproc
import numpy as np
from blender_synth.annotation.yolo import YOLOAnnotator

def test_annotation_generation():
    """Test that annotations are generated correctly."""
    # Setup
    bproc.init()
    
    # Test
    # ...
    
    # Assert
    assert len(annotations) > 0
```

## Documentation

### Code Documentation
- All public APIs must have docstrings
- Use Google-style docstrings
- Include examples for complex functions

### User Documentation
- Update README.md for user-facing changes
- Update relevant docs in `examples/`
- Add usage examples

## Pull Request Process

1. **Before submitting**:
   - Run tests and ensure they pass
   - Update documentation
   - Check code style
   - Add tests for new features

2. **PR Description**:
   - Describe what changed and why
   - Link to related issues
   - Include screenshots for UI changes
   - List breaking changes

3. **Review process**:
   - Address reviewer feedback
   - Keep commits clean and focused
   - Squash commits if requested

## Common Tasks

### Adding a New Feature
1. Create feature in `blender_synth/`
2. Write tests in `tests/`
3. Add example in `examples/`
4. Update documentation
5. Submit PR

### Fixing a Bug
1. Write a test that reproduces the bug
2. Fix the bug
3. Verify test passes
4. Submit PR with clear description

### Adding Utilities
1. Add to `scripts/utils/` for production utilities
2. Add to `scripts/debug/` for debug scripts
3. Document in `scripts/README.md`
4. Include usage examples

## Questions?

If you have questions:
1. Check existing documentation
2. Look at examples in `examples/`
3. Review similar code in the codebase
4. Open an issue for discussion

Thank you for contributing!
