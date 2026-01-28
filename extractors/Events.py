from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, UnexpectedAlertPresentException, NoSuchFrameException, NoAlertPresentException, ElementNotVisibleException, InvalidElementStateException
from urllib.parse import urlparse, urljoin
import json
import pprint
import datetime
import tldextract
import math
import os
import traceback
import random
import re
import logging
import copy
import time

import Classes
from selenium.webdriver.common.by import By

def extract_data_toggle(driver):
    toggles = driver.find_elements(By.XPATH, "//button[@data-toggle]")
    dos = []
    for toggle in toggles:

        xpath = driver.execute_script("return getXPath(arguments[0])", toggle) 
        do = {'function_id': '',
              'event': 'click',
              'id': toggle.get_attribute('id'),
              'tag': 'button',
              'addr': xpath,
              'class': ''}
        dos.append(do)

    return dos

def extract_inputs(driver):
    toggles = driver.find_elements(By.TAG_NAME, ".//input") 
    dos = []
    for toggle in toggles:
        input_type = toggle.get_attribute("type")
        if (not input_type) or input_type == "text":

            in_form = toggle.find_elements(By.TAG_NAME,".//ancestor::form")
            if not in_form:
                xpath = driver.execute_script("return getXPath(arguments[0])", toggle)
                do = {'function_id': '',
                      'event': 'input',
                      'id': toggle.get_attribute('id'),
                      'tag': 'input',
                      'addr': xpath,
                      'class': ''}
                dos.append(do)

    toggles = driver.find_elements(By.TAG_NAME, "//textarea")
    for toggle in toggles:
        xpath = driver.execute_script("return getXPath(arguments[0])", toggle)
        do = {'function_id': '',
              'event': 'input',
              'id': toggle.get_attribute('id'),
              'tag': 'input',
              'addr': xpath,
                  'class': ''}
        dos.append(do)

    return dos



def extract_fake_buttons(driver):
    fake_buttons = driver.find_elements(By.TAG_NAME, "btn") 
    dos = []
    for button in fake_buttons:

        xpath = driver.execute_script("return getXPath(arguments[0])", button) 
        do = {'function_id': '',
              'event': 'click',
              'id': button.get_attribute('id'),
              'tag': 'a',
              'addr': xpath,
              'class': 'btn'}
        dos.append(do)

    return dos


def extract_events(driver):
    # Use JavaScript to find events
    todo = []
    try:
        resps = driver.execute_script("return catch_properties()")
        if resps:
            try:
                todo = json.loads(resps)
            except Exception:
                logging.exception("Failed to parse catch_properties response")
                todo = []
    except Exception:
        logging.exception("catch_properties() JS failed")

    # From event listeners
    try:
        resps = driver.execute_script("return JSON.stringify(added_events)")
        if resps:
            try:
                todo += json.loads(resps)
            except Exception:
                logging.exception("Failed to parse added_events response")
    except Exception:
        logging.exception("added_events JS failed")

    # From data-toggle
    try:
        resps = extract_data_toggle(driver)
        todo += resps
    except Exception:
        logging.exception("extract_data_toggle failed")


    # Only works in Chrome DevTools
    # resps = driver.execute_script("catch_event_listeners()");
    # todo += resps

    # From fake buttons class="btn"
    try:
        resps = extract_fake_buttons(driver)
        todo += resps
    except Exception:
        logging.exception("extract_fake_buttons failed")

    try:
        resps = extract_inputs(driver)
        todo += resps
    except Exception:
        logging.exception("extract_inputs failed")

    #for do in todo:
    #    print(do)

    events = set()
    for do in todo:
        event = Classes.Event(do['function_id'], 
                      do['event'],
                      do['id'],
                      do['tag'],
                      do['addr'],
                      do['class'])
        events.add(event)

    return events


