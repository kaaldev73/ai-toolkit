from pathlib import Path

from models.work_item import WorkItem
from services.filesystem_service import FileSystemService
from services.metadata_service import MetadataService


class WorkItemService:
    """
    Coordinates the creation and management of work items.
    """

    @staticmethod
    def create(work_item: WorkItem) -> Path:

        folder = FileSystemService.create_work_item_folder(
            work_item
        )

        MetadataService.write(
            folder=folder,
            work_item=work_item,
        )

        return folder