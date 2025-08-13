from collections import OrderedDict
import pandas as pd
import logging
import json

import factors_statements as fs

logging.basicConfig(level=logging.INFO, filename=f"logs/factors_extraction.log", filemode='w',
                    format='%(levelname)s:%(message)s')


def factors_join(cik, raw_data, factor_keys, key_name):
    currency = "USD"
    factors = raw_data.get('us-gaap', raw_data.get('ifrs-full', {}))
    if not factors:
        raise KeyError(f"CIK{cik.zfill(10)} has no us-gaap or ifrs-full need to be check.")
    
    factors_df = pd.DataFrame(list(factors.keys()), columns=['factors'])
    have_factors = factors_df[factors_df['factors'].isin(factor_keys)]
    if have_factors.empty:
        return currency, {key_name : {}}
        # raise ValueError(f"CIK{cik.zfill(10)} does not have the factor keys needed.")

    frames = []
    for fact in have_factors['factors'].to_list():
        # Dynamically look what currency key this cik have.
        currency = list(factors[fact]['units'].keys())[0]
        records = factors[fact]['units'][currency]
        
        records_df = pd.DataFrame(records)
        # To catch if the cik file have missing key needed.
        try:
            # Filter out the data to get only that are 1 year apart.
            if  'start' in records_df.columns:
                records_df['start'] = pd.to_datetime(records_df['start'], errors='coerce') if 'start' in records_df.columns else pd.Series([pd.NaT] * len(records_df))
                records_df['end'] = pd.to_datetime(records_df['end'], errors='coerce')
                filtered_df = records_df[(records_df['end'] - records_df['start']).dt.days >= 360].copy()
                filtered_df = filtered_df.loc[filtered_df['form'].isin(['10-K', '20-F', '6-K'])]
            else:  # If the cik doesn't have 'start' date
                records_df['end'] = pd.to_datetime(records_df['end'], errors='coerce')
                filtered_df = records_df.loc[records_df['form'].isin(['10-K', '20-F', '6-K'])].copy()
            # Now removing some duplicates that are in the dataframe.
            filtered_df['end_year'] = pd.to_datetime(filtered_df['end']).dt.year
            annual_records = filtered_df.drop_duplicates(subset='end_year', keep='last')[::-1]
            frames.append(annual_records)
        except KeyError as e:
            missing_key = e.args[0]
            print(f"{cik.zfill(10)}-{key_name}-{fact}: Missing a key {missing_key}")
            continue    
    
    if not frames:
        return currency, {key_name : {}}
    # merging all the frames into 1 then remove duplicate.
    merged = pd.concat(frames, ignore_index=True)
    merged = merged.drop_duplicates(subset='end_year', keep='first')
    merged = merged.sort_values('end', ascending=False)  
    merged['end'] = merged['end'].dt.strftime('%Y-%m-%d')
    date_value = merged.set_index('end')['val'].to_dict()
    del factors_df, records_df, merged, frames      # clean up memory
    return currency, {key_name : date_value}


def exception_operate(key_name, statement):
    """"""
    detail = fs.factors_exception_calculate[key_name]
    new_value = {}
    new_value.update(statement[detail[1]])
    first_keys = statement[detail[1]].keys()
    arithmetic = lambda d, k, v: d.__setitem__(k, 0 if v == 0 else d[k] - v)  # default is minus
    if detail[0] == "add":
        arithmetic = lambda d, k, v: d.__setitem__(k, d[k] + v)  # change into add
    for var in detail[2:]:
        try:
            for k, (d, v) in zip(first_keys, statement[var].items()):
                if k == d:
                    arithmetic(new_value, k, v)
        except KeyError:
            continue
    
    return {key_name : new_value}


if __name__ == "__main__":
    print("Starting to grab all data needed for financial statement.")
    # Get all the ciks that are available to extract. close the file
    with open("resources/edgar_companyavailable.json", "r") as c:
        ciks = json.load(c)
    # Get the table template to put in data. close the file
    with open("resources/edgar_companytickers.json", "r") as t:
        template = json.load(t)

    for idx, data in enumerate(ciks.values()):
        cik = str(data['cik_str'])
        ticker = data['ticker']
        meta = template[ticker]
        print(f"({idx+1}.) Extracting ticker ({ticker}) financial data...")
        for state, facts in fs.factors_statements.items():
            statement = template[ticker]['statements'][state]
            # close the file.
            with open(f"resources/edgar_companyfacts/CIK{cik.zfill(10)}.json", "r") as f:
                raw_data = json.load(f)['facts']

            filler = {}
            max_dates = 0
            for fact, keys in facts.items():
                try:
                    currency, record = factors_join(cik, raw_data, keys, fact)
                    if not record[fact] and not fact in fs.factors_exception_calculate.keys():    # Log the CIK file that doesn't have factors are needed.
                        logging.error(f"{ticker}:{fact}:CIK_FILE: Couldn't find any data for this factor in the CIK file.")
                    if max_dates < len(record[fact]):
                        filler = {d: 0 for d in list(record[fact].keys())}
                        max_dates = len(record[fact])
                    meta['currency'] = currency
                    statement.update(record)
                except KeyError as e:    # Log the CIK file that doesn't have key of us-gaap or ifrs-full
                    logging.error(f"{ticker}:{str(e)}")
                    continue
            # Make the facts are equal lengths.
            for fact, values in statement.items():
                for date in filler:
                    values.setdefault(date, filler[date])
                statement[fact] = OrderedDict((d, values[d]) for d in filler)
            # Fill up values that can be calculated.
            count_zeros = lambda d: sum(v == 0 for v in d.values())
            for fact in facts:
                if count_zeros(statement[fact]) >= 5 and fact in fs.factors_exception_calculate:
                    record = exception_operate(fact, statement)
                    statement.update(record)
                    if count_zeros(record) >= 8:
                        logging.error(f"{ticker}:{fact}:CALCULATION: Couldn't find enough values for this factor even generating values for it.")

        print(f"Done extracting ticker ({ticker})\n")
        logging.info(f"{ticker}:{cik.zfill(10)}:Extraction complete!")
    # Update the template file.
    with open("resources/edgar_companytickers.json", "w") as f:
        json.dump(template, f, indent=2)
