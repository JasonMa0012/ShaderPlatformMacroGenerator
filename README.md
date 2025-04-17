# Shader Platform Macro Generator

轻松编辑并控制每个平台每个质量的每个功能的开关, 然后自动生成宏定义, 以减少Shader变体数量.
易于自定义, 适用于多种Shader语言/游戏引擎.

Easily edit and control the switch for each feature at every quality level on each platform, then automatically generate macro definitions to reduce the number of Shader Variants.
Easy to customize, suitable for various Shader Languages/Game Engines.

## Usage

1. Run `ShaderPlatformMacroGenerator.exe`
2. Click `Edit` to open the config file and add the keywords you need.
3. Click `Reload` to update the config.
4. Enable/disable each feature based on each platform.
5. Click `Generate` to save as a file.

## Build

1. Run `_install_deps.bat`
   > - Python==3.12.1
   > - PyQt5==5.15.11
   > - pyinstaller==6.13.0
   >
2. Run `_build.bat`
