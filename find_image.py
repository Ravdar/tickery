import requests
from bs4 import BeautifulSoup as bs
import re
import pycountry


def find_logo(ticker):
    """Scrapes TradingView website in order to get logo of company based on provided ticker"""

    url = f"https://www.tradingview.com/symbols/{ticker}"
    pattern = r'src="(.*?)"'

    response = requests.get(url)
    soup = bs(response.content, "html.parser")
    img_elements = soup.find_all(
        "img", class_="tv-circle-logo tv-circle-logo--xxlarge medium-xoKMfU7r"
    )
    img_element = str(img_elements[0])
    match = re.findall(pattern, img_element)
    logo_url = match[0]

    return logo_url


def find_bg_color(logo_url):

    pattern = r'fill="(.*?)"'

    response = requests.get(logo_url)
    soup = bs(response.content, "html.parser")
    bg_color_code = str((soup.find_all("path"))[0])
    match = re.findall(pattern, bg_color_code)

    return match[0]


def find_flag(country):
    """Returns url to image of flag based on provided country name"""

    country_info = pycountry.countries.search_fuzzy(country)
    country_code = country_info[0].alpha_2

    flag_url = f"https://flagsapi.com/{country_code}/flat/64.png"

    return flag_url
