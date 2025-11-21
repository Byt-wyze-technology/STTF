"""
SAT Transformation Trace Format (STTF) v1.0
A universal standard for recording SAT CNF transformations.

Modules:
    sttf_core: Core library (expression evaluation, bundle loading, model lifting)
    sttf_replay: Replay engine for transformation reconstruction
    sttf_validate: Validation tools
    sttf_generate: Bundle generation utilities
"""

__version__ = "1.0.0"
__author__ = "STTF Contributors"

from .sttf_core import Expr, STTFBundle
from .sttf_replay import STTFReplayEngine, CNFFormula, replay_bundle

__all__ = [
    'Expr',
    'STTFBundle',
    'STTFReplayEngine',
    'CNFFormula',
    'replay_bundle',
    '__version__'
]

