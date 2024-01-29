from filemanager import FileReader, CookieDumper
from proxy import ProxyRepository, NoWorkingProxyServersError
from driver import DeezerDriver, ExistingCookiesException

from selenium.common.exceptions import NoSuchWindowException, JavascriptException


class DeezerDumper:
    def __init__(self):
        self.__reader = FileReader()
        self.__cookie_dumper = CookieDumper()
        self.__proxy_repository = ProxyRepository(self.__reader)

        self.__dumps_count = 0

    def start(self):
        accounts = self.__reader.accounts

        print(f"Accounts count: {len(accounts)}\n")

        for account in accounts:
            try:
                driver = DeezerDriver(self.__cookie_dumper, self.__proxy_repository, account[0], account[1])
            except ExistingCookiesException as cookies_error:
                print(cookies_error)
            except JavascriptException as js_error:
                print(f"Unexpected Javascript error: {js_error}")
            else:
                self.__cookie_dumper.dump_cookies(driver.get_cookies(), driver.dump_path)
                self.__dumps_count += 1

                print(f"Dumping cookie for account {account[0]} complete.")

        print(f"\nDumping cookie for all accounts ({self.__dumps_count}) complete!")


def main():
    try:
        deezer_dumper = DeezerDumper()
    except FileNotFoundError as file_error:
        print(file_error)
    except (ValueError, NotADirectoryError, TimeoutError) as critical_error:
        print(critical_error)
    except NoWorkingProxyServersError as proxy_error:
        print(proxy_error)
    else:
        deezer_dumper.start()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, NoSuchWindowException):
        print("Script execution stopped by user!")
