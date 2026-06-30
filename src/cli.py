from factories.work_item_factory import WorkItemFactory
from services.work_item_service import WorkItemService


def main():

    print("\n===================================")
    print("      AI Engineering Toolkit")
    print("===================================\n")

    work_type = input(
        "Work Item Type (bug/feature/refactor): "
    ).strip().lower()

    title = input(
        "Title: "
    ).strip()

    try:

        work_item = WorkItemFactory.create(
            work_type=work_type,
            title=title,
        )

        folder = WorkItemService.create(
            work_item
        )

        print("\n✅ Work Item Created Successfully\n")

        print(f"ID      : {work_item.id}")
        print(f"Folder  : {folder}")

    except Exception as ex:

        print(f"\n❌ {ex}")


if __name__ == "__main__":
    main()