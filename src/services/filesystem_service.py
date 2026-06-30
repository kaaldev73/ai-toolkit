from pathlib import Path

from config.config import OUTPUT_DIR
from models.work_item import WorkItem


class FileSystemService:
    """
    Handles all filesystem operations for work items.
    """

    @staticmethod
    def create_work_item_folder(work_item: WorkItem) -> Path:
        """
        Creates the work item folder.

        Example

        output/
            BUG-001-Dashboard-Investor-page/
        """

        folder = OUTPUT_DIR / work_item.folder_name

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        return folder