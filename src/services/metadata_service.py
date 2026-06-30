from pathlib import Path

import yaml

from models.work_item import WorkItem


class MetadataService:
    """
    Handles creation and management of work item metadata.
    """

    @staticmethod
    def write(
        folder: Path,
        work_item: WorkItem,
    ) -> Path:
        """
        Creates metadata.yaml for a work item.
        """

        metadata = {
            "id": work_item.id,
            "type": work_item.work_type,
            "title": work_item.title,
            "status": work_item.status,
            "priority": work_item.priority,
            "created": work_item.created,
            "updated": work_item.updated,
            "assignee": work_item.assignee,
            "tags": work_item.tags,
        }

        metadata_file = folder / "metadata.yaml"

        with metadata_file.open(
            "w",
            encoding="utf-8",
        ) as file:

            yaml.safe_dump(
                metadata,
                file,
                sort_keys=False,
                allow_unicode=True,
            )

        return metadata_file