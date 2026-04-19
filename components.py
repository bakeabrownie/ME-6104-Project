# imports
import numpy as np
from dataclasses import dataclass
import cadquery as cq
from configuration import MemberProfile

def create_profile_sketch(profile: MemberProfile) -> cq.Sketch:
    """
    Internal helper function to draw the 2D cross-section of a steel member.
    """
    sketch = cq.Sketch()
    
    if profile.shape == 'hollow_tube':
        # Safety check to ensure required dimensions exist
        if profile.diameter is None or profile.wall_thickness is None:
            raise ValueError("A 'hollow_tube' profile requires both 'diameter' and 'wall_thickness'.")
            
        outer_radius = profile.diameter / 2.0
        inner_radius = outer_radius - profile.wall_thickness
        
        sketch = (
            sketch
            .circle(outer_radius)
            .circle(inner_radius, mode='s') # 's' subtracts
        )
        
    elif profile.shape == 'solid_tube':
        if profile.diameter is None:
            raise ValueError("A 'solid_tube' profile requires a 'diameter'.")
            
        sketch = sketch.circle(profile.diameter / 2.0)
        
    elif profile.shape == 'solid_rectangle':
        if profile.width is None or profile.height is None:
            raise ValueError("A 'solid_rectangle' profile requires both 'width' and 'height'.")
            
        sketch = sketch.rect(profile.width, profile.height)

    elif profile.shape == "hollow_rectangle":
        if profile.width is None or profile.height is None or profile.wall_thickness is None:
            raise ValueError("A 'hollow_rectangle' profile requires 'width', 'height', and 'wall_thickness'.")
        
        outer_width = profile.width
        outer_height = profile.height
        inner_width = outer_width - 2 * profile.wall_thickness
        inner_height = outer_height - 2 * profile.wall_thickness
        outer_radius = 2*profile.wall_thickness
        inner_radius = profile.wall_thickness
        
        outie = (
            cq.Sketch("XY")
            .rect(outer_width, outer_height)
            .vertices()
            .fillet(outer_radius)
        )

        innie = (
            cq.Sketch("XY")
            .rect(inner_width, inner_height)
            .vertices()
            .fillet(inner_radius)
        )

        sketch = (
            cq.Sketch()
            .face(outie)
            .face(innie, mode='s')
        )
        
    else:
        raise ValueError(f"Geometry for shape '{profile.shape}' is not yet implemented.")
        
    return sketch

def build_structural_member(length: float, profile: MemberProfile, x_offset: float = 0.0, y_offset: float = 0.0) -> cq.Workplane:
    """
    Builds a single beam or tube. 
    Can be placed anywhere on the XY plane using x_offset and y_offset.
    """
    sketch = create_profile_sketch(profile)
    
    # 1. Select the XY plane
    # 2. Move the center to the specified (x, y) coordinates
    # 3. Place the 2D sketch there
    # 4. Extrude it upwards along the Z-axis
    member = (
        cq.Workplane("XY")
        .center(x_offset, y_offset)
        .placeSketch(sketch)
        .extrude(length, both=False)
    )
    
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