factors_exception_calculate = {
    # Income Statement
    "GrossProfit": ["minus", "TotalRevenue", "CostOfRevenue"],
    "OperatingIncome": ["minus", "GrossProfit", "OperatingExpenses"],
    "PreTaxIncome": ["add", "OperatingIncome", "OtherIncomeExpenses"],
    "NetIncome": ["minus", "PreTaxIncome", "IncomeTax"],

    # Balance Sheet
    # "TotalAssets": ["add", "TotalLiabilities", "TotalEquity"],
    "TotalLiabilities": ["minus", "TotalAssets", "TotalEquity"],
    "TotalEquity": ["minus", "TotalAssets", "TotalLiabilities"],
    "CurrentAssets": ["minus", "TotalAssets", "AssetsNoncurrent"],
    "CurrentLiabilities": ["minus", "TotalLiabilities", "NonCurrentLiabilities"],
    "NonCurrentLiabilities": ["minus", "TotalLiabilities", "CurrentLiabilities"],
    "AssetsNoncurrent": ["minus", "TotalAssets", "CurrentAssets"],
    
    # Cash Flow Statement
    "FreeCashFlow": ["minus", "OperatingCashFlow", "CapitalExpenditure"],
    "NetCashFlow": ["add", "OperatingCashFlow", "InvestingCashFlow", "FinancingCashFlow"],

    # Additional fallback options
    "OperatingExpenses": [
        "add",
        "SellingGeneralAndAdministrative",
        "ResearchAndDevelopment",
        "OtherOperatingExpenses"
    ],
    "RetainedEarnings": ["minus", "TotalEquity", "OtherComprehensiveIncome"]
}

factors_statements = {
    'income': {
        "TotalRevenue": [
            "Revenues",
            "SalesRevenueNet",
            "RevenueFromContractWithCustomerExcludingAssessedTax",
            "RevenueFromContractWithCustomerIncludingAssessedTax",
            "TotalRevenuesAndOtherIncome",
            "TotalRevenue",
            "SalesRevenueGoodsNet",
            "SalesRevenueServicesNet",
            "RevenuesNet",
            "SalesRevenue",
            "OperatingRevenue"
        ],
        "CostOfRevenue": [
            "CostOfRevenue",
            "CostOfGoodsAndServicesSold",
            "CostOfGoodsSold",
            "CostsAndExpenses"
        ],
        "GrossProfit": [
            "GrossProfit",
            "GrossProfitIncludingInterest",
            "GrossOperatingProfit",
            "GrossIncome"
        ],
        "SellingGeneralAndAdministrative": [
            "SellingGeneralAndAdministrativeExpense",
            "SellingAndMarketingExpense",
            "GeneralAndAdministrativeExpense"
        ],
        "ResearchAndDevelopment": ["ResearchAndDevelopmentExpense"],
        "OtherOperatingExpenses": ["OtherOperatingExpenses"],
        "OperatingExpenses": [
            "OperatingExpenses",
            "OperatingCostsAndExpenses",
            "OtherNonOperatingIncome",
            "OtherIncome"
        ],
        "OperatingIncome": ["OperatingIncomeLoss"],
        "OtherIncomeExpenses": [
            "OtherNonoperatingIncomeExpense",
            "NonoperatingIncomeExpense",
            "OtherIncomeExpenseNet",
            "InterestAndOtherIncome"
        ],
        "PreTaxIncome": [
            "IncomeLossBeforeIncomeTaxes",
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
            "IncomeLossFromContinuingOperationsBeforeIncomeTaxes",
            "EarningsBeforeTax",
            "PretaxIncome"
        ],
        "IncomeTax": ["IncomeTaxExpenseBenefit"],
        "NetIncome": [
            "NetIncomeLoss",
            "ProfitLoss",
            "NetIncomeLossAvailableToCommonStockholdersBasic",
            "EarningsNetOfTax"
        ]
    },
    'balance': {
        "TotalAssets": ["Assets", "AssetsNet"],
        "CurrentAssets": ["AssetsCurrent", "CurrentAssets", "AssetsCurrentNet"],
        "CashAndCashEquivalent": [
            "CashAndCashEquivalentsAtCarryingValue",
            "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"
        ],
        "AccountReceivable": ["AccountsReceivableNetCurrent", "AccountsReceivableNet"],
        "Inventory": ["InventoryNet", "InventoryFinishedGoodsNetOfReserves"],
        "AssetsNoncurrent": ["AssetsNoncurrent", "NoncurrentAssets"],
        "NetPPE": [
            "PropertyPlantAndEquipmentNet",
            "PropertyPlantAndEquipmentGross",
            "PropertyPlantEquipmentNet"
        ],
        "Goodwill": ["Goodwill", "GoodwillAndIntangibleAssetsNet"],
        "OtherAssetsCurrent": ["OtherAssetsCurrent", "PrepaidExpenseAndOtherAssetsCurrent"],
        "TotalLiabilities": [
            "Liabilities",
            "LiabilitiesAndStockholdersEquity",
            "LiabilitiesNet"
        ],
        "CurrentLiabilities": [
            "LiabilitiesCurrent",
            "CurrentLiabilities",
            "LiabilitiesCurrentNet"
        ],
        "AccountsPayable": [
            "AccountsPayableCurrent",
            "AccountsPayableAndAccruedLiabilitiesCurrent"
        ],
        "OtherCurrentLiabilities": [
            "OtherAccruedLiabilitiesCurrent",
            "OtherLiabilitiesCurrent"
        ],
        "NonCurrentLiabilities": ["LiabilitiesNoncurrent", "NoncurrentLiabilities"],
        "LongTermDebt": ["LongTermDebtNoncurrent", "LongTermDebt"],
        "OtherNonCurrentLiabilities": [
            "OtherAccruedLiabilitiesNoncurrent",
            "OtherLiabilitiesNoncurrent"
        ],
        "TotalEquity": [
            "StockholdersEquity",
            "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
        ],
        "RetainedEarnings": ["RetainedEarningsAccumulatedDeficit", "RetainedEarnings"],
        "OtherComprehensiveIncome": [
            "AccumulatedOtherComprehensiveIncomeLossNetOfTax",
            "AccumulatedOtherComprehensiveIncome"
        ]
    },
    'cash': {
        "OperatingCashFlow": [
            "NetCashProvidedByUsedInOperatingActivities",
            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations",
            "CashFlowFromOperatingActivities"
        ],
        "InvestingCashFlow": [
            "NetCashProvidedByUsedInInvestingActivities",
            "NetCashProvidedByUsedInInvestingActivitiesContinuingOperations"
        ],
        "FinancingCashFlow": [
            "NetCashProvidedByUsedInFinancingActivities",
            "NetCashProvidedByUsedInFinancingActivitiesContinuingOperations"
        ],
        "IncomeTaxPaidSupp": ["IncomeTaxesPaidNet", "IncomeTaxPaidSupplementalData"],
        "CapitalExpenditure": [
            "PaymentsToAcquirePropertyPlantAndEquipment",
            "CapitalExpenditures",
            "PurchaseOfPPE",
            "CapitalInvestment",
            "PaymentsToAcquireProductiveAssets"
        ],
        "RepaymentDebt": ["RepaymentsOfLongTermDebt", "RepaymentsOfDebt"],
        "RepurchaseCapitalStock": [
            "PaymentsForRepurchaseOfCommonStock",
            "PaymentsForRepurchaseOfEquity"
        ],
        "NetCashFlow": [],
        "FreeCashFlow": []  # No direct XBRL tag; typically calculated as OperatingCashFlow - CapitalExpenditure
    }
}
