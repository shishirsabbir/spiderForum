# importing selenium packages
from selenium import webdriver
from time import sleep as wait_for
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains as Action


def genBrowser():
    chrome_service = Service(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()
    set_arg = chrome_options.add_argument
    set_experiment = chrome_options.add_experimental_option

    # set options to make browser easier
    # set_arg('--headless') # to enable headless mode
    
    set_arg('disable-infobars') # disable infobar popus
    # set_arg('start-maximized') # start selenium in a maximized window
    set_arg('disable-dev-shm-usage') # disable developer mode error for linux and mac only
    set_arg('no-sandbox') # disable security sandbox layer **important
    set_arg('disable-blink-features=AutomationControlled') # disable detection of automation test
    set_experiment('excludeSwitches', ['enable-automation']) # for allowing the automation

    # mobile emulation
    # mobile_emulation = {"deviceName": "Samsung Galaxy S20 Ultra"}
    # set_experiment("mobileEmulation", mobile_emulation)

    # disable password saving popup and location sharing
    prefs = {"credentials_enable_service": False,
             "profile.password_manager_enabled": False,
             "profile.default_content_setting_values.geolocation" :2, 
             "profile.default_content_setting_values.notifications" : 2}
    set_experiment("prefs", prefs)

    driver = webdriver.Chrome(options=chrome_options, service=chrome_service)
    return driver

# setting up webdriver waits

def driverWait(driver_name, time):
    wait = WebDriverWait(driver_name, timeout=time)
    return wait

