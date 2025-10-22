from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Optional
from .features.types import BootstrapFeature

@dataclass
class ProjectContext:
    name: str
    output_dir: Path
    features: List[BootstrapFeature]
    python_dependencies: List[str]
    iac_dir: Optional[Path] = None
    agent_imports: Optional[str] = ""
    agent_instantiation: Optional[str] = ""
    agent_invocation: Optional[str] = ""

    def dict(self):
        return asdict(self)
