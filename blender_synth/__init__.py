"""Blender-Synth: Synthetic dataset generator for archaeological artifacts."""

__version__ = "0.1.0"
__all__ = ["SyntheticGenerator", "GenerationConfig"]


def __getattr__(name):
    """Lazy import to avoid loading blenderproc outside of blenderproc run context."""
    if name == "GenerationConfig":
        from blender_synth.pipeline.config import GenerationConfig
        return GenerationConfig
    elif name == "SyntheticGenerator":
        from blender_synth.pipeline.generator import SyntheticGenerator
        return SyntheticGenerator
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
