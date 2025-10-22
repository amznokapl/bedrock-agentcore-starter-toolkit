from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from .features.types import BootstrapFeature
from .features.base_feature import SDKFeature
from typing import List
from .types import ProjectContext
from .features import feature_registry
from .constants import COMMON_PYTHON_DEPENDENCIES
from ..utils.runtime.container import ContainerRuntime

def generate_project(name: str, features: List[BootstrapFeature]):
    output_path = (Path.cwd() / name)
    output_path.mkdir(exist_ok=False)
    ctx = ProjectContext(
        name=name,
        output_dir=output_path,
        features=features,
        python_dependencies=[],
    )

    # Collect dependencies from features, starting with common deps
    deps = set(COMMON_PYTHON_DEPENDENCIES)
    for feature in ctx.features:
        feature_cls = feature_registry[feature]
        deps.update(feature_cls().python_dependencies)
    ctx.python_dependencies = sorted(deps)

    # Render SDK snippet templates
    for feature in ctx.features:
        instance = feature_registry[feature]()
        if isinstance(instance, SDKFeature):
            instance.render_snippets(ctx)
        else:
            instance.apply(ctx)

    render_base_templates(ctx)

    ContainerRuntime().generate_dockerfile(agent_path=Path(ctx.output_dir / "src" / "main.py"), output_dir=ctx.output_dir, agent_name=f"{ctx.name}-agent")



def render_base_templates(context: ProjectContext):
    """
    Use jinja to create the common template files
    """
    template_dir = Path(__file__).parent / "templates"
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape()
    )

    for src in template_dir.rglob("*.j2"):
        relative_path = src.relative_to(template_dir)
        destination_path = context.output_dir / relative_path.with_suffix("") # drop .j2
        destination_path.parent.mkdir(parents=True, exist_ok=True)

        template = env.get_template(str(relative_path))
        destination_path.write_text(template.render(context.dict()))