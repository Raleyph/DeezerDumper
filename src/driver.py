import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from fake_useragent import UserAgent
from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask

from filemanager import CookieDumper
from proxy import ProxyRepository


class DeezerDriver:
    __URL = os.getenv("DEEZER_LOGIN_PAGE_URL")
    __WEBDRIVER_PATH = os.getenv("WEBDRIVER_PATH")
    __RECAPTCHA_URL = os.getenv("RECAPTCHA_URL")

    __API_KEY = os.getenv("API_KEY")
    __SITE_KEY = os.getenv("SITE_KEY")

    __HOMEPAGE_IDS = ["dzr-app", "offer_page"]

    def __init__(
            self,
            cookies_manager: CookieDumper,
            proxy_repository: ProxyRepository,
            login: str,
            password: str
    ):
        self.__cookies_manager = cookies_manager
        self.__proxy_repository = proxy_repository

        self.__login = login
        self.__password = password
        self.__cookies_filename = f"{self.__login}_cookies"

        self.__check_validity()

        service = Service(executable_path=self.__WEBDRIVER_PATH)

        self.__driver = webdriver.Chrome(options=self.__get_driver_options(), service=service)
        self.__driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            """
        })

        self.__driver.get(self.__URL)
        self.__driver.implicitly_wait(10)

    def __del__(self):
        try:
            self.__driver.close()
        except AttributeError:
            pass

    @property
    def dump_path(self) -> str:
        return os.path.join(self.__cookies_manager.COOKIES_DIRNAME, self.__cookies_filename)

    def __check_validity(self) -> None:
        if not os.path.isfile(self.__WEBDRIVER_PATH):
            raise FileNotFoundError("Chrome driver missing!")

        if self.__cookies_manager.is_cookies_exist(self.__cookies_filename):
            raise ExistingCookiesException(self.__login)

    def __get_driver_options(self) -> Options:
        useragent = UserAgent()
        options = Options()

        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(f"--user-agent={useragent.random}")

        options.add_experimental_option("detach", True)

        if os.getenv("START_MAXIMIZED").lower() in ("true", "1"):
            options.add_argument("--start-maximized")

        if os.getenv("HEADLESS_MODE").lower() in ("true", "1"):
            options.add_argument("--headless")

        if self.__proxy_repository.is_available:
            proxy = self.__proxy_repository.get_random_proxy()

            if proxy.plugin_path:
                options.add_extension(proxy.plugin_path)
            else:
                options.add_argument(f"--proxy-server={proxy.address}")

        return options

    def __accept_cookies(self) -> None:
        try:
            dismiss_cookies_button = self.__driver.find_element(By.ID, "gdpr-btn-accept-all")
        except NoSuchElementException:
            return
        else:
            dismiss_cookies_button.click()

    def __login_to_account(self) -> None:
        login_input = self.__driver.find_elements(By.CLASS_NAME, "unlogged-input")
        login_input[0].send_keys(self.__login)
        login_input[1].send_keys(self.__password)

        login_button = self.__driver.find_element(By.ID, "login_form_submit")

        if not login_button.get_attribute("disabled"):
            login_button.click()

    def __solve_captcha(self) -> None:
        try:
            captcha_iframes: list[WebElement] = WebDriverWait(self.__driver, 5).until(
                ec.presence_of_all_elements_located((By.TAG_NAME, "iframe"))
            )

            target_iframe = None

            for iframe in captcha_iframes:
                iframe_src = iframe.get_attribute("src")

                if (
                        iframe_src == "" or self.__RECAPTCHA_URL not in iframe_src
                        or iframe.get_attribute("title") == "reCAPTCHA"
                ):
                    continue

                target_iframe = iframe

            if not target_iframe:
                return

            self.__driver.switch_to.frame(target_iframe)
            self.__driver.find_element(By.CLASS_NAME, "rc-imageselect-payload")
            self.__driver.switch_to.default_content()
        except (TimeoutException, NoSuchElementException):
            pass
        else:
            captcha_solver = AnticaptchaClient(self.__API_KEY)
            captcha_task = NoCaptchaTaskProxylessTask(website_url=self.__URL, website_key=self.__SITE_KEY)

            job = captcha_solver.createTask(captcha_task)
            job.join()

            response = job.get_solution_response()

            self.__driver.execute_script(
                f"document.getElementById('g-recaptcha-response').innerHTML = arguments[0];"
                f"___grecaptcha_cfg.clients[0].T.T.callback(arguments[0]);",
                response['code']
            )

    def __check_redirect(self):
        for homepage_id in self.__HOMEPAGE_IDS:
            try:
                WebDriverWait(self.__driver, 5).until(ec.presence_of_element_located((By.ID, homepage_id)))
            except TimeoutException:
                pass
            else:
                return

        raise TimeoutError("Redirection timed out! Try restarting the program!")

    def get_cookies(self) -> list[dict]:
        self.__accept_cookies()
        self.__login_to_account()
        self.__solve_captcha()
        self.__check_redirect()

        return self.__driver.get_cookies()


class ExistingCookiesException(Exception):
    def __init__(self, login: str):
        self.__login = login

    def __str__(self):
        return f"Cookies for {self.__login} are already written!"
