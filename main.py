print("--- THE SCRIPT IS ALIVE ---")

import cadquery as cq
print("Imported cadquery...")

from cadquery.vis import show
print("Imported viewer...")

from configuration import MastGeometry, MemberProfile, MacroGeometry, LacingConfig, LacingStyle, Units
print("Imported configuration...")

from assembly import assemble_mast_section, create_truss_base, stack_assembly_sections

print("Imported base_assembly...")

print("1. Starting script...")
    

# dims are in mm, length is in mm for consistency with the configuration file

# define cross-section of chord (truss corner, main structural beams), hollow tube profile
#corner_profile = MemberProfile(shape='hollow_rectangle', width=10*25.4, height=10*25.4, wall_thickness=0.625*25.4)
corner_profile = MemberProfile(shape='hollow_tube', diameter=10*25.4, wall_thickness=0.625*25.4)

# define truss geometry, triangular cross-section with specified dimensions
macro_geometry = MacroGeometry(length=489.0*25.4, width=96.0*25.4, height=96.0*25.4, main_chord_profile=corner_profile, cross_section_shape=MastGeometry.RECTANGULAR)
print("Defined macro geometry and corner profile...")

#primary bracing definition, inverted v pattern, horizontal webbing profile solid rectangle, diagonal webbing profile solid rectangle
primary_bracing = BracingConfig(style=BracingStyle.INVERTED_V, num_bays=8, diagonal_profile=MemberProfile(shape='hollow_rectangle', width=5*25.4, height=5*25.4, wall_thickness=0.500*25.4), has_horizontal_struts=True, horizontal_profile=MemberProfile(shape='hollow_rectangle', width=5*25.4, height=5*25.4, wall_thickness=0.500*25.4), has_cap_struts=True, cap_strut_profile=MemberProfile(shape='hollow_rectangle', width=5*25.4, height=5*25.4, wall_thickness=0.500*25.4))
print("Defined primary bracing pattern...")

#secondary bracing definition, x brace pattern, webbing profile solid rectangle
secondary_bracing = BracingConfig(style=BracingStyle.WARREN, num_bays=8, diagonal_profile=MemberProfile(shape='hollow_rectangle', width=5*25.4, height=5*25.4, wall_thickness=0.500*25.4), has_cap_struts=True, cap_strut_profile=MemberProfile(shape='hollow_rectangle', width=5*25.4, height=5*25.4, wall_thickness=0.500*25.4))

#create truss section by adding in corner posts
mast_base = assemble_mast_section(macro_geometry, corner_profile, primary_bracing, secondary_bracing)
show(mast_base, alpha = 0.5, fxaa=False)

#two_masts = stack_assembly_sections([mast_base, mast_base]) # Stack two sections for a taller mast
#show(two_masts_u, alpha = 0.5, fxaa=False)
cq.exporters.export(mast_base, 'mast_base.step')
print("Exported mast_base.step successfully.")
