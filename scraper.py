import json
import time
import os
import requests
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from fyers_apiv3 import fyersModel

# Configuration
JSON_FILE = "program_triggered_at.json"
GAP_BW_TWO_RUNS = 75 # minutes
START = "09:15:00"
END = "15:30:00"

def gatekeeper(file_path, start_time_str, end_time_str, log_format="%d-%m-%Y %H:%M:%S"):
    """
    A wrapper generator that forces all checks into Indian Standard Time (IST).
    Accepts daily operational windows in "H:M:S" format and blocks execution on weekends.
    """
    def decorator(foo):
        def wrapper(*args, **kwargs):
            ist_tz = ZoneInfo("Asia/Kolkata")
            current_time = datetime.now(ist_tz)
            
            # 1. Weekend Check (Saturday = 5, Sunday = 6)
            if current_time.weekday() in (5, 6):
                print(f"Skipping execution: Today is {current_time.strftime('%A')} (Weekend) in IST.")
                return None

            # 2. Parse operational daily window (H:M:S)
            try:
                start_window = datetime.strptime(start_time_str, "%H:%M:%S").time()
                end_window = datetime.strptime(end_time_str, "%H:%M:%S").time()
            except ValueError as e:
                print(f"Error parsing start/end window strings (must be H:M:S): {e}")
                return None

            # Check if the current time falls inside the daily window
            current_clock_time = current_time.time()
            if not (start_window <= current_clock_time <= end_window):
                print(f"Skipping execution: {current_clock_time.strftime('%H:%M:%S')} IST is outside the allowed window ({start_time_str} - {end_time_str}).")
                return None

            # 3. Load the JSON tracking file
            data = {"timestamps": []}
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)
                except json.JSONDecodeError:
                    print("Warning: Corrupted JSON file. Starting fresh.")

            timestamps = data.get("timestamps", [])

            # 4. Check the 15-minute cool-down constraint
            if timestamps:
                try:
                    last_trigger_time = datetime.strptime(timestamps[-1], log_format).replace(tzinfo=ist_tz)
                    
                    if (current_time - last_trigger_time) <= timedelta(minutes=GAP_BW_TWO_RUNS):
                        print(f"Skipping execution: Less than {GAP_BW_TWO_RUNS} minutes have passed since the last run.")
                        return None
                except ValueError:
                    print("Warning: Could not parse the last timestamp log. Proceeding with execution.")

            # 5. Conditions met -> Trigger foo()
            print("Conditions met. Executing function...")
            result = foo(*args, **kwargs)

            # 6. Append current time and save back to file
            current_time_str = current_time.strftime(log_format)
            timestamps.append(current_time_str)
            data["timestamps"] = timestamps

            with open(file_path, "w") as f:
                json.dump(data, f, indent=4)

            return result
        return wrapper
    return decorator

# Complete watchlist provided
# Copy past the list from https://www.nseindia.com/products-services/equity-derivatives-list-underlyings-information by the following js
# symbols=[];$0.querySelectorAll('td:nth-child(3)').forEach(symbol => symbols.push(symbol.textContent));copy(symbols);
watchlist = [
    "360ONE", "ABB", "APLAPOLLO", "AUBANK", "ADANIENSOL", "ADANIENT", "ADANIGREEN",
    "ADANIPORTS", "ADANIPOWER", "ABCAPITAL", "ALKEM", "AMBER", "AMBUJACEM",
    "ANGELONE", "APOLLOHOSP", "ASHOKLEY", "ASIANPAINT", "ASTRAL", "AUROPHARMA",
    "DMART", "AXISBANK", "BSE", "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV",
    "BAJAJHLDNG", "BANDHANBNK", "BANKBARODA", "BANKINDIA", "BDL", "BEL",
    "BHARATFORG", "BHEL", "BPCL", "BHARTIARTL", "BIOCON", "BLUESTARCO", "BOSCHLTD",
    "BRITANNIA", "CGPOWER", "CANBK", "CDSL", "CHOLAFIN", "CIPLA", "COALINDIA",
    "COCHINSHIP", "COFORGE", "COLPAL", "CAMS", "CONCOR", "CROMPTON",
    "CUMMINSIND", "DLF", "DABUR", "DALBHARAT", "DELHIVERY", "DIVISLAB",
    "DIXON", "DRREDDY", "ETERNAL", "EICHERMOT", "EXIDEIND", "FORCEMOT",
    "NYKAA", "FORTIS", "GAIL", "GMRAIRPORT", "GLENMARK", "GODFRYPHLP",
    "GODREJCP", "GODREJPROP", "GRASIM", "HCLTECH", "HDFCAMC", "HDFCBANK",
    "HDFCLIFE", "HAVELLS", "HEROMOTOCO", "HINDALCO", "HAL", "HINDPETRO",
    "HINDUNILVR", "HINDZINC", "POWERINDIA", "HYUNDAI", "ICICIBANK", "ICICIGI",
    "ICICIPRULI", "IDFCFIRSTB", "ITC", "INDIANB", "IEX", "IOC", "IRFC", "IREDA",
    "INDUSTOWER", "INDUSINDBK", "NAUKRI", "INFY", "INOXWIND", "INDIGO",
    "JINDALSTEL", "JSWENERGY", "JSWSTEEL", "JIOFIN", "JUBLFOOD", "KEI",
    "KPITTECH", "KALYANKJIL", "KAYNES", "KFINTECH", "KOTAKBANK", "LTF",
    "LICHSGFIN", "LTM", "LT", "LAURUSLABS", "LICI", "LODHA", "LUPIN", "M&M",
    "MANAPPURAM", "MANKIND", "MARICO", "MARUTI", "MFSL", "MAXHEALTH", "MAZDOCK",
    "MOTILALOFS", "MPHASIS", "MCX", "MUTHOOTFIN", "NBCC", "NHPC", "NMDC",
    "NTPC", "NATIONALUM", "NESTLEIND", "NAM-INDIA", "NUVAMA", "OBEROIRLTY",
    "ONGC", "OIL", "PAYTM", "OFSS", "POLICYBZR", "PGEL", "PIIND", "PNBHOUSING",
    "PAGEIND", "PATANJALI", "PERSISTENT", "PETRONET", "PIDILITIND", "POLYCAB",
    "PFC", "POWERGRID", "PREMIERENE", "PRESTIGE", "PNB", "RBLBANK", "RECLTD",
    "RVNL", "RELIANCE", "SBICARD", "SBILIFE", "SHREECEM", "SRF", "SAMMAANCAP",
    "MOTHERSON", "SHRIRAMFIN", "SIEMENS", "SOLARINDS", "SONACOMS", "SBIN",
    "SAIL", "SUNPHARMA", "SUPREMEIND", "SUZLON", "SWIGGY", "TATACONSUM",
    "TVSMOTOR", "TCS", "TATAELXSI", "TMPV", "TATAPOWER", "TATASTEEL", "TECHM",
    "FEDERALBNK", "INDHOTEL", "PHOENIXLTD", "TITAN", "TORNTPHARM", "TRENT",
    "TIINDIA", "UNOMINDA", "UPL", "ULTRACEMCO", "UNIONBANK", "UNITDSPR", "VBL",
    "VEDL", "VMM", "IDEA", "VOLTAS", "WAAREEENER", "WIPRO", "YESBANK", "ZYDUSLIFE"
]

