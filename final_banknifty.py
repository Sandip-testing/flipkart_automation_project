from playwright.sync_api import sync_playwright, Page
from datetime import datetime
import requests
import json
import re
import time

# === Constants ===
EXPIRY_DATE_DISPLAY = "31-07-2025"
EXPIRY_DATE_API = "2025-07-31"
BASE_URL = "https://www.nseindia.com"
SPOT_SELECTOR = ("body > main:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(17) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > h3:nth-child(2)")


OPTION_BASE_URL = "https://www.nseindia.com/get-quotes/derivatives?symbol=BANKNIFTY&identifier=OPTIDXBANKNIFTY"

# Replace with actual selectors for IV and VWAP
SELECTORS = {
    "PE_IV": "body > div:nth-child(18) > div:nth-child(1) > div:nth-child(2) > section:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > table:nth-child(2) > tbody:nth-child(2) > tr:nth-child(2) > td:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(3) > div:nth-child(1) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(2) > tr:nth-child(3) > td:nth-child(2)",
    "PE_VWAP": "body > div:nth-child(18) > div:nth-child(1) > div:nth-child(2) > section:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > table:nth-child(2) > tbody:nth-child(2) > tr:nth-child(2) > td:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(2) > tr:nth-child(4) > td:nth-child(2)",
    "CE_IV": "body > div:nth-child(18) > div:nth-child(1) > div:nth-child(2) > section:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > table:nth-child(2) > tbody:nth-child(2) > tr:nth-child(2) > td:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(3) > div:nth-child(1) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(2) > tr:nth-child(3) > td:nth-child(2)",
    "CE_VWAP": "body > div:nth-child(18) > div:nth-child(1) > div:nth-child(2) > section:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > table:nth-child(2) > tbody:nth-child(2) > tr:nth-child(2) > td:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > table:nth-child(1) > tbody:nth-child(2) > tr:nth-child(4) > td:nth-child(2)"
}

# === Utility Functions ===

def extract_spot_value(page: Page):
    page.goto(BASE_URL, wait_until="networkidle", timeout=60000)
    page.wait_for_selector(SPOT_SELECTOR, timeout=60000)
    time.sleep(2)
    try:
        raw = page.inner_text(SPOT_SELECTOR).replace(",", "")
        match = re.search(r"([\d.]+)", raw)
        if match:
            original = float(match.group(1))
            rounded = round(original / 100) * 100
            return original, rounded + 500, rounded - 500
        return None, None, None
    except Exception as e:
        print(f"Error extracting spot value: {e}")
        return None, None, None

def get_iv_and_vwap(page: Page, url, iv_css, vwap_css):
    page.goto(url, wait_until="networkidle", timeout=60000)
    time.sleep(5)
    try:
        iv = page.locator(iv_css).first.text_content().strip()
        vwap = page.locator(vwap_css).first.text_content().strip().replace(",", "")
        return iv, vwap
    except Exception as e:
        print(f"Error extracting IV/VWAP: {e}")
        return None, None

def black_scholes(page: Page, spot, strike, expiry_date, volatility, is_put=True):
    try:
        page.goto("https://zerodha.com/tools/black-scholes/", wait_until="domcontentloaded", timeout=60000)
        time.sleep(1)
        page.fill("#input-spot", str(spot))
        page.fill("#input-strike", str(strike))
        page.fill("#datetimepicker", expiry_date + " 03:00:00")
        page.fill("#input-volt", str(volatility * 100))
        page.click("button:has-text('Calculate')")
        time.sleep(2)
        selector = "#put-option-prem-value" if is_put else "#call-option-prem-value"
        page.wait_for_selector(selector)
        return page.inner_text(selector).strip()
    except Exception as e:
        print(f"Black-Scholes error: {e}")
        return None

def send_data_to_google_script(data, label="CALL/PUT"):
    url = "https://script.google.com/macros/s/AKfycbxhmDTatzyH7_nRdKzvwcKwB0h90gS7D5ENkX8f9ZVEFx1MCF0hBUbX9mmkiw-sVOQ/exec"  # Replace with your URL
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            print(f"Success ({label}):", response.text)
        else:
            print(f"Error ({label}):", response.status_code, response.text)
    except requests.exceptions.RequestException as e:
        print(f"Request error ({label}): {e}")

def process_option(page: Page, instrument_type: str, strike: float, iv_css: str, vwap_css: str, is_put: bool):
    instrument_name = f"{EXPIRY_DATE_DISPLAY}{instrument_type}{int(strike)}.00"
    option_url = f"{OPTION_BASE_URL}{instrument_name}"
    iv_text, vwap_text = get_iv_and_vwap(page, option_url, iv_css, vwap_css)

    if not iv_text:
        print(f"{instrument_type} IV not found")
        return

    try:
        iv = float(iv_text) / 100.0
        premium = black_scholes(page, spot, strike, EXPIRY_DATE_API, iv, is_put=is_put)
    except Exception:
        premium = None

    data = {
        "spot": spot,
        "strike": strike,
        "instrument": instrument_name,
        "iv": iv_text,
        "vwap": vwap_text,
        "msp": premium,
        "lastupdated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    print(f"\nJSON Data ({instrument_type}):")
    print(json.dumps(data, indent=2))
    send_data_to_google_script(data, label=instrument_type)

# === Main Execution ===

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        context.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        })
        page = context.new_page()

        try:
            global spot, plus_500, minus_500
            spot, plus_500, minus_500 = extract_spot_value(page)
            if not all([spot, plus_500, minus_500]):
                print("Failed to fetch spot values.")
                return

            print(f"Spot: {spot}, spot + 500: {plus_500}, spot - 500: {minus_500}")

            # Process PUT (Spot +500)
            process_option(
                page, "PE", plus_500,
                SELECTORS["PE_IV"], SELECTORS["PE_VWAP"], is_put=True
            )

            # Process CALL (Spot -500)
            process_option(
                page, "CE", minus_500,
                SELECTORS["CE_IV"], SELECTORS["CE_VWAP"], is_put=False
            )

        finally:
            page.close()
            context.close()
            browser.close()

if __name__ == "__main__":
    main()
