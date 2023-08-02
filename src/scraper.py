import pandas as pd
import requests
import json

from bs4 import BeautifulSoup as bs4
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options

def main():
    mlb_url = "https://www.mlb.com/scores"
    check_date = "2023-02-25"


def open_web_driver():
    options = Options()
    options.add_argument('--disable-blink-features=AutomationControlled')



if __name__ == "__main__":
    main()