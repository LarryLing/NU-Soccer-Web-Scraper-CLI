import time

from selenium.common import TimeoutException, WebDriverException

from utils import initialize_web_driver, download_pdf_to_cwd, print_failure_message


def download_roster(url: str, filename: str) -> None:
    """
    Downloads the roster page to a PDF file.

    Args:
        url: URL of the site.
        filename: Name of the downloaded file.

    Returns:
        None
    """
    driver = initialize_web_driver()

    script = """
        let removed = document.getElementById('divSatisfiChat'); 
        if (removed) removed.parentNode.removeChild(removed);

        removed = document.getElementById('transcend-consent-manager'); 
        if (removed) removed.parentNode.removeChild(removed);

        removed = document.getElementById('termly-code-snippet-support'); 
        if (removed) removed.parentNode.removeChild(removed);
    """

    try:
        driver.get(url)
        time.sleep(1)

        driver.execute_script(script)

        download_pdf_to_cwd(driver, filename)
    except TimeoutException as e:
        print_failure_message(filename, e.msg)
    except WebDriverException as e:
        print_failure_message(filename, e.msg)
    finally:
        driver.quit()
