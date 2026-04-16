
from components import build_structural_member
import cadquery as cq
from configuration import MemberProfile
    
# # Test building a 100mm OD tube with 5mm walls, 2 meters long
# test_profile = MemberProfile(shape='tube', dim_1=100.0, dim_2=5.0)
# test_tube = build_structural_member(length=2000.0, profile=test_profile)
    
# # Export to step to view in SolidWorks or another CAD viewer
# cq.exporters.export(test_tube, 'test_tube.step')
# print("Exported test_tube.step successfully.")

# dims are in mm, length is in mm for consistency with the configuration file
test_profile_rect = MemberProfile(shape='rectangular', dim_1=50.0, dim_2=20.0)
test_rect = build_structural_member(length=2000.0, profile=test_profile_rect)
cq.exporters.export(test_rect, 'test_rect.step')
print("Exported test_rect.step successfully.")