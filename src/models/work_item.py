from dataclasses import dataclass, field
from datetime import date


@dataclass(slots=True)
class WorkItem:
    """
    Represents a single engineering work item.
    """

    prefix: str
    number: int

    work_type: str
    title: str

    status: str = "Draft"
    priority: str = "Medium"

    created: str = field(
        default_factory=lambda: date.today().isoformat()
    )

    updated: str = field(
        default_factory=lambda: date.today().isoformat()
    )

    assignee: str = ""

    tags: list[str] = field(default_factory=list)

    @property
    def id(self) -> str:
        return f"{self.prefix}-{self.number:03}"

    @property
    def folder_name(self) -> str:
        """
        Filesystem-safe folder name.
        """

        invalid = '<>:"/\\|?*'

        safe_title = self.title

        for char in invalid:
            safe_title = safe_title.replace(char, "")

        safe_title = "-".join(safe_title.split())

        return f"{self.id}-{safe_title}"

    def __str__(self) -> str:
        return self.id