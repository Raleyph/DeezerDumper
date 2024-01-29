# DeezerDumper

A program that automatically creates cookie dumps after authorizing an account for the Deezer streaming service.

Current version: 1.0

## 👩‍🏫 Usage
1. Install Python 3.11+ and pip.
2. Install **requirements.txt**.
3. Setup **.env** file.
4. Create a file called **account.txt** and enter your account credentials there.
5. Create a file called **proxy.txt** and enter your proxy credentials there.
6. Go to *src/* and run **main.py** file.

## ⚙️ Environment variables
Before running the program, make sure that the correct settings are specified in the .env file.

### ✅ You can change:
* **API_KEY** - API key for the captcha solver service (Anticaptcha).
* **START_MAXIMIZED** - run drivers in full screen mode (by default true).
* **HEADLESS_MODE** - run drivers in headless mode (by default false).
* **USE_PROXY** - use a proxy (by default false).

### ✅ You can change it, but it won't affect anything:
* **LOGIN_DATA_FILENAME** - name of the file with credentials.
* **PROXY_DATA_FILENAME** - name of the proxy server data file.
* **COOKIES_DIRNAME** - name of the directory with cookie dumps.
* **COOKIES_LIST_FILENAME** - name of the file with a list of ready-made cookie dumps.
* **PROXIES_DIRNAME** - name of the directory with proxy plugins.

### ❌ Do not change:
* **SITE_KEY** - site key for deezer.com.
* **WEBDRIVER_PATH** - path to Chrome webdriver.
* **DEEZER_LOGIN_PAGE_URL** - link to Deezer login page.
* **PROXY_SOURCE_DIRNAME** - path to the source files intended for generating proxy plugins.
* **PROXY_MANIFEST_FILENAME** and **PROXY_BACKGROUND_FILENAME** - source files intended for generating proxy plugins.

## 🔐 Credential format

To start working with the program, you must provide your Deezer account credentials and proxy server credentials (if any). 
Each set of credentials is entered on a new line. If you enter credentials in the wrong format, the program will notify you about this.

Account credential format (accounts.txt):
    
    login:password

Credential format for proxy servers with authorization (proxy.txt):

    ip:port:login:password

Credential format for proxy servers without authorization (proxy.txt):

    ip:port

> [!IMPORTANT]
> The program has a built-in proxy checker, so if a proxy is not working, the program will notify you about this and will 
> not continue working if there are no other working proxies.
