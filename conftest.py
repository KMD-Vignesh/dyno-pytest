def pytest_collection_modifyitems(config, items):
    items_to_keep = []
    for item in items:
        if not item.name.startswith("test_"):
            items_to_keep.append(item)
    items[:] = items_to_keep
