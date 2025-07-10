import importlib
import inspect
import os
import sys
import pytest
from api_tests.src.api_utils.allure_reporter import AllureReporter
from api_tests.src.api_utils.testrail_integration import (
    get_testrail_case,
    get_test_from_run_by_test_id,
    update_test_result,
)
from api_tests.tests.conftest import get_test_cases_grouped_by_section
from ui_tests.tests.ui_test_suites import R5_2_prompts_regression_testing_single_turn

actual_run_name, test_case_data = get_test_cases_grouped_by_section(
    test_plan_name=R5_2_prompts_regression_testing_single_turn,
    run_name="Prompt_Regression",
    flatten=True,
    include_section_names=True,
)

test_map:dict = {
    "Google and Microsoft" :"ui_test_dashboard_landing_page",
    "Already have an account": "ui_test_setting_page"
}

methods_path = os.path.join(os.path.dirname(__file__), "methods")
project_root = os.path.abspath(os.path.join(__file__, ".."))
sys.path.insert(0, project_root)

for file in os.listdir(methods_path):
    if file.endswith(".py") and not file.startswith("__"):
        mod_name = file[:-3]
        full_import = f"methods.{mod_name}"
        module = importlib.import_module(full_import)
        for name, obj in vars(module).items():
            if inspect.isfunction(obj):
                globals()[name] = obj
                
@pytest.mark.parametrize("section_name, run_id, test_id", test_case_data)
def test_runid_section_and_test_id(
    testrail_client_fixture,section_name, run_id, test_id
):
    AllureReporter.set_parent_and_section_suite(f"{actual_run_name} - {section_name}")
    AllureReporter.start_test(
        f"Workflow Execution for TestRail Run ID {run_id}, Test ID {test_id}"
    )

    if not testrail_client_fixture:
        AllureReporter.log_warning("TestRail client not available. Skipping test.")
        pytest.skip("TestRail client not available.")
        return
    print(globals())
    test_result = 1 
    comment = ""
    try:
        test_data = get_test_from_run_by_test_id(
            testrail_client_fixture, run_id, test_id
        )
        AllureReporter.assert_that(
            test_data, f"No test found in Run {run_id} with Test ID {test_id}"
        )

        case_id = test_data["case_id"]
        case_data = get_testrail_case(testrail_client_fixture, case_id)
        AllureReporter.assert_that(case_data, f"Failed to retrieve case ID {case_id}")
        title = case_data.get("title", "No title")
        AllureReporter.log_info(f"Retrieved TestRail title for T{test_id}: {title}")

        expected_output = case_data.get("custom_case_automation_expected_output")
        AllureReporter.log_info(f"Expected Output: {expected_output}")

        for key in test_map:
            if key in title:
                test_function = globals().get(test_map[key])
                AllureReporter.assert_that(
                    test_function, f"Test function for {key} not found"
                )
                AllureReporter.log_info(f"Running test function: {test_map[key]}")
                test_function(AllureReporter, case_id)
                break

    except AssertionError as ae:
        comment = str(ae)
        AllureReporter.log_warning(f"Assertion failed: {comment}")

    except Exception as e:
        comment = f"Unexpected error occurred: {str(e)}"
        AllureReporter.log_warning(comment)

    finally:
        try:
            update_test_result(
                testrail_client_fixture, run_id, test_id, test_result, comment
            )
            AllureReporter.log_info(
                f"TestRail updated: T{test_id}, Status: {test_result}"
            )
        except Exception as e:
            AllureReporter.log_warning(
                f"Failed to update TestRail result for T{test_id}: {str(e)}"
            )
