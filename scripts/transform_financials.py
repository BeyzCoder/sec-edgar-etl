import pandas as pd
import json

import factors_statements as fs


def factors_join(cik, factor_keys, key_names):
    # Grab the json data then close the file.
    with open(f"resources/edgar_companyfacts/CIK{cik.zill(10)}.json", "r") as f:
        cik_data = json.load(f)['facts']
    
    if cik_data.get('us-gaap', {}):
        cik_data = cik_data['us-gaap']
    elif cik_data.get('ifrs-full', {}):
        cik_data = cik_data['ifrs-full']
    else:
        raise KeyError(f"CIK{cik.zill(10)} has no us-gaap or ifrs-full need to be check.")
    
    # Look at the cik file if it has the keys requirements.
    factors_df = pd.DataFrame(list(cik_data.keys()), columns=['factors'])
    factors = factors_df[factors_df['factors'].isin(factor_keys)]

    if factors.empty:
        raise ValueError(f"CIK{cik.zill(10)} does not have the factor keys needed.")
    
    frames = []
    for fact in factors['factors'].to_list():
        # Catch if the CIK is not a US stock.
        try:
            records = cik_data[fact]['units']['USD']
        except KeyError:
            first_key = list(cik_data[fact]['units'].keys())[0]
            records = cik_data[fact]['units'][first_key]
        
        records_df = pd.DataFrame(records)

        # Catch if the records doesn't have the standard keys needed.
        try:
            if 'start' in records.columns:
                records_df['start'] = pd.to_datetime(records_df['start'], errors='coerce') if 'start' in records_df.columns else pd.Series([pd.NaT] * len(records_df))
                records_df['end'] = pd.to_datetime(records_df['end'], errors='coerce')
                filtered_df = records_df[(records_df['end'] - records_df['start']).dt.days >= 360]
                filtered_df = filtered_df.loc[(filtered_df['form'] == '10-K')]
            else:
                records_df['end'] = pd.DataFrame(records_df['end'], errors='coerce')
                filtered_df = records_df[(records_df['form'] == '10-K')]

            filtered_df['end_year'] = pd.to_datetime(filtered_df['end']).dt.year
            annual_report = filtered_df.drop_duplicates(subset='end_year', keep='last')[::-1]
            frames.append(annual_report)
        except KeyError as e:
            missing_key = e.args[0]
            print(f"{cik.zfill(10)}-{key_names}-{fact}: Missing a key {missing_key}")
            continue

    # This step merge the frames into 1.
    if not frames:
        return {key_names : {}}
    
    merged = pd.concat(frames, ignore_index=True)
    merged = merged.drop_duplicates(subset='end_year', keep='first')
    merged['end'] = merged['end'].dt.strftime('%Y-%m-%d')
    data_values = merged.set_index('end')['val'].to_dict()
    return {key_names : data_values}

def exception_operate(key_name, statement):
    operation = fs.factors_exception_calculate[key_name]
    if operation[0] == 'add':
        new_value = {}
        new_value.update(statement[operation[1]])
        first_key = statement[operation[1]].keys()
        for var in operation[2:]:
            for k, v in zip(first_key, statement[var].values()):
                new_value[k] += v
    else:
        new_value = {}
        new_value.update(statement[operation[1]])
        first_key = statement[operation[1]].keys()
        for var in operation[2:]:
            for k, v in zip(first_key, statement[var].values()):
                new_value[k] -= v
    
    return {key_name : new_value}