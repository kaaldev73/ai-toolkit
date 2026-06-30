from models.work_item import WorkItem
from services.numbering_service import NumberingService


class WorkItemFactory:
    """
    Factory responsible for creating WorkItem objects.
    """

    PREFIXES = {
        "bug": "BUG",
        "feature": "FEAT",
        "refactor": "REF",
    }

    @classmethod
    def create(
        cls,
        work_type: str,
        title: str,
    ) -> WorkItem:
        """
        Creates a new WorkItem.
        """

        work_type = work_type.lower().strip()

        if work_type not in cls.PREFIXES:
            raise ValueError(f"Unsupported work type: {work_type}")

        prefix = cls.PREFIXES[work_type]

        number = NumberingService.get_next_number(prefix)

        return WorkItem(
            prefix=prefix,
            number=number,
            work_type=work_type,
            title=title,
        )

    @classmethod
    def create_bug(
        cls,
        title: str,
    ) -> WorkItem:
        return cls.create(
            work_type="bug",
            title=title,
        )

    @classmethod
    def create_feature(
        cls,
        title: str,
    ) -> WorkItem:
        return cls.create(
            work_type="feature",
            title=title,
        )

    @classmethod
    def create_refactor(
        cls,
        title: str,
    ) -> WorkItem:
        return cls.create(
            work_type="refactor",
            title=title,
        )