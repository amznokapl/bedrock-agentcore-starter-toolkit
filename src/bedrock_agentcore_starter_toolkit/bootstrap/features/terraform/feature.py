from ...features.base_feature import Feature
from ...features.types import BootstrapIACProvider
from ...types import ProjectContext

class TerraformFeature(Feature):
    name = BootstrapIACProvider.Terraform.value

    def after_apply(self, context: ProjectContext):
        pass