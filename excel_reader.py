from dataclasses import dataclass, field
from typing import Union
import openpyxl


@dataclass
class PlatformMacro:
    name: str
    condition: str


@dataclass
class QualityMacro:
    name: str
    condition: str


@dataclass
class FeatureRow:
    keyword: str
    values: dict  # {(platform_name, quality_name): str}


@dataclass
class GroupHeader:
    name: str


@dataclass
class ExcelConfig:
    prefix_lines: list = field(default_factory=list)
    file_include_macro: str = ""
    platforms: list = field(default_factory=list)
    qualities: list = field(default_factory=list)
    features: list = field(default_factory=list)


def _parse_grouped_rows(ws, start_row: int = 1) -> list:
    """
    通用的"A列标记 + B列多行收集"解析器。
    适用于 Platform Macros、Quality Macros、Other Settings 页面。

    规则：扫描 A 列，遇到非空 -> 新分组开始；
    从同行 B 列向下收集连续非空值，直到下一个 A 列非空或表末尾。

    返回: [(group_name, [line1, line2, ...]), ...]
    """
    results = []
    current_name = None
    current_lines = []
    for row in range(start_row, ws.max_row + 1):
        a_val = ws.cell(row, 1).value
        b_val = ws.cell(row, 2).value
        if a_val is not None:
            if current_name is not None:
                results.append((current_name, current_lines))
            current_name = str(a_val).strip()
            current_lines = []
        if b_val is not None and current_name is not None:
            current_lines.append(str(b_val).strip())
    if current_name is not None:
        results.append((current_name, current_lines))
    return results


def _build_column_map(ws, quality_names: list) -> dict:
    """
    扫描 Feature Switch 页的 Row1 + Row2，
    返回 {col_index: (platform_name, quality_name)}。

    平台名在 Row1 从 C 列起标记（合并单元格只有首列有值），
    后续空列继承上一个平台名。

    画质映射策略：每个平台组内，按位置对应 quality_names 列表顺序。
    这样即使 Row2 有拼写差异（如 "Hight" vs "High"），仍能正确匹配。
    """
    current_platform = None
    platform_groups = []
    current_cols = []

    for col in range(3, ws.max_column + 1):
        val = ws.cell(1, col).value
        if val:
            if current_platform is not None:
                platform_groups.append((current_platform, current_cols))
            current_platform = str(val).strip()
            current_cols = []
        if current_platform and ws.cell(2, col).value is not None:
            current_cols.append(col)

    if current_platform is not None:
        platform_groups.append((current_platform, current_cols))

    column_map = {}
    for platform_name, cols in platform_groups:
        for i, col in enumerate(cols):
            if i < len(quality_names):
                column_map[col] = (platform_name, quality_names[i])
    return column_map


def _parse_feature_switch(ws, column_map: dict) -> list:
    """
    解析 Feature Switch 页的数据行 (Row 3+)。
    - 整行为空 -> 跳过
    - 仅 A 列有值、B 列为空 -> GroupHeader
    - A + B 列都有值 -> FeatureRow
    """
    features = []
    for row in range(3, ws.max_row + 1):
        a_val = ws.cell(row, 1).value
        b_val = ws.cell(row, 2).value

        if a_val is None and b_val is None:
            continue

        if a_val is not None and b_val is None:
            features.append(GroupHeader(name=str(a_val).strip()))
        elif b_val is not None:
            keyword = str(b_val).strip()
            values = {}
            for col, (platform, quality) in column_map.items():
                cell_val = ws.cell(row, col).value
                if cell_val is not None:
                    val_str = str(cell_val)
                    if val_str.endswith('.0') and val_str[:-2].isdigit():
                        val_str = val_str[:-2]
                    values[(platform, quality)] = val_str
                else:
                    values[(platform, quality)] = ""
            features.append(FeatureRow(keyword=keyword, values=values))
    return features


def read_excel(path: str) -> ExcelConfig:
    """读取 Excel 配置文件，返回 ExcelConfig 数据结构。"""
    wb = openpyxl.load_workbook(path, data_only=True)

    platforms = []
    if "Platform Macros" in wb.sheetnames:
        for name, lines in _parse_grouped_rows(wb["Platform Macros"]):
            if name.lower() == "platform":
                continue
            platforms.append(PlatformMacro(name=name, condition=" ".join(lines)))

    qualities = []
    if "Quality Macros" in wb.sheetnames:
        for name, lines in _parse_grouped_rows(wb["Quality Macros"]):
            if name.lower() == "quality":
                continue
            qualities.append(QualityMacro(name=name, condition=" ".join(lines)))

    prefix_lines = []
    file_include_macro = ""
    if "Other Settings" in wb.sheetnames:
        settings_dict = {}
        for key, lines in _parse_grouped_rows(wb["Other Settings"]):
            settings_dict[key] = lines
        prefix_lines = settings_dict.get("Prefix", [])
        macro_lines = settings_dict.get("File Include Macro", [])
        file_include_macro = macro_lines[0] if macro_lines else ""

    features = []
    if "Feature Switch" in wb.sheetnames:
        ws = wb["Feature Switch"]
        quality_names = [q.name for q in qualities]
        column_map = _build_column_map(ws, quality_names)
        features = _parse_feature_switch(ws, column_map)

    wb.close()
    return ExcelConfig(
        prefix_lines=prefix_lines,
        file_include_macro=file_include_macro,
        platforms=platforms,
        qualities=qualities,
        features=features,
    )
