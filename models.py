from typing import List, Dict
from dataclasses import dataclass, field

@dataclass
class Platform:
    name: str
    macro: str

@dataclass
class Quality:
    name: str
    macro: str

@dataclass
class Feature:
    name: str
    macro: str

@dataclass
class FeatureGroup:
    name: str
    features: List[Feature]

@dataclass
class Config:
    output_path: str = 'Output/output.hlsl'
    force_overwrite: bool = False
    prefix: str = ""
    postfix: str = ""
    file_include_macro: str = "PLATFORM_FEATURE_MACRO_INCLUDE"
    row_height: int = 40
    row_header_width: int = 250
    column_width: int = 150
    column_header_height: int = 25
    font_size: int = 10

    platforms: List[Platform] = field(default_factory=lambda: [
        Platform("PC", "PLATFORM_PC"),
        Platform("IOS", "PLATFORM_IOS"),
    ])
    qualities: List[Quality] = field(default_factory=lambda: [
        Quality("High", "QUALITY_HIGH"),
        Quality("Low", "QUALITY_LOW"),
    ])
    feature_groups: List[FeatureGroup] = field(default_factory=lambda: [
        FeatureGroup("Default", [
            Feature("Tessellation", "FEATURE_TESSELLATION"),
            Feature("Ray Marching", "FEATURE_RAY_MARCHING")
        ]),
        FeatureGroup("Character", [
            Feature("Subsurface", "FEATURE_SUBSURFACE")
        ])
    ])
    
    settings: Dict[str, Dict[str, int]] = field(default_factory=dict)