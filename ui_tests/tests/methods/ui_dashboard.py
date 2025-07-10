import sys
sys.path.append("./")
from api_tests.src.api_utils.allure_reporter import AllureReporter


def ui_test_dashboard_landing_page(
    AllureReporter:AllureReporter,
    case_id:str
):
    AllureReporter.log_info(f"this is landing page test for case {case_id}")


print(globals().keys())