# Imports
import numpy as np
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

# 1. Define macro geometry
@dataclass
class MacroGeometry:
    length: float
    width: float
    height: float
    taper_angle: float
    cross_section_shape: str

# 2. Define the allowed lacing patterns
class LacingStyle(Enum):
    WARREN = auto()
    X_BRACE = auto()
    INVERTED_V = auto()
    DIAGONAL_ONLY = auto()

# 3. Define a reusable cross-section profile
@dataclass
class MemberProfile:
    shape: str      # e.g., 'tube', 'solid_bar', 'angle'
    dim_1: float    # e.g., Outer Diameter (mm)
    dim_2: float    # e.g., Wall Thickness (mm)

# 4. Define the main lacing configuration
@dataclass
class LacingConfig:
    style: LacingStyle
    num_bays: int
    diagonal_profile: MemberProfile
    has_horizontal_struts: bool = False
    horizontal_profile: Optional[MemberProfile] = None
    eccentricity_offset: float = 0.0

    def calculate_bay_length(self, total_mast_length: float) -> float:
        """Helper method to determine the base width of a single repeating bay."""
        return total_mast_length / self.num_bays