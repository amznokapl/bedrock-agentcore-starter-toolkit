from ...types import ProjectContext
from ..types import BootstrapSDKProvider
from ..base_feature import SDKFeature

class StrandsFeature(SDKFeature):
    name = BootstrapSDKProvider.Strands.value
    python_dependencies = ["strands-agents >= 1.13.0"]

    def after_apply(self, context: ProjectContext):
        pass