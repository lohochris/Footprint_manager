from backend.apps.common.pipeline.core import PipelineContext, PipelineStage

class AIPromptAssemblyStage(PipelineStage):
    def execute(self, ctx: PipelineContext) -> PipelineContext:
        return ctx

class AIProviderExecutionStage(PipelineStage):
    def execute(self, ctx: PipelineContext) -> PipelineContext:
        return ctx

class AIValidationStage(PipelineStage):
    def execute(self, ctx: PipelineContext) -> PipelineContext:
        return ctx

class AIPersistenceStage(PipelineStage):
    def execute(self, ctx: PipelineContext) -> PipelineContext:
        return ctx
