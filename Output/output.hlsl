// Generated by Shader Platform Macro Generator (https://github.com/JasonMa0012/ShaderPlatformMacroGenerator)
// Unity Builtin Macros: https://docs.unity3d.com/2022.3/Documentation/Manual/SL-BuiltinMacros.html
// Unreal Builtin Macros: https://github.com/EpicGames/UnrealEngine/blob/5.5/Engine/Shaders/Public/Platform.ush

#ifndef PLATFORM_FEATURE_MACRO_INCLUDE
    #define PLATFORM_FEATURE_MACRO_INCLUDE

    #if defined(PLATFORM_PC) || defined(SHADER_API_DX11)
        #if QUALITY_HIGH || QUALITY_ULTRA
            #define PLATFORM_ENABLE_TESSELLATION 1
            #define PLATFORM_ENABLE_GEOMETRY_SHADER 1
            
            #define PLATFORM_ENABLE_RAY_MARCHING 1
            
            #if defined(PLATFORM_ENABLE_SUBSURFACE)
                #undef PLATFORM_ENABLE_SUBSURFACE
                #define PLATFORM_ENABLE_SUBSURFACE 1
            #endif
        #elif QUALITY_LOW
            #define PLATFORM_ENABLE_TESSELLATION 0
            #define PLATFORM_ENABLE_GEOMETRY_SHADER 0
            
            #define PLATFORM_ENABLE_RAY_MARCHING 0
            
            #if defined(PLATFORM_ENABLE_SUBSURFACE)
                #undef PLATFORM_ENABLE_SUBSURFACE
                #define PLATFORM_ENABLE_SUBSURFACE 0
            #endif
        #endif
    #elif defined(PLATFORM_IOS)
        #if QUALITY_HIGH || QUALITY_ULTRA
            #define PLATFORM_ENABLE_TESSELLATION 1
            #define PLATFORM_ENABLE_GEOMETRY_SHADER 1
            
            #define PLATFORM_ENABLE_RAY_MARCHING 1
            
            #if defined(PLATFORM_ENABLE_SUBSURFACE)
                #undef PLATFORM_ENABLE_SUBSURFACE
                #define PLATFORM_ENABLE_SUBSURFACE 1
            #endif
        #elif QUALITY_LOW
            #define PLATFORM_ENABLE_TESSELLATION 0
            #define PLATFORM_ENABLE_GEOMETRY_SHADER 0
            
            #define PLATFORM_ENABLE_RAY_MARCHING 0
            
            #if defined(PLATFORM_ENABLE_SUBSURFACE)
                #undef PLATFORM_ENABLE_SUBSURFACE
                #define PLATFORM_ENABLE_SUBSURFACE 0
            #endif
        #endif
    #endif

#endif // PLATFORM_FEATURE_MACRO_INCLUDE