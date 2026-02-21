# Code2Video - AI 教学视频生成系统
# AI-powered Educational Video Generation System

# 导出核心类（延迟导入以避免循环依赖）
__all__ = [
    "TeachingVideoAgent",
    "Section",
    "RunConfig",
    "EnglishTeachingVideoAgent",
    "create_english_grammar_video",
]


def __getattr__(name):
    """延迟导入以避免在导入时加载所有依赖"""
    if name == "TeachingVideoAgent":
        from agent import TeachingVideoAgent
        return TeachingVideoAgent
    elif name == "Section":
        from agent import Section
        return Section
    elif name == "RunConfig":
        from agent import RunConfig
        return RunConfig
    elif name == "EnglishTeachingVideoAgent":
        from english.agent import EnglishTeachingVideoAgent
        return EnglishTeachingVideoAgent
    elif name == "create_english_grammar_video":
        from english.agent import create_english_grammar_video
        return create_english_grammar_video
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
