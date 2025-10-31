# Blender-Synth Documentation

Welcome to the blender-synth documentation! This directory contains comprehensive guides for installing, configuring, and using the blender-synth synthetic data generation tool.

## 🚀 Getting Started

Start here if you're new to blender-synth:

1. **[Installation Guide](INSTALLATION.md)** - Step-by-step installation instructions with system requirements
2. **[GPU Setup](GPU_SETUP.md)** - Configure GPU acceleration for 10-20x faster rendering (highly recommended)
3. **[Quick Start](QUICKSTART.md)** - Get up and running in 5 minutes

## 📖 Usage Guides

Learn how to use blender-synth effectively:

### Core Usage
- **[Usage Guide](USAGE.md)** - Comprehensive usage documentation with all configuration options
- **[Configuration Examples](../configs/)** - Pre-built YAML configuration templates

### Monitoring & Debugging
- **[Memory Monitoring](MEMORY_MONITORING.md)** - Track memory usage, prevent OOM crashes, analyze resource consumption
- **[Logging System](LOGGING.md)** - Understanding logs, debugging issues, and monitoring generation progress

### Code Examples
- **[Python Examples](../examples/README.md)** - Example scripts for different use cases
- **[Utility Scripts](../scripts/README.md)** - Visualization and validation tools

## 🔧 Project Information

Technical documentation and architecture:

- **[Navigation Guide](NAVIGATION.md)** - Visual documentation map and quick links
- **[Project Structure](PROJECT_STRUCTURE.md)** - Directory organization and file layout
- **[Project Summary](PROJECT_SUMMARY.md)** - Architecture overview and technical details
- **[Cleanup Summary](CLEANUP_SUMMARY.md)** - Recent codebase improvements and refactoring
- **[Changelog](../CHANGELOG.md)** - Recent updates and bug fixes

## 📚 Additional Resources

- **[Main README](../README.md)** - Project overview and introduction
- **[Contributing Guidelines](../CONTRIBUTING.md)** - How to contribute to the project
- **[License](../LICENSE)** - Project license information

## Documentation Organization

This documentation is organized to support different user needs:

### For New Users
1. Read the [Quick Start](QUICKSTART.md) guide (5 minutes)
2. Follow the [Installation Guide](INSTALLATION.md)
3. Set up [GPU acceleration](GPU_SETUP.md) (highly recommended for 10-20x speedup)
4. Try the [example scripts](../examples/README.md)

### For Regular Users
- Refer to the [Usage Guide](USAGE.md) for detailed command options
- Use [Memory Monitoring](MEMORY_MONITORING.md) to optimize large generation runs
- Check the [Logging System](LOGGING.md) for debugging and monitoring
- Explore [configuration templates](../configs/) for different scenarios

### For Developers
- Review the [Project Summary](PROJECT_SUMMARY.md) for architecture details
- Follow the [Contributing Guidelines](../CONTRIBUTING.md) for development workflow
- Run tests in [tests/](../tests/README.md) to validate changes

## Common Tasks

### Generating Your First Dataset
1. Organize models: `models/class_name/*.glb`
2. Run: `blender-synth generate --models ./models --output ./output --num-images 100`
3. Review output in `output/train/`, `output/val/`, `output/test/`

### Preventing OOM Crashes on Large Runs
1. Read [Memory Monitoring](MEMORY_MONITORING.md) guide
2. Monitor memory usage in logs: `output/logs/generation_*/memory_usage.csv`
3. Adjust config if memory grows: reduce `max_per_scene` or `rendering.samples`

### Speeding Up Rendering
1. Follow [GPU Setup](GPU_SETUP.md) guide to enable CUDA/OptiX
2. Use `configs/fast_preview.yaml` for quick tests
3. Reduce samples for faster generation: `rendering.samples: 64`

### Debugging Generation Issues
1. Check logs: `output/logs/generation_*/generation.log`
2. Review [Logging System](LOGGING.md) for log interpretation
3. Use debug scripts in [scripts/debug/](../scripts/README.md)
4. Visualize annotations: `python scripts/utils/visualize_annotations.py`

## Support

If you encounter issues:

1. **Check Documentation**:
   - [Troubleshooting section](../README.md#troubleshooting) in main README
   - [Memory Monitoring](MEMORY_MONITORING.md) for OOM issues
   - [Logging System](LOGGING.md) for debugging tips
   - [GPU Setup](GPU_SETUP.md) for rendering issues

2. **Review Logs**:
   - Check `output/logs/generation_*/generation.log`
   - Review `output/logs/generation_*/memory_usage.csv` for memory trends

3. **Open an Issue**:
   - Provide log files and configuration
   - Include system information (RAM, GPU, OS)
   - Describe expected vs actual behavior

## Recent Updates

See [CHANGELOG](../CHANGELOG.md) for recent improvements and bug fixes.

---

**Note:** This is a living documentation set that is continuously updated. If you notice any errors or areas for improvement, please submit a pull request or open an issue.
