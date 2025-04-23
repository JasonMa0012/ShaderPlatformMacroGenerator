from typing import List, Dict
from dataclasses import dataclass, field

@dataclass
class Platform:
    name: str
    macros: List[str] = field(default_factory=lambda: [])

@dataclass
class Quality:
    name: str
    macros: List[str] = field(default_factory=lambda: [])

@dataclass
class Feature:
    name: str
    macros: List[str] = field(default_factory=lambda: [])

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

    def get_column_header_labels(self) -> list:
        pairs = [(p, q) for p in self.platforms for q in self.qualities]
        return [f"{p.name} | {q.name}" for p, q in pairs]

    def calculate_cell_indices(self, column_index: int) -> tuple:
        platform_idx = column_index // len(self.qualities)
        quality_idx = column_index % len(self.qualities)
        return platform_idx, quality_idx

    def get_feature_by_index(self, group_index: int, row_index: int) -> Feature:
        if 0 <= group_index < len(self.feature_groups):
            group = self.feature_groups[group_index]
            if 0 <= row_index < len(group.features):
                return group.features[row_index]
        return Feature('', [])

    def get_feature_state(self, platform: Platform, quality: Quality, feature: Feature) -> bool:
        key = f"{ platform.name }|{ quality.name }"
        return bool(self.settings.get(key, {}).get(feature.name, 1))

    def set_feature_state(self, platform: Platform, quality: Quality, feature: Feature, value: bool):
        key = f"{ platform.name }|{ quality.name }"
        if not value:
            self.settings.setdefault(key, {})[ feature.name ] = 0
        else:
            if key in self.settings:
                if feature.name in self.settings[key]:
                    del self.settings[key][feature.name]
                if not self.settings[key]:
                    del self.settings[key]