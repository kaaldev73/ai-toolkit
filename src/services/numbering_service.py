from config.config import OUTPUT_DIR


class NumberingService:
    """
    Generates sequential work item numbers.

    Examples

        BUG-001
        BUG-002
        FEAT-001
    """

    @staticmethod
    def get_next_number(prefix: str) -> int:

        if not OUTPUT_DIR.exists():
            return 1

        highest = 0

        for folder in OUTPUT_DIR.iterdir():

            if not folder.is_dir():
                continue

            name = folder.name

            if not name.startswith(prefix):
                continue

            parts = name.split("-")

            if len(parts) < 2:
                continue

            try:
                number = int(parts[1])
                highest = max(highest, number)

            except ValueError:
                continue

        return highest + 1