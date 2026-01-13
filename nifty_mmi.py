from playwright.sync_api import sync_playwright
from datetime import datetime
import requests
import time
import json

NIFTY_URL = "https://www.niftytrader.in/live-nifty-open-interest"
TICKERTAPE_URL = "https://www.tickertape.in/market-mood-index"
POST_URL = "https://script.google.com/macros/s/AKfycbzBghC_r5iUsnk1zh_X6KZE3adsNDHDZo6128rH-Hay-CakEPdm_FSUQtkSc4aS-rU/exec"


def scrape_nifty_data():
    selectors = {
        'spot': "div[class='justify-content-lg-start justify-content-center flex-column spot_price_value spot_price_val d-none d-sm-flex'] span[class='spot_price fw-600 fs-16']",
        'max_pain': "body > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(5) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(3) > ul:nth-child(1) > li:nth-child(3) > p:nth-child(2)",
        'pcr_all': "body > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(5) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(3) > ul:nth-child(1) > li:nth-child(10) > p:nth-child(2)",
        'calls_oi': "body > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(5) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > ul:nth-child(1) > li:nth-child(1) > span:nth-child(2)",
        'puts_oi': "body > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(5) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > ul:nth-child(1) > li:nth-child(2) > span:nth-child(2)",
        'vix': ".fs-13.mb-0.text-green, .fs-13.mb-0.text-red"
    }

    data = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        try:
            page.goto(NIFTY_URL)
            time.sleep(10)

            data['spot'] = page.locator(selectors['spot']).inner_text()
            data['max_pain'] = page.locator(selectors['max_pain']).inner_text()
            data['pcr_all'] = page.locator(selectors['pcr_all']).inner_text()
            data['calls_oi'] = page.locator(selectors['calls_oi']).inner_text().replace("Calls OI", "").strip()
            data['puts_oi'] = page.locator(selectors['puts_oi']).inner_text().replace("Puts OI", "").strip()
            data['vix'] = page.locator(selectors['vix']).inner_text()
        except Exception as e:
            print(f"[ERROR] Nifty scrape failed: {e}")
            data['error'] = str(e)
        finally:
            browser.close()
    return data


def scrape_tickertape_data():
    selectors = {
        'from_value': "div[class='jsx-3769769187 from'] p[class='jsx-3769769187 value typography-body-regular-xs text-teritiary pt8 lh-100']",
        'to_value': "div[class='jsx-3769769187 to'] p[class='jsx-3769769187 value typography-body-regular-xs text-teritiary pt8 lh-100']",
        'percentage': ".jsx-3654585993.jsx-2307192908.number"
    }

    data = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        try:
            page.goto(TICKERTAPE_URL)
            time.sleep(10)

            from_val = page.locator(selectors['from_value']).inner_text()
            to_val = page.locator(selectors['to_value']).inner_text()
            percent = page.locator(selectors['percentage']).inner_text()

            data['extreme_greed_to_greed'] = f"Extreme Greed {from_val} ---> to Greed {to_val}"
            data['percentage'] = percent
            data['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f"[ERROR] TickerTape scrape failed: {e}")
            data['error'] = str(e)
        finally:
            browser.close()
    return data


def main():
    nifty_data = scrape_nifty_data()
    tickertape_data = scrape_tickertape_data()

    combined_data = {
        "spot": nifty_data.get("spot"),
        "maxpain": nifty_data.get("max_pain"),
        "pcr": nifty_data.get("pcr_all"),
        "calloi": nifty_data.get("calls_oi"),
        "putoi": nifty_data.get("puts_oi"),
        "vix": nifty_data.get("vix"),
        "marketmood": tickertape_data.get("extreme_greed_to_greed"),
        "mmipercentage": tickertape_data.get("percentage"),
        "lastupdated": tickertape_data.get("last_updated")
    }

    # 1. Dump data to console
    print("📦 Scraped Data Dump:")
    print(json.dumps(combined_data, indent=4))

    # 2. Send data to Apps Script
    try:
        response = requests.post(POST_URL, json=combined_data)
        if response.status_code == 200:
            print("✅ Success:", response.text)
        else:
            print("❌ Error:", response.status_code, response.text)
    except Exception as e:
        print("⚠️ An error occurred during POST:", str(e))


if __name__ == "__main__":
    main()

