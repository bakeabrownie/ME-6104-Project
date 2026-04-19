print("--- THE SCRIPT IS ALIVE ---")

import cadquery as cq
print("Imported cadquery...")

from configuration import MastGeometry, MemberProfile, MacroGeometry, LacingConfig, LacingStyle, Units
print("Imported configuration...")

from base_assembly import assemble_mast_section, create_truss_base, stack_assembly_sections

print("Imported base_assembly...")

print("1. Starting script...")
    

# dims are in mm, length is in mm for consistency with the configuration file
corner_profile = MemberProfile(shape='hollow_tube', diameter=50.0, wall_thickness=5.0)

macro_geometry = MacroGeometry(length=5000.0, width=1000.0, height=1000.0, main_chord_profile=corner_profile, cross_section_shape=MastGeometry.TRIANGULAR)
print("Defined macro geometry and corner profile...")
primary_lacing = LacingConfig(style=LacingStyle.INVERTED_V, num_bays=5, diagonal_profile=MemberProfile(shape='solid_rectangle', width=30.0, height=10.0), has_horizontal_struts=True, horizontal_profile=MemberProfile(shape='solid_rectangle', width=20.0, height=10.0))
secondary_lacing = LacingConfig(style=LacingStyle.X_BRACE, num_bays=5, diagonal_profile=MemberProfile(shape='solid_rectangle', width=20.0, height=10.0))
mast_base = assemble_mast_section(macro_geometry, corner_profile, primary_lacing, secondary_lacing)
two_masts = stack_assembly_sections([mast_base, mast_base]) # Stack two sections for a taller mast
print("Assembled mast section successfully.")
cq.exporters.export(two_masts, 'two_masts.step')
print("Exported two_masts.step successfully.")
