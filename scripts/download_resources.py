import requests as req
import zipfile
import json
import os
import io
import sys

from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file


def download_edgar_folder(URL, filename):
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.sec.gov/",
    }
    res = req.get(os.getenv(URL), headers=HEADERS)
    if res.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(res.content)) as z:
            z.extractall(f"resources/edgar_{filename}")
            print("Folder download and extracted!")
    else:
        print("Failed to download the folder. Re-run the function, status code:", res.status_code)
        sys.exit()


def download_egdar_tickers(URL):
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": "https://www.sec.gov/",
    }
    res = req.get(os.getenv(URL), headers=HEADERS)
    if res.status_code == 200:
        tickers = res.json()
        with open(f"resources/listticker.json", "w") as f:
            json.dump(tickers, f, indent=4)
            print("File download complete!")
    else:
        print("Failed to download the file. Re-run the function, status code:", res.status_code)
        sys.exit()


def filter_empty_data():
    with open(f"resources/listticker.json", "r") as f:
        tickers = json.load(f)

        has_info = {}       # This is for ticker that has data available.
        cache = []          # This is for ticker that already been recorded. There are duplicates in json.
        idx = 0
        for val in tickers.values():
            cik_str = str(val["cik_str"]).zfill(10)
            cik_path = f"resources/edgar_companyfacts/CIK{cik_str}.json"
            # If there is no CIK**********.json file.
            if not os.path.exists(cik_path):
                print(f"[SKIP] No file found: {cik_str}")
                continue
            # If there is file but an empty file.
            if os.path.getsize(cik_path) < 60:
                print(f"[SKIP] File is empty: {cik_str}")
                continue
            # If the ticker is already recorded.
            if cik_str in cache:
                continue
            # Record ticker that has data.
            print(f"[ADD] has data: {cik_str}")
            has_info[str(idx)] = val
            cache.append(cik_str)
            idx += 1
    # Write new file for it.
    with open(f"resources/edgar_companyavailable.json", "w") as f:
        json.dump(has_info, f, indent=4)


def generate_template_ticker():
    with open(f"resources/edgar_companyavailable.json", "r") as f:
        tickers = json.load(f)

        company_tickers = {}        # This is the structure template for ticker json.
        for val in tickers.values():
            TEMPLATE_STATEMENT = {
                'income' : {
                    'TotalRevenue' : {},
                    'CostOfRevenue' : {},
                    'GrossProfit' : {},
                    'SellingGeneralAndAdministrative' : {},
                    'ResearchAndDevelopment' : {},
                    'OtherOperatingExpenses' : {},
                    'OperatingExpenses' : {},
                    'OperatingIncome' : {},
                    'OtherIncomeExpenses' : {},
                    'PreTaxIncome' : {},
                    'IncomeTax' : {},
                    'NetIncome' : {},
                },
                'balance' : {
                    'TotalAssets' : {},
                    'CurrentAssets' : {},
                    'CashAndCashEquivalent' : {},
                    'AccountReceivable' : {},
                    'Inventory' : {},
                    'AssetsNoncurrent' : {},
                    'NetPPE' : {},
                    'Goodwill' : {},
                    'OtherAssetsCurrent' : {},
                    'TotalLiabilities' : {},
                    'CurrentLiabilities' : {},
                    'AccountsPayable' : {},
                    'OtherCurrentLiabilities' : {},
                    'NonCurrentLiabilities' : {},
                    'LongTermDebt' : {},
                    'OtherNonCurrentLiabilities' : {},
                    'TotalEquity' : {},
                    'RetainedEarnings' : {},
                    'OtherComprehensiveIncome' : {},
                },
                'cash' : {
                    'OperatingCashFlow' : {},
                    'InvestingCashFlow' : {},
                    'FinancingCashFlow' : {},
                    'IncomeTaxPaidSupp' : {},
                    'CapitalExpenditure' : {},
                    'RepaymentDebt' : {},
                    'RepurchaseCapitalStock' : {},
                    'FreeCashFlow' : {},
                },
            }
            cik_str = str(val["cik_str"]).zfill(10)
            with open(f"resources/edgar_companysubmissions/CIK{cik_str}.json", "r") as f2:
                cik = json.load(f2)

                company_info = {}
                company_info['name'] = cik['name']
                company_info['ticker'] = val['ticker']
                if cik['ownerOrg'] != None:
                    company_info['sector'] = str(cik['ownerOrg'])[3:]
                else:
                    company_info['sector'] = None
                company_info['industry'] = cik['sicDescription']
                company_info['currency'] = None
                company_info['statements'] = TEMPLATE_STATEMENT

                company_tickers[val["ticker"]] = company_info

    with open(f"resources/edgar_companytickers.json", "w") as f:
        json.dump(company_tickers, f, indent=4)


if __name__ == "__main__":
    # These functions will only be running once.
    print("Grabbing all the resources needed for data extraction...")
    # edgar_companyfacts folder.
    download_edgar_folder("COMPANYFACTS_FOLDER_URL", "companyfacts")
    # edgar_companysubmissions folder.
    download_edgar_folder("SUBMISSIONS_FOLDER_URL", "companysubmissions")
    # edgar_companytickers json.
    download_egdar_tickers("TICKERS_LIST_URL")

    print("Cleaning up files and recording what company are availables...")
    # Creating a new list that only contains ticker that has CIK file.
    filter_empty_data()

    print("Making a template json for storing data...")
    # Creating a template json to store the actual data of ticker.
    generate_template_ticker()
