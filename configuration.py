# Imports
import numpy as np
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

# Define unit conversion factors for easy scaling of dimensions
class Units(Enum):
    MILLIMETERS = 1.0
    INCHES = 25.4
    METERS = 1000.0
    FEET = 304.8

# Define a mast geometry class to determine the cross section   
class MastGeometry(Enum):
    RECTANGULAR = auto()
    TRIANGULAR = auto()
    SQUARE = auto()

@dataclass
class MemberProfile:
    shape: str      # e.g., 'tube', 'solid_circular_bar', 'rectangular'
    diameter: Optional[float] = None
    wall_thickness: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    # Optional helper method to apply units to this specific profile
    def apply_units(self, unit: Units):
        if self.diameter: self.diameter *= unit.value
        if self.wall_thickness: self.wall_thickness *= unit.value
        if self.width: self.width *= unit.value
        if self.height: self.height *= unit.value

# 1. Define macro geometry
@dataclass
class MacroGeometry:
    length: float
    width: float
    main_chord_profile: MemberProfile # <-- Added the main corner posts
    height: Optional[float] = None    # Default to None for square sections
    taper_angle: float = 0.0          # Default to 0 for straight tower masts
    cross_section_shape: MastGeometry = MastGeometry.SQUARE

# 2. Define the allowed bracing patterns
class BracingStyle(Enum):
    WARREN = auto()
    X_BRACE = auto()
    INVERTED_V = auto()
    DIAGONAL_ONLY = auto()


# 4. Define the main bracing configuration class
@dataclass
class BracingConfig:
    style: BracingStyle
    num_bays: int
    diagonal_profile: MemberProfile
    has_horizontal_struts: bool = False
    horizontal_profile: Optional[MemberProfile] = None
    has_cap_struts: Optional[bool] = False
    cap_strut_profile: Optional[MemberProfile] = None
    eccentricity_offset: float = 0.0

    def calculate_bay_length(self, total_mast_length: float) -> float:
        """Helper method to determine the base width of a single repeating bay."""
        return total_mast_length*.98 / self.num_bays        #.99*total_mast_length for minor offset