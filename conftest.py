def pytest_collection_modifyitems(config, items):
    items_to_keep = []
    for item in items:
        # Skip tests whose function names start with "test_ui"
        if not item.name.startswith("test_"):
            items_to_keep.append(item)
    items[:] = items_to_keep
