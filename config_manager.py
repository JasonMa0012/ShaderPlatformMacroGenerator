from dataclasses import is_dataclass, asdict
from PyQt5.QtWidgets import QMessageBox
from models import Config, Platform, Quality, Feature, FeatureGroup
import json
import os

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if is_dataclass(obj):
            return asdict(obj)
        return super().default(obj)

class ConfigManager:
    DEFAULT_CONFIG_PATH = 'Config/config.json'
    current_config_path = DEFAULT_CONFIG_PATH

    @staticmethod
    def load_config(path: str = DEFAULT_CONFIG_PATH) -> Config:
        config = Config()
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                config.output_path = data.get('output_path', config.output_path)
                config.force_overwrite = data.get('force_overwrite', config.force_overwrite)
                config.prefix = data.get('prefix', config.prefix)
                config.postfix = data.get('postfix', config.postfix)
                config.file_include_macro = data.get('file_include_macro', config.file_include_macro)
                config.row_height = data.get('row_height', config.row_height)
                config.row_header_width = data.get('row_header_width', config.row_header_width)
                config.column_width = data.get('column_width', config.column_width)
                config.column_header_height = data.get('column_header_height', config.column_header_height)
                config.font_size = data.get('font_size', config.font_size)
                config.platforms = [Platform(**p) for p in data['platforms']]
                config.qualities = [Quality(**q) for q in data['qualities']]
                config.feature_groups = [FeatureGroup(
                    name=g['name'],
                    features=[Feature(**f) for f in g['features']]
                ) for g in data.get('feature_groups', [])]
                config.settings = data.get('settings', {})
            ConfigManager.current_config_path = path
        except Exception as e:
            import traceback
            print(f"Config file loading failed: {str(e)}\n{traceback.format_exc()}")

        return config

    @staticmethod
    def save_config(config: Config, path: str = ""):
        data = {
            'output_path': config.output_path,
            'force_overwrite': config.force_overwrite,
            'prefix': config.prefix,
            'postfix': config.postfix,
            'file_include_macro': config.file_include_macro,
            'row_height': config.row_height,
            'row_header_width': config.row_header_width,
            'column_width': config.column_width,
            'column_header_height': config.column_header_height,
            'font_size': config.font_size,
            'platforms': [p.__dict__ for p in config.platforms],
            'qualities': [q.__dict__ for q in config.qualities],
            'feature_groups': [g.__dict__ for g in config.feature_groups],
            'settings': config.settings
        }
        target_path = path
        if path == "":
            target_path = ConfigManager.current_config_path

        try:
            # Check if the file is read-only
            if os.path.exists(target_path) and not os.access(target_path, os.W_OK):
                reply = QMessageBox.question(None, 'File Read-Only', f'File({target_path}) is read-only, force overwrite?',
                                           QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.No:
                    return
                # Remove read-only attribute
                os.chmod(target_path, 0o777)

            with open(target_path, 'w') as f:
                json.dump(data, f, indent=4, cls=CustomEncoder)
                print("Save to: " + target_path)

        except PermissionError as e:
            QMessageBox.critical(None, 'Save Failed', f'Write permission denied: {str(e)}')
        except Exception as e:
            QMessageBox.critical(None, 'Save Failed', f'Error saving configuration:\n{str(e)}')

        ConfigManager.current_config_path = target_path
        
    @staticmethod
    def get_column_header_labals(config: Config) -> list:
        pairs = [(p, q) for p in config.platforms for q in config.qualities]
        return [f"{p[0].name} | {p[1].name}" for p in pairs]

    @staticmethod
    def calculate_cell_indices(config: Config, column_index: int) -> tuple:
        platform_idx = column_index // len(config.qualities)
        quality_idx = column_index % len(config.qualities)
        return platform_idx, quality_idx

    @staticmethod
    def get_feature_by_index(config: Config, group_index: int, row_index: int) -> Feature:
        if 0 <= group_index < len(config.feature_groups):
            group = config.feature_groups[group_index]
            if 0 <= row_index < len(group.features):
                return group.features[row_index]
        return Feature('', '')
