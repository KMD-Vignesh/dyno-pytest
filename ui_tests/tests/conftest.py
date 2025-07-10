import shutil
import os
import json
import pytest
from api_tests.src.api_services.custom_emergence_api_services import (
    CustomEmergenceAPIService,
)
from api_tests.src.api_utils.testrail_integration import testrail_client
from api_tests.src.api_utils.logger import logger

service = CustomEmergenceAPIService()


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    """Clean logs and allure-results folders at test session start."""
    # Clean allure-results folder
    results_dir = os.path.join(os.getcwd(), "ui_tests","allure-results")
    if os.path.exists(results_dir):
        for filename in os.listdir(results_dir):
            file_path = os.path.join(results_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
        print("Cleared contents of allure-results folder.")
    else:
        os.makedirs(results_dir)
        print("Created allure-results folder.")

    # Clean allure-report folder
    report_dir = os.path.join(os.getcwd(), "ui_tests", "allure-report")
    if os.path.exists(report_dir):
        for filename in os.listdir(report_dir):
            file_path = os.path.join(report_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")
        print("Cleared contents of allure-report folder.")
    else:
        os.makedirs(report_dir)
        print("Created allure-report folder.")

    # Clean logs folder
    log_dir = os.path.join(os.getcwd(), "ui_tests", "ui_logs")
    if os.path.exists(log_dir):
        for filename in os.listdir(log_dir):
            file_path = os.path.join(log_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    # Clear the content of the file
                    with open(file_path, "w") as file:
                        file.truncate(0)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to clear content of {file_path}. Reason: {e}")
        print("Cleared contents of ui_logs folder.")
    else:
        os.makedirs(log_dir)
        print("Created ui_logs folder.")


# HELPER FUNCTION
def get_test_cases_for_run(test_plan_name, run_name):
    """
    Fetch test IDs dynamically from TestRail for the given run_name inside test_plan_name,
    update the test_plan_name dictionary with those test IDs, and then return a list of
    (run_id, test_id) tuples for the run.

    Args:
      test_plan_name: Dictionary containing runs and run IDs (e.g., R3_2_prompts_regression_testing)
      run_name: Name of the run to fetch test cases for (e.g., R3_2_prompts_regression_testing)

    Returns:
      List of (run_id, test_id) tuples for the specified run
    """
    logger.info(f"Fetching test cases for run: '{run_name}'")

    run_config = test_plan_name.get(run_name)
    if not run_config:
        error_msg = f"Test run '{run_name}' not found in configuration."
        logger.error(error_msg)
        raise ValueError(error_msg)

    run_id = run_config["run_id"]
    logger.info(f"Using run_id: {run_id}")

    # Fetch test IDs dynamically from TestRail
    try:
        response = testrail_client().tests.get_tests(run_id=run_id)
        tests = response.get("tests", [])
        test_ids = [test["id"] for test in tests]

        run_config["test_ids"] = test_ids  # Update the original dict dynamically
        logger.info(
            f"Successfully populated {len(test_ids)} test IDs for run '{run_name}' (ID: {run_id})"
        )
    except Exception as e:
        logger.error(
            f"Failed to populate test IDs for run_id {run_id}: {e}", exc_info=True
        )
        # logger.exception(f"Failed to populate test IDs for run_id {run_id}")
        run_config["test_ids"] = []

    # Prepare the list of (run_id, test_id) tuples
    test_cases = [(run_id, test_id) for test_id in run_config.get("test_ids", [])]

    logger.debug(f"Test case tuples: {test_cases}")
    return test_cases


"""
    Fetch test IDs dynamically from TestRail for the given run_name inside test_plan_name,
    and group them by their section (folder) name.

    Args:
        test_plan_name (dict): Dictionary with run names as keys and configs including run_id.
        run_name (str): Specific run name to fetch test cases for.
        flatten (bool): If True, return a flat list of (run_id, test_id) tuples.
        include_section_names (bool): If True with flatten, return (section_name, run_id, test_id) instead.

    Returns:
        dict or list: 
            - If flatten is False: dict with section names as keys and list of (run_id, test_id) as values.
            - If flatten is True and include_section_names is False: flat list of (run_id, test_id).
            - If flatten is True and include_section_names is True: flat list of (section_name, run_id, test_id).
    """


def get_full_section_path(client, section_id):
    path = []
    try:
        while section_id:
            section = client.sections.get_section(section_id)
            path.insert(0, section["name"])
            section_id = section.get("parent_id")
    except Exception as e:
        logger.warning(f"Error retrieving full section path: {e}")
    return " > ".join(path) if path else f"Section {section_id or 'Unknown'}"


def get_test_cases_grouped_by_section(
    test_plan_name, run_name, flatten=False, include_section_names=False
):
    logger.info(f"Fetching and grouping test cases for run: '{run_name}'")

    run_config = test_plan_name.get(run_name)
    if not run_config:
        error_msg = f"Test run '{run_name}' not found in ui_test_suite."
        logger.error(error_msg)
        raise ValueError(error_msg)

    run_id = run_config["run_id"]
    logger.info(f"Using run_id: {run_id}")

    grouped_test_cases = {}

    try:
        client = testrail_client()
        run_details = client.runs.get_run(run_id)
        actual_run_name = run_details.get("name", f"Run {run_id}")
        logger.info(f"Actual run name fetched from TestRail: '{actual_run_name}'")

        response = client.tests.get_tests(run_id=run_id)
        tests = response.get("tests", [])

        for test in tests:
            test_id = test["id"]
            case_id = test.get("case_id")
            section_id = test.get("section_id")

            if not section_id and case_id:
                case = client.cases.get_case(case_id)
                section_id = case.get("section_id")

            if section_id:
                section_name = get_full_section_path(client, section_id)
            else:
                section_name = "Unknown Section"

            grouped_test_cases.setdefault(section_name, []).append((run_id, test_id))

        logger.info(
            f"Grouped test cases by section for run_id={run_id}:\n{json.dumps(grouped_test_cases, indent=2)}"
        )

        if flatten:
            flattened = []
            for section, tests in grouped_test_cases.items():
                for run_id, test_id in tests:
                    item = ()
                    if include_section_names:
                        item += (section,)
                    item += (run_id, test_id)
                    flattened.append(item)
            return actual_run_name, flattened

        return actual_run_name, grouped_test_cases

    except Exception as e:
        logger.error(
            f"Error while fetching/grouping test cases for run_id {run_id}: {e}",
            exc_info=True,
        )
        return None, []



@pytest.fixture(scope="session")
def testrail_client_fixture():
    return testrail_client()
