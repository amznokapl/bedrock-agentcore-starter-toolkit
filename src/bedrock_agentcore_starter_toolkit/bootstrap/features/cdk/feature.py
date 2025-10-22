from pathlib import Path
import subprocess
from ...features.base_feature import Feature
from ...features.types import BootstrapIACProvider
from ...types import ProjectContext

class CDKFeature(Feature):
    name = BootstrapIACProvider.CDK.value

    def before_apply(self, context: ProjectContext):

        # create output dir
        iac_dir = Path(context.output_dir / "cdk")
        iac_dir.mkdir(exist_ok=False)
        context.iac_dir = iac_dir

        # initiate the cdk project via npx
        subprocess.run(
            ["npx", "--yes", "aws-cdk", "init", "app", "--language", "typescript", "--generate-only"],
            cwd=context.iac_dir,
            check=True,
        )

        # aws-cdk doesn't give the newest aws-cdk, so need to run upgrade with npm
        subprocess.run(
            ["npm", "install", "aws-cdk-lib@latest", "constructs@latest"],
            cwd=context.iac_dir,
            check=True,
        )

    def after_apply(self, context: ProjectContext):
        pass