from typing import Dict
from PyQt5.QtWidgets import (
    QMainWindow, QTableWidget, QTableWidgetItem, QTabWidget,
    QToolBar, QAction, QHeaderView, QCheckBox, QFileDialog, QWidget,
    QHBoxLayout, QVBoxLayout, QApplication
)
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QDesktopServices, QFont
from models import Config, Platform, Quality, Feature
from config_manager import ConfigManager
from hlsl_generator import generate_hlsl
from PyQt5.QtWidgets import QMessageBox
import os, json

class MainWindow(QMainWindow):
    TITLE = 'Shader Platform Macro Generator'
    GITHUB_URL = 'https://github.com/JasonMa0012/ShaderPlatformMacroGenerator'

    def __init__(self, ):
        super().__init__()
        self.config = ConfigManager.load_config()
        self._init_ui()
        self._load_data()
    
    def _init_ui(self):
        QApplication.setFont(QFont('Consolas', self.config.font_size))
        self._setup_title()
        # Delay maximize to prevent flickering
        QTimer.singleShot(100, self.showMaximized)
        # Set main container as tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self._setup_toolbar()

        # Initialize main table container
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        
        # Add default tab page
        main_table = QTableWidget()
        main_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table_layout.addWidget(main_table)
        self.tabs.addTab(table_container, "Default")
        
        # Initialize space shortcut
        self.space_shortcut = QShortcut(Qt.Key_Space, self)
        self.space_shortcut.activated.connect(self._toggle_selected_checkbox)

    def _setup_toolbar(self):
        toolbar = QToolBar()
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        actions = [
            ("New", self._new_config),
            ("Open", self._open_config_file),
            ("Save As", self._save_as_config),
            ("Edit", lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.abspath(ConfigManager.current_config_path)))),
            ("Reload", self._reload_config_file),
            ("Generate", self._generate_shader_marco),
            ("Copy Output Path", self._copy_output_path),
            ("About", lambda: QDesktopServices.openUrl(QUrl(self.GITHUB_URL))),
        ]
        for text, callback in actions:
            action = QAction(text, self)
            action.triggered.connect(callback)
            toolbar.addAction(action)

    def _setup_title(self):
        self.setWindowTitle(self.TITLE + f"  ({ConfigManager.current_config_path}  Target: {self.config.output_path})")

    def _load_data(self):
        self.tabs.clear()
        
        for group in self.config.feature_groups:
            tab_widget = QWidget()
            layout = QVBoxLayout(tab_widget)
            group_table = QTableWidget()
            layout.addWidget(group_table)
            self._create_group_table(group_table, group.features)
            self.tabs.addTab(tab_widget, group.name)

    def _new_config(self):
        path, _ = QFileDialog.getSaveFileName(self, "New Config", "", "JSON Files (*.json)")
        if path:
            try:
                self.config = Config()
                self._load_data()
                ConfigManager.save_config(self.config, path)
                self._setup_title()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save config: {str(e)}")

    def _open_config_file(self):
        ConfigManager.save_config(self.config)
        path, _ = QFileDialog.getOpenFileName(self, "Open Config File", "", "JSON Files (*.json)")
        if path:
            try:
                self.config = ConfigManager.load_config(path)
                self._load_data()
                self._setup_title()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load config: {str(e)}")

    def _reload_config_file(self):
        try:
            self.config = ConfigManager.load_config(ConfigManager.current_config_path)
            self._load_data()
            self._setup_title()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reload config: {str(e)}")

    def _save_as_config(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Config As", "", "JSON Files (*.json)")
        if path:
            try:
                ConfigManager.save_config(self.config, path)
                self._setup_title()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save config: {str(e)}")

    def _toggle_selected_checkbox(self):
        current_table = self.tabs.currentWidget().findChild(QTableWidget)
        if len(current_table.selectedRanges()) == 0:
            return

        if current_table and current_table.hasFocus():
            # Get first selected cell's state as baseline
            first_cell = current_table.cellWidget(
                current_table.selectedRanges()[0].topRow(),
                current_table.selectedRanges()[0].leftColumn()
            )
            base_state = not first_cell.findChild(QCheckBox).isChecked()
            
            for selection_range in current_table.selectedRanges():
                for row in range(selection_range.topRow(), selection_range.bottomRow() + 1):
                    for col in range(selection_range.leftColumn(), selection_range.rightColumn() + 1):
                        widget = current_table.cellWidget(row, col)
                        checkbox = widget.findChild(QCheckBox) if widget else None
                        if checkbox:
                            checkbox.setChecked(base_state)
                            platform_idx, quality_idx = self.config.calculate_cell_indices(col)
                            platform = self.config.platforms[platform_idx]
                            quality = self.config.qualities[quality_idx]
                            feature = self.config.get_feature_by_index(self.tabs.currentIndex(), row)
                            self._set_feature_state(platform, quality, feature, base_state)

    def _set_feature_state(self, platform: Platform, quality: Quality, feature: Feature, value: bool):
        self.config.set_feature_state(platform, quality, feature, value)
        ConfigManager.save_config(self.config)

    def _copy_output_path(self):
        if self.config.output_path:
            QApplication.clipboard().setText(os.path.abspath(self.config.output_path))

    def _generate_shader_marco(self):
        try:
            if not self.config.output_path:
                path, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'HLSL Files (*.hlsl)')
                if not path:
                    return
                path = os.path.relpath(os.path.abspath(path))
                self.config.output_path = path
            
            target_abs_path = os.path.abspath(self.config.output_path)
            dir_name = os.path.dirname(target_abs_path) or os.getcwd()
            os.makedirs(dir_name, exist_ok=True)
            
            if os.path.exists(target_abs_path):
                if not self.config.force_overwrite:
                    reply = QMessageBox.question(self, 'File Exists', 
                        f'Target file({target_abs_path}) already exists, overwrite?',
                        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                    if reply != QMessageBox.Yes:
                        return
                if not os.access(target_abs_path, os.W_OK):
                    os.chmod(target_abs_path, 0o777)

            with open(target_abs_path, 'w') as f:
                f.write(generate_hlsl(self.config))
            QMessageBox.information(self, 'Success', f'File saved to: {target_abs_path}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'File save failed: {str(e)}')

    def _create_group_table(self, table, features):
        if not self.config.platforms or not self.config.qualities:
            table.setRowCount(1)
            table.setColumnCount(1)
            table.setItem(0, 0, QTableWidgetItem("Please configure platforms and quality levels first!"))
            return

        columns = self.config.get_column_header_labels()
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        table.setRowCount(len(features))

        # Populate checkboxes
        for col, _ in enumerate(columns):
            platform_idx, quality_idx = self.config.calculate_cell_indices(col)
            
            # Boundary check
            if platform_idx >= len(self.config.platforms) or quality_idx >= len(self.config.qualities):
                continue

            platform = self.config.platforms[platform_idx]
            quality = self.config.qualities[quality_idx]
            
            for row in range(len(features)):
                feature = features[row]
                checkbox = QCheckBox()
                checkbox.setStyleSheet('QCheckBox::indicator { width: 20px; height: 20px; }')
                checkbox.setChecked(self.config.get_feature_state(platform, quality, feature))
                checkbox.stateChanged.connect(
                    lambda state, p=platform, q=quality, f=feature: 
                    self._set_feature_state(p, q, f, state)
                )
                widget = QWidget()
                layout = QHBoxLayout()
                layout.addWidget(checkbox, alignment=Qt.AlignCenter)
                widget.setLayout(layout)
                table.setCellWidget(row, col, widget)

        # Populate row headers
        for row, feature in enumerate(features):
            table.setVerticalHeaderItem(row, QTableWidgetItem(f'{feature.name}'))
        
        # Set cell dimensions
        table.verticalHeader().setSectionResizeMode(QHeaderView.Interactive)
        table.verticalHeader().setDefaultAlignment(Qt.AlignCenter)
        table.verticalHeader().setDefaultSectionSize(self.config.row_height)
        table.verticalHeader().setMinimumWidth(self.config.row_header_width)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        table.horizontalHeader().setDefaultSectionSize(self.config.column_width)
        table.horizontalHeader().setMinimumHeight(self.config.column_header_height)