# Fetch access token from your PythonAnywhere app
try:
    res = requests.get('https://wigaq.pythonanywhere.com/fretrieve', timeout=15)
    access_token = res.text.strip()
    if len(access_token) < 10:  # Basic sanity check for token length
        raise ValueError("Received access token is too short, likely invalid.")
except Exception as e:
    print(f"Failed to fetch Access Token from server: {e}")
    exit(1)

# Initialize Fyers API client
fyers = fyersModel.FyersModel(client_id='VH3GG57J9Y-100', is_async=False, token=access_token, log_path="")

def get_response(symbol, timestamp=''):
    data = {
        "symbol": f"NSE:{symbol}-EQ",
        "strikecount": 50,
        "timestamp": timestamp,
        "greeks": "1"
    }
    return fyers.optionchain(data=data)

def get_data_for_symbol(symbol):
    expiry0_data = get_response(symbol)
    expiryData = expiry0_data.get('data', {}).get('expiryData', {})
    
    if not expiryData or len(expiryData) < 3:
        raise ValueError(f"Insufficient expiry data returned for {symbol}")

    expiry1_data = get_response(symbol, expiryData[1].get('expiry'))
    expiry2_data = get_response(symbol, expiryData[2].get('expiry'))

    # Strict IST timezone timestamping
    IST = timezone(timedelta(hours=5, minutes=30))
    current_time = datetime.now(IST).strftime("%d-%m-%Y-%H-%M-%S")

    return {
        current_time: {
            expiryData[0].get('expiry'): expiry0_data,
            expiryData[1].get('expiry'): expiry1_data,
            expiryData[2].get('expiry'): expiry2_data
        }
    }

@gatekeeper(JSON_FILE, START, END)
def get_data_for_watchlist():
    last_request_sent_on = time.perf_counter()
    os.makedirs('data', exist_ok=True)

    for symbol in watchlist:
        # Enforce minimum 1 second rate limit window between loops
        while (time.perf_counter() - last_request_sent_on) <= 1.0:
            continue

        retry_count = 5
        data = None
        
        while retry_count > 0:
            try:
                data = get_data_for_symbol(symbol)
                last_request_sent_on = time.perf_counter()
                break
            except Exception as e:
                print("\tError at {}: {}".format(symbol, e))
                retry_count -= 1
                time.sleep(0.5)  # Quick pause before retry

        if retry_count == 0 or data is None:
            print(f"❌ Failed to get data for {symbol} after 5 attempts.")
            continue

        # Load existing JSON file data or initialize empty dictionary
        file_path = f'data/{symbol}.json'
        existing_data = {}
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    existing_data = json.load(f)
            except Exception:
                existing_data = {}

        # Append new timestamp data block and write back
        existing_data.update(data)
        with open(file_path, 'w') as f:
            json.dump(existing_data, f, indent=2)
            
        print(f"✅ {symbol} data successfully collected.")

if __name__ == "__main__":
    get_data_for_watchlist()
