class BusinessLogic:
    @staticmethod
    def process_user(data):
        return f"\nUser {data['name']} processed with ID {data['id']}"

    @staticmethod
    def process_admin(data):
        return f"\nAdmin {data['name']} processed with elevated privileges"

    @staticmethod
    def process_guest(data):
        return f"\nGuest {data['name']} processed with limited access"

    @staticmethod
    def process_moderator(data):
        return f"\nModerator {data['name']} processed with moderation rights"


business_logic = BusinessLogic()


TEST_DATA = [
    {"id": 1, "type": "user", "name": "John", "email": "john@example.com"},
    {"id": 2, "type": "admin", "name": "Alice", "email": "alice@example.com"},
    {"id": 3, "type": "user", "name": "Bob", "email": "bob@example.com"},
    {"id": 4, "type": "guest", "name": "Charlie", "email": "charlie@example.com"},
    {"id": 5, "type": "moderator", "name": "Diana", "email": "diana@example.com"},
    {"id": 6, "type": "user", "name": "Eve", "email": "eve@example.com"},
    {"id": 7, "type": "admin", "name": "Frank", "email": "frank@example.com"},
]


def original_for_loop_logic():
    results = []

    for item in TEST_DATA:
        if item["type"] == "user":
            result = business_logic.process_user(item)
            results.append(result)
        elif item["type"] == "admin":
            result = business_logic.process_admin(item)
            results.append(result)
        elif item["type"] == "guest":
            result = business_logic.process_guest(item)
            results.append(result)
        elif item["type"] == "moderator":
            result = business_logic.process_moderator(item)
            results.append(result)

    return results


def generate_test_cases():
    test_cases = []

    for item in TEST_DATA:
        test_name = f"ui_{item['type']}_{item['name'].lower()}_processing"

        if item["type"] == "user":
            test_cases.append(
                (
                    test_name,
                    item,
                    business_logic.process_user,
                    ["User", item["name"], str(item["id"])],
                )
            )
        elif item["type"] == "admin":
            test_cases.append(
                (
                    test_name,
                    item,
                    business_logic.process_admin,
                    ["Admin", item["name"], "elevated"],
                )
            )
        elif item["type"] == "guest":
            test_cases.append(
                (
                    test_name,
                    item,
                    business_logic.process_guest,
                    ["Guest", item["name"], "limited"],
                )
            )
        elif item["type"] == "moderator":
            test_cases.append(
                (
                    test_name,
                    item,
                    business_logic.process_moderator,
                    ["Moderator", item["name"], "moderation"],
                )
            )

    return test_cases


def create_test_function(test_data, test_func, expected_keywords):
    def individual_test():
        result = test_func(test_data)

        assert result is not None, f"Function returned None for {test_data}"
        assert isinstance(result, str), f"Expected string result for {test_data}"

        for keyword in expected_keywords:
            assert keyword in result, f"Expected '{keyword}' in result '{result}'"

        assert test_data["name"] in result, (
            f"Name {test_data['name']} not found in result"
        )

        print(f"\n✓ Test passed for {test_data['type']} {test_data['name']}: {result}")

    return individual_test


_test_cases = generate_test_cases()

for test_name, test_data, test_func, expected_keywords in _test_cases:
    test_function = create_test_function(test_data, test_func, expected_keywords)

    test_function.__name__ = test_name
    test_function.__doc__ = (
        f"Test processing of {test_data['type']} {test_data['name']}"
    )

    globals()[test_name] = test_function
