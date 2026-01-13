from playwright.sync_api import sync_playwright
import time
import json
from datetime import datetime
import requests

# URLs
NIFTY_URL = "https://www.niftytrader.in/live-nifty-open-interest"
TICKERTAPE_URL = "https://www.tickertape.in/market-mood-index"
POST_URL = "https://script.google.com/macros/s/AKfycbzBghC_r5iUsnk1zh_X6KZE3adsNDHDZo6128rH-Hay-CakEPdm_FSUQtkSc4aS-rU/exec"

# Scrape BANKNIFTY data by selecting it from dropdown
def scrape_banknifty_data_via_dropdown():
    selectors = {
        'spot': "div[class='justify-content-lg-start justify-content-center flex-column spot_price_value spot_price_val d-none d-sm-flex'] span[class='spot_price fw-600 fs-16']",
        'max_pain': "body > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(5) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(3) > ul:nth-child(1) > li:nth-child(3) > p:nth-child(2)",
        'pcr_all': "body > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(5) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(3) > ul:nth-child(1) > li:nth-child(10) > p:nth-child(2)",
        'calls_oi': "body > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(5) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > ul:nth-child(1) > li:nth-child(1) > span:nth-child(2)",
        'puts_oi': "body > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(5) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > ul:nth-child(1) > li:nth-child(2) > span:nth-child(2)"
    }

    data = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        try:
            page.goto(NIFTY_URL)
            page.wait_for_timeout(12000)

            # Click dropdown and select BANKNIFTY
            page.locator("//button[@id='dropdown-basic']").click() 
            page.locator("text=BANKNIFTY").click()
            page.wait_for_timeout(3000)

            data['spot'] = page.locator(selectors['spot']).inner_text()
            data['max_pain'] = page.locator(selectors['max_pain']).inner_text()
            data['pcr_all'] = page.locator(selectors['pcr_all']).inner_text()
            data['calls_oi'] = page.locator(selectors['calls_oi']).inner_text().replace("Calls OI", "").strip()
            data['puts_oi'] = page.locator(selectors['puts_oi']).inner_text().replace("Puts OI", "").strip()

            # Attempt to retrieve VIX from green or red class
            try:
                vix_element = page.locator(".fs-13.mb-0.text-green")
                if not vix_element.count():
                    vix_element = page.locator(".fs-13.mb-0.text-red")
                data['vix'] = vix_element.inner_text()
            except Exception as ve:
                print(f"[WARNING] Failed to fetch VIX: {ve}")
                data['vix'] = "N/A"

            data['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            print(f"[ERROR] Failed to scrape BANKNIFTY via dropdown: {e}")
            data['error'] = str(e)
        finally:
            browser.close()
    return data

# Scrape market mood index from Tickertape
def scrape_tickertape_data():
    selectors = {
        'from_value': "div[class='jsx-3769769187 from'] p[class='jsx-3769769187 value typography-body-regular-xs text-teritiary pt8 lh-100']",
        'to_value': "div[class='jsx-3769769187 to'] p[class='jsx-3769769187 value typography-body-regular-xs text-teritiary pt8 lh-100']",
        'percentage': ".jsx-3654585993.jsx-2059427245.number"
    }

    data = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        try:
            page.goto(TICKERTAPE_URL)
            time.sleep(7)

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

# Main function
def main():
    banknifty_data = scrape_banknifty_data_via_dropdown()
    tickertape_data = scrape_tickertape_data()

    combined_data = {
        "spot": banknifty_data.get("spot"),
        "maxpain": banknifty_data.get("max_pain"),
        "pcr": banknifty_data.get("pcr_all"),
        "calloi": banknifty_data.get("calls_oi"),
        "putoi": banknifty_data.get("puts_oi"),
        "vix": banknifty_data.get("vix"),
        "marketmood": tickertape_data.get("extreme_greed_to_greed"),
        "mmipercentage": tickertape_data.get("percentage"),
        "lastupdated": tickertape_data.get("last_updated")
    }

    # Step 1: Dump data to console
    print("📦 Scraped BANKNIFTY + Market Mood Data:")
    print(json.dumps(combined_data, indent=4))

    # Step 2: Post to Google Script
    try:
        response = requests.post(POST_URL, json=combined_data)
        if response.status_code == 200:
            print("✅ Data posted successfully!")
        else:
            print(f"❌ Failed to post data: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"⚠️ POST request failed: {e}")

if __name__ == "__main__":
    main()



