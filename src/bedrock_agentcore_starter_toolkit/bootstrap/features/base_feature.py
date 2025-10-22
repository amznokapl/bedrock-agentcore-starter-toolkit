from __future__ import annotations
from pathlib import Path
from typing import Any
from abc import ABC, abstractmethod
from jinja2 import Environment, FileSystemLoader, TemplateError
from ..types import ProjectContext


class Feature(ABC):
    """Base feature class for applying Jinja2-based templates to a target directory."""

    name: str  # subclasses must override
    python_dependencies: list[str] = []

    def __init__(self) -> None:
        if not getattr(self, "name", None):
            raise ValueError(f"{self.__class__.__name__} must define a 'name' attribute")

        self.template_dir = Path(__file__).parent / self.name.lower() / "templates"

        if not self.template_dir.exists():
            raise FileNotFoundError(f"Template directory not found: {self.template_dir}")

        self.env = Environment(loader=FileSystemLoader(self.template_dir))


    def before_apply(self, context: ProjectContext) -> None:
        """Hook for implementing additional logic before templates are applied"""
        pass

    def after_apply(self, context: ProjectContext) -> None:
        """Hook for implementing any additional logic after templates are applied."""
        pass

    def apply(self, context: ProjectContext) -> None:
        """Render all Jinja2 templates in the feature’s directory into the target directory."""

        self.before_apply(context)

        for src in self.template_dir.rglob("*.j2"):
            rel = src.relative_to(self.template_dir)
            dest = context.output_dir / rel.with_suffix("")  # remove .j2 from output filename
            dest.parent.mkdir(parents=True, exist_ok=True)

            try:
                template = self.env.get_template(str(rel))
                rendered = template.render(context.dict())
            except TemplateError as e:
                raise RuntimeError(f"Error rendering template '{rel}': {e}") from e

            dest.write_text(rendered)

        self.after_apply(context)


class SDKFeature(Feature):
    """Base class for SDK features that inject code fragments into shared templates."""

    ENTRYPOINT_SNIPPET_KEYS = [
        "agent_imports",
        "agent_instantiation",
        "agent_invocation",
    ]

    def render_snippets(self, context: ProjectContext):
        """Render SDK-specific code snippets directly into the context."""
        for key in self.ENTRYPOINT_SNIPPET_KEYS:
            template_path = self.template_dir / f"{key}.j2"
            if not template_path.exists():
                continue

            # Usually Jinja2 env templates are referenced by relative name
            template = self.env.get_template(template_path.name)
            rendered = template.render(context.dict())

            # Set the field dynamically on the context
            setattr(context, key, rendered)