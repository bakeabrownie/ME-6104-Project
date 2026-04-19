# Imports
from turtle import width

import numpy as np
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
import cadquery as cq
from configuration import LacingConfig, MacroGeometry, MastGeometry, MemberProfile
from components import build_structural_member
from transforms import build_strut, build_2d_flat_panel



def create_truss_base(base_length: float, member_profile: MemberProfile, macro_geometry: MacroGeometry) -> cq.Workplane:
    # Define coordinates for the 4 corner posts of the truss base
    half_width = macro_geometry.width / 2.0
    half_height = macro_geometry.height / 2.0
    if macro_geometry.cross_section_shape == MastGeometry.RECTANGULAR or macro_geometry.cross_section_shape == MastGeometry.SQUARE:
        corner_coords = [
        (half_width, half_height),   # Top Right
        (-half_width, half_height),  # Top Left
        (-half_width, -half_height), # Bottom Left
        (half_width, -half_height)]  # Bottom Right
        
    elif macro_geometry.cross_section_shape == MastGeometry.TRIANGULAR:
        # For an equilateral triangle, 'width' is the side length.
        s = macro_geometry.width 
        
        # Calculate the distance from centroid to vertex (R) and centroid to flat edge (r)
        R = s / np.sqrt(3)  # Circumradius
        r = s / (2 * np.sqrt(3)) # Apothem
        
        # 3 points: One pointing directly UP (Y-axis), two on the bottom left/right
        corner_coords = [
            (0, R),                 # Top vertex
            (s/2.0, -r),            # Bottom right vertex
            (-s/2.0, -r)            # Bottom left vertex
        ]
    else:
        raise ValueError("Unsupported mast geometry.")
    
    base_assembly = cq.Workplane("XY")
    for coord in corner_coords:
        member = build_structural_member(base_length, member_profile, coord[0], coord[1])
        base_assembly = base_assembly.add(member)
    return base_assembly, corner_coords

def assemble_mast_section(macro_geometry: MacroGeometry, member_profile: MemberProfile, primary_lacing: LacingConfig, secondary_lacing: LacingConfig) -> cq.Workplane:
    length = macro_geometry.length
    width = macro_geometry.width
    depth = macro_geometry.height
    half_width = width / 2.0
    half_depth = depth / 2.0


    assembly, corner_coords = create_truss_base(length, member_profile, macro_geometry) # Your 4 corner posts
    
    if macro_geometry.cross_section_shape == MastGeometry.RECTANGULAR or macro_geometry.cross_section_shape == MastGeometry.SQUARE:
        # 1. Front Face (No Z-rotation needed, just stand it up)
        front_panel = build_2d_flat_panel(primary_lacing, width, length) # Build the 2D panel for the front face)
        front_panel = front_panel.rotate((0,0,0), (1,0,0), 90).translate((0, -half_depth, 0))
        assembly = assembly.add(front_panel)
        
        # 2. Right Face (Rotate 90 degrees around Z)
        right_panel = build_2d_flat_panel(secondary_lacing, depth, length)
        right_panel = right_panel.rotate((0,0,0), (1,0,0), 90) # Stand up
        right_panel = right_panel.rotate((0,0,0), (0,0,1), 90).translate((half_width, 0, 0)) # Rotate to side
        assembly = assembly.add(right_panel)
        
        # ... Repeat for Back (180 deg) and Left (270 deg)
        back_panel = build_2d_flat_panel(primary_lacing, width, length)
        back_panel = back_panel.rotate((0,0,0), (1,0,0), 90) # Stand up
        back_panel = back_panel.rotate((0,0,0), (0,0,1), 180).translate((0, half_depth, 0))
        assembly = assembly.add(back_panel)
        # 4. Left Face (Rotate 270 degrees around Z)
        left_panel = build_2d_flat_panel(secondary_lacing, depth, length)
        left_panel = left_panel.rotate((0,0,0), (1,0,0), 90) # Stand up
        left_panel = left_panel.rotate((0,0,0), (0,0,1), 270).translate((-half_width, 0, 0))
        assembly = assembly.add(left_panel)


    elif macro_geometry.cross_section_shape == MastGeometry.TRIANGULAR:
        # Distance from center to the flat faces
        apothem = width / (2 * np.sqrt(3))
        
        # Build the 2D panel
        panel_geom = build_2d_flat_panel(primary_lacing, width, length)
        
        # Face 1: Stand up, push out along Y
        face1 = panel_geom.rotate((0,0,0), (1,0,0), 90).translate((0, -apothem, 0))
        
        # Face 2: Stand up, push out along Y, THEN orbit 120 degrees around global Z
        face2 = panel_geom.rotate((0,0,0), (1,0,0), 90).translate((0, -apothem, 0)).rotate((0,0,0), (0,0,1), 120)
        
        # Face 3: Stand up, push out along Y, THEN orbit 240 degrees around global Z
        face3 = panel_geom.rotate((0,0,0), (1,0,0), 90).translate((0, -apothem, 0)).rotate((0,0,0), (0,0,1), 240)
        
        assembly = assembly.add(face1).add(face2).add(face3)

    assembly = assembly.union()

    #'cutting' tools to remove web material from chord interior if hollow
    if member_profile.shape == 'hollow_rectangle':

        inner_width = member_profile.width - 2 * member_profile.wall_thickness
        inner_height = member_profile.height - 2 * member_profile.wall_thickness
        inner_radius = member_profile.wall_thickness

        cutter_sketch = (
            cq.Sketch("XY")
            .rect(inner_width, inner_height)
            .vertices()
            .fillet(inner_radius)
        )
        cutter = cq.Workplane("XY")
        for corner in corner_coords:
            inner = (
                cq.Workplane("XY")
                .center(corner[0], corner[1])
                .placeSketch(cutter_sketch)
                .extrude(macro_geometry.length)
            )
            cutter = cutter.add(inner)

        assembly = assembly.cut(cutter)


    if member_profile.shape == 'hollow_tube':

        outer_radius = member_profile.diameter / 2.0
        inner_radius = outer_radius - member_profile.wall_thickness

        cutter_sketch = (
            cq.Sketch()
            .circle(inner_radius)
        )
        cutter = cq.Workplane("XY")
        for corner in corner_coords:
            inner = (
                cq.Workplane("XY")
                .center(corner[0], corner[1])
                .placeSketch(cutter_sketch)
                .extrude(macro_geometry.length)
            )
            cutter = cutter.add(inner)

        assembly = assembly.cut(cutter)

    


    return assembly

def stack_assembly_sections(sections: list[cq.Workplane]) -> cq.Workplane:
    """
    Takes a list of assembly sections and stacks them vertically with the specified spacing.
    """
    stacked = cq.Workplane("XY")
    current_height = 0.0
    for section in sections:
        section_height = section.val().BoundingBox().zlen
        stacked = stacked.add(section.translate((0, 0, current_height)))
        current_height += section_height
    return stacked


    