import cadquery as cq
from configuration import LacingConfig, MacroGeometry, MemberProfile, LacingStyle
import numpy as np
from components import create_profile_sketch


def build_strut(pt1: tuple, pt2: tuple, profile: MemberProfile) -> cq.Workplane:
    """
    Builds a member connecting any two 3D points.
    Locks the roll angle so flat faces remain flush.
    """
    # 1. Convert to CadQuery Vectors
    v1 = cq.Vector(pt1)
    v2 = cq.Vector(pt2)
    
    # 2. Calculate direction and distance
    direction = v2 - v1
    distance = direction.Length
    
    # Safety check so we don't divide by zero
    if distance < 1e-6:
        raise ValueError("Start and end points are identical!")
        
    direction = direction.normalized()
    
    # 3. Calculate the locked X-direction to prevent twisting
    global_up = cq.Vector(0, 0, 1)
    
    # We must handle the edge case where the strut is perfectly vertical 
    # (Because the cross product of two parallel vectors is zero)
    if abs(direction.dot(global_up)) > 0.9999:  # If perfectly vertical
        x_dir = cq.Vector(1, 0, 0)              # Lock X to Global X
    else:
        # Cross product guarantees a strictly horizontal X-axis!
        x_dir = global_up.cross(direction)
        
    # 4. Create the custom plane with the locked xDir
    strut_plane = cq.Plane(origin=(0, 0, 0), xDir=x_dir, normal=direction)
    
    # 5. Build the strut
    sketch = create_profile_sketch(profile)
    
    strut = (
        cq.Workplane(strut_plane)
        .placeSketch(sketch)
        .extrude(distance, combine=True)
    )
    
    # 6. Move the newly created strut from the origin to pt1
    return strut.translate(v1)

def build_2d_flat_panel(lacing: LacingConfig, panel_width: float, panel_height: float) -> cq.Workplane:
    """
    Builds a flat 2D panel where width and height are local to the panel itself.
    """
    half_width = panel_width / 2.0
    lacing_style = lacing.style
    panel = cq.Workplane("XY")
    
    # Calculate vertical spacing
    bay_length = lacing.calculate_bay_length(panel_height)
    
    for i in range(lacing.num_bays):
        y_bottom = i * bay_length + 0.1*bay_length
        y_top = (i + 1) * bay_length + 0.1*bay_length

        
        # Grid coordinates
        bottom_left = (-half_width, y_bottom, 0)
        bottom_right = (half_width, y_bottom, 0)
        top_left = (-half_width, y_top, 0)
        top_right = (half_width, y_top, 0)
        
        # --- Pattern Logic ---
        if lacing_style == LacingStyle.X_BRACE:
            s1 = build_strut(bottom_left, top_right, lacing.diagonal_profile)
            s2 = build_strut(bottom_right, top_left, lacing.diagonal_profile)
            panel = panel.add(s1.union(s2))
            
        elif lacing_style == LacingStyle.WARREN:
            start, end = (bottom_left, top_right) if i % 2 == 0 else (bottom_right, top_left)
            panel = panel.add(build_strut(start, end, lacing.diagonal_profile))
            
        elif lacing_style == LacingStyle.INVERTED_V:
            top_mid = (0, y_top, 0)
            panel = panel.add(build_strut(bottom_left, top_mid, lacing.diagonal_profile))
            panel = panel.add(build_strut(bottom_right, top_mid, lacing.diagonal_profile))
            
        elif lacing_style == LacingStyle.DIAGONAL_ONLY:
            panel = panel.add(build_strut(bottom_left, top_right, lacing.diagonal_profile))

        # Add horizontal struts only if needed and only at the top of the bay 
        # (to avoid overlapping the bottom of the next bay)
        if lacing.has_horizontal_struts and lacing.horizontal_profile:
            panel = panel.add(build_strut(top_left, top_right, lacing.horizontal_profile))

        #Add top and bottom "cap" struts if specified (horizontal strut but only at top/bottom of section)
        if lacing.has_cap_struts and lacing.cap_strut_profile:
            if i == 0:
                panel = panel.add(build_strut(bottom_left, bottom_right, lacing.cap_strut_profile))
            if i == lacing.num_bays - 1:
                if lacing.has_horizontal_struts == False:
                    panel = panel.add(build_strut(top_left, top_right, lacing.cap_strut_profile))

    return panel