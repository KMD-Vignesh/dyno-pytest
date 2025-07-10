import sys
sys.path.append("./")
from api_tests.src.api_utils.allure_reporter import AllureReporter

def ui_test_setting_page(
    AllureReporter:AllureReporter,
    case_id:str
):
    AllureReporter.log_info(f"this is setting page test for case {case_id}")