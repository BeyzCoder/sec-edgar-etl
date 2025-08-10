import pandas as pd
import json

import factors_statements as fs


def factors_join(cik, raw_data, factor_keys, key_name):
    currency = "USD"
    factors = raw_data.get('us-gaap', raw_data.get('ifrs-full', {}))
    if not factors:
        raise KeyError(f"CIK{cik.zill(10)} has no us-gaap or ifrs-full need to be check.")
    
    factors_df = pd.DataFrame(list(raw_data.keys()), columns=['factors'])
    have_factors = factors_df[factors_df['factors'].isin(factor_keys)]
    if have_factors.empty:
        raise ValueError(f"CIK{cik.zill(10)} does not have the factor keys needed.")

    frames = []
    for fact in have_factors['factors'].to_list():
        # Dynamically look what currency key this cik have.
        try:
            records = factors[fact]['units'][currency]
        except KeyError:
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
                filtered_df = filtered_df.loc[(filtered_df['form'] == '10-K')]
            else:  # If the cik doesn't have 'start' date
                records_df['end'] = pd.to_datetime(records_df['end'], errors='coerce')
                filtered_df = records_df.loc[(records_df['form'] == '10-K')]
            # Now removing some duplicates that are in the dataframe.
            filtered_df['end_year'] = pd.to_datetime(filtered_df['end']).dt.year
            annual_records = filtered_df.drop_duplicates(subset='end_year', keep='last')[::-1]
            frames.append(annual_records)
        except KeyError as e:
            missing_key = e.args[0]
            print(f"{cik.zfill(10)}-{key_names}-{fact}: Missing a key {missing_key}")
            continue
    
    if not frames:
        return currency, {key_name : {}}
    # merging all the frames into 1 then remove duplicate.
    merged = pd.concat(frames, ignore_index=True)
    merged = merged.drop_duplicates(subset='end_year', keep='first')
    merged = merged.sort_values('end', ascending=False)  
    merged['end'] = merged['end'].dt.strftime('%Y-%m-%d')
    date_value = merged.set_index('end')['val'].to_dict()
    del df, merged, frames      # clean up memory
    return currency, {key_name : date_value}


def exception_operate(key_name, statement):
    """"""
    detail = fs.factors_exception_calculate[key_name]
    if detail[0] == "add":
        new_value = {}
        new_value.update(statement[detail[1]])
        first_keys = statement[detail[1]].keys()
        for var in detail[2:]:
            try:
                for k, v in zip(first_keys, statement[var].values()):
                    new_value[k] += v
            except KeyError:
                continue
        
        return {key_name : new_value}

    else:
        new_value = {}
        new_value.update(statement[detail[1]])
        first_keys = statement[detail[1]].keys()
        for var in detail[2:]:
            try:
                for k, v in zip(first_keys, statement[var].values()):
                    new_value[k] -= v
            except KeyError:
                continue
        
        return {key_name : new_value}

