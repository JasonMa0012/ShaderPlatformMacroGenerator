from models import Config, FeatureGroup
from config_manager import ConfigManager

def generate_hlsl(config: Config) -> str:
    output = [config.prefix + "\n"] if config.prefix else []
    output.append("// Generated by Shader Platform Macro Generator (https://github.com/JasonMa0012/ShaderPlatformMacroGenerator)\n")
    
    # Platform condition checks
    for i, platform in enumerate(config.platforms):
        condition = "#if" if i == 0 else "#elif"
        output.append(f"{condition} defined({platform.macro})")
        
        # Quality level condition chain
        for i_quality, quality in enumerate(config.qualities):
            q_condition = "#if" if i_quality == 0 else "#elif"
            output.append(f"    {q_condition} defined({quality.macro})")
            
            # Feature macros (遍历所有功能组)
            key = f"{platform.macro}|{quality.macro}"
            for group in config.feature_groups:
                for feature in group.features:
                    value = config.settings.get(key, {}).get(feature.macro, 1)
                    output.append(f"        #define {feature.macro} {value}")
        
            output.append("    #endif")
    
    output.append("#endif\n")
    
    return '\n'.join(output) + ("\n" + config.postfix if config.postfix else "")