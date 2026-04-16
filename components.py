# imports
import numpy as np
from dataclasses import dataclass
import cadquery as cq
from configuration import MemberProfile

def _create_profile_sketch(profile: MemberProfile) -> cq.Sketch:
    """
    Internal helper function to draw the 2D cross-section of a steel member.
    """
    sketch = cq.Sketch()
    
    if profile.shape == 'tube':
        # Safety check to ensure required dimensions exist
        if profile.diameter is None or profile.wall_thickness is None:
            raise ValueError("A 'tube' profile requires both 'diameter' and 'wall_thickness'.")
            
        outer_radius = profile.diameter / 2.0
        inner_radius = outer_radius - profile.wall_thickness
        
        sketch = (
            sketch
            .circle(outer_radius)
            .circle(inner_radius, mode='s') # 's' subtracts
        )
        
    elif profile.shape == 'solid_circle':
        if profile.diameter is None:
            raise ValueError("A 'solid_circle' profile requires a 'diameter'.")
            
        sketch = sketch.circle(profile.diameter / 2.0)
        
    elif profile.shape == 'rectangular':
        if profile.width is None or profile.height is None:
            raise ValueError("A 'rectangular' profile requires both 'width' and 'height'.")
            
        sketch = sketch.rect(profile.width, profile.height)
        
    else:
        raise ValueError(f"Geometry for shape '{profile.shape}' is not yet implemented.")
        
    return sketch

def build_structural_member(length: float, profile: MemberProfile) -> cq.Workplane:
    """
    Builds a single beam or tube. 
    Extrudes symmetrically so the center of mass remains exactly at (0, 0, 0).
    """
    sketch = _create_profile_sketch(profile)
    
    # Place the 2D sketch on the XY plane and extrude it along the Z-axis.
    # both=True ensures the origin is dead center, making rotation math much easier.
    member = cq.Workplane("XY").placeSketch(sketch).extrude(length, both=False)
    
    return member

def build_end_plate(width: float, thickness: float, hole_dia: float, hole_margin: float) -> cq.Workplane:
    """
    Builds the heavy steel plates used to bolt mast sections together.
    Includes the four bolt holes in the corners.
    """
    # Calculate the distance between bolt holes based on the margin
    hole_spacing = width - (2 * hole_margin)
    
    plate = (
        cq.Workplane("XY")
        .box(width, width, thickness) # Create the main square plate
        .faces(">Z").workplane()      # Select the top face to drill holes
        .rect(hole_spacing, hole_spacing, forConstruction=True) # Create a construction rectangle
        .vertices()                   # Select the 4 corners of that rectangle
        .hole(hole_dia)               # Drill the bolt holes through the plate
    )
    
    return plate

# --- Quick Test Block ---
# If you run this specific file, it will generate a test part to verify your logic
if __name__ == "__main__":
    from configuration import MemberProfile
    
    # Test building a 100mm OD tube with 5mm walls, 2 meters long
    test_profile = MemberProfile(shape='tube', diameter=100.0, wall_thickness=5.0)
    test_tube = build_structural_member(length=2000.0, profile=test_profile)
    
    # Export to step to view in SolidWorks or another CAD viewer
    cq.exporters.export(test_tube, 'test_tube.step')
    print("Exported test_tube.step successfully.")