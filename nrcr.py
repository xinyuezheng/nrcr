import configparser
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

config = configparser.ConfigParser()
config.read('config.ini')

username = config['default']['username']
email = config['default']['email']
prefered_time = config['default']['prefered_time']
http_page = config['default']['url']

#HTTP_PAGE = "http://doodle.com/poll/sz94cavn8r4657d2"
option_time = datetime.strptime(prefered_time, '%H:%M %p')
option_list = []

def get_option(option_list):
    min_delta = 86400.0  # seconds/day
    for option in option_list:
        time_raw = (option.get_attribute("title"))
        time_reg = re.match(r"(.*?)(\d+:\d+ (A|P)M)", time_raw)
        selected_time = datetime.strptime(time_reg.group(2), '%H:%M %p')
        time_delta = abs((selected_time - option_time).total_seconds())
        if time_delta < min_delta:
            min_delta = time_delta
            my_option = option
    return my_option

browser = webdriver.Firefox()
browser.get(http_page)
browser.maximize_window()
try:
    elem = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "tr.header.date.month th.asep")))
    elem.click()
except TimeoutException:
    pass

#check the first instance of existing name
try:
    existing_name = browser.find_element(By.XPATH, '//div[contains(@class, "pname") and contains(@title, "%s")]' % username)
    print("already registered")
    browser.quit()
    exit(0)
except NoSuchElementException:
    pass

event_list = browser.find_elements_by_css_selector('tr.participation.yesNo.partMyself td:not(.disabled)')

for event in event_list[1:]:
    option_list.append(event)

if option_list:
    pname_list = browser.find_elements_by_id('pname')
    if pname_list:
        pname_list[0].send_keys(username)
        option = get_option(option_list)
        option.click()
        button_list = browser.find_elements_by_id('save')
        if button_list:
            button_list[0].click()

browser.quit()
