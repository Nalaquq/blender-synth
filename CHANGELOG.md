# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Memory Monitoring System** - Comprehensive memory tracking to prevent OOM crashes
  - Real-time memory usage logging every 10-50 images
  - CSV export of memory metrics (`memory_usage.csv`)
  - Peak memory tracking and reporting
  - Blender data block counts (meshes, materials, textures, images)
  - Enhanced generation summaries with memory statistics
  - Documentation in `docs/MEMORY_MONITORING.md`

### Fixed
- **Critical: Memory Leak** - Fixed OOM crashes during large dataset generation (10,000+ images)
  - Added proper cleanup of Blender data blocks (meshes, materials, textures, images, node groups)
  - Implemented `_cleanup_blender_data()` method in scene manager
  - Memory now stabilizes after initial ramp-up instead of growing unbounded
  - Generation can now complete 10,000+ images without crashes on systems with 16GB RAM

### Improved
- **Documentation Organization** - Restructured and enhanced documentation
  - Moved `MEMORY_MONITORING.md` to `docs/` directory
  - Updated main `README.md` with troubleshooting section
  - Enhanced `docs/index.md` with better navigation and common tasks
  - Added detailed system requirements (minimum vs recommended)
  - Cross-referenced all documentation files

- **Logging Enhancements** - More informative and useful logs
  - Memory logs now include peak usage in addition to current usage
  - More frequent logging in first 100 images (every 10 images) to catch early issues
  - Memory metrics include both MB and GB for easier reading
  - Final summary includes peak memory usage statistics

### Changed
- Memory logging frequency: Every 10 images (first 100), then every 50 images
- Generation summary JSON now includes `peak_memory_mb` and `peak_memory_gb` fields
- Preview summary JSON now includes memory statistics

## Previous Releases

See git history for changes prior to this changelog.

---

## Legend

- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Soon-to-be removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security vulnerability fixes
- **Improved** - Enhancements to existing features
