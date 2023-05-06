from datamart_profiler.core import process_dataset
import datamart_rest

from fuzzywuzzy import fuzz
from itertools import product
import pandas as pd

from .datamart_API import DataMartAPI
from .utils import normalize_text, filter_int, parse_json
from .tabledriven import parse_col
from .geoconcat import GeoConcat

__author__ = "Eden Wu, Zhisheng Hua, Yuqian Li"
__copyright__ = "Copyright (C) 2023 TeamHoWan"
__version__ = "1.0"

class SpatialProfiler():
    def __init__(self, geo_key):
        # Hard-coded filters for column names
        self.column_keywords = ['addr', 'address', 'area', 'bbl', 'bin', 'block', 'board', 'borocod', 'borough', 'build', 'citi', 'compani', 'council', 'counti',  'cross', 'district', 'intersect', 'locat', 'neighborhood', 'nta', 'place', 'post', 'postal','region', 'site', 'state', 'statepl', 'street', 'tract', 'zip']
        # Add filters for longitude&latitude using keywords from Auctus(Optional: find columns that match apart from latitude and longitude keywords)
        self.column_keywords.extend(['lat', 'latitud','ycoord'])
        self.column_keywords.extend(['lng', 'lon', 'long', 'longitud', 'xcoord'])
        self.column_keywords.extend(['geo', 'point', 'linestring', 'polygon', 'multipoint', 'multilinestring', 'multipolygon', 'multi'])
    
        self.fuzz_rename = {
            "address": ['addr', 'address', 'area', 'bbl', 'bin', 'block', 'board', 'borocod', 'borough', 'build', 'citi', 'compani','council', 'counti', 'cross', 'district', 'intersect', 'locat', 'neighborhood', 'nta', 'place','region', 'site', 'state', 'statepl', 'street', 'tract'],
            "latitude": ['lat', 'latitud','ycoord'],
            "longitude": ['lng', 'lon', 'long', 'longitud', 'xcoord'],
            "zipcode": ['post', 'postal','site', 'zip'],
            "geojson": ['geo', 'point', 'linestring', 'polygon', 'multipoint', 'multilinestring', 'multipolygon', 'multi'],
        }
        
        self.datamart = DataMartAPI()
        self.geoconcat = GeoConcat(geo_key)
        self.uscity = pd.read_csv('../resource/uscities_selected.csv')
        self.json = {}
    
    
    def profiling(self, df, datamart_url: datamart_rest.rest.RESTSearchResult):
        """TBD
        Here feed this function a dataframe, 
        it will append the dataframe with a new column with our format.
        e.g.
        ------------------    -----------------===========
        | Zipcode | City |    | Zipcode | City | THW_loc |
        ------------------ => -----------------===========
        | 11111   | PA   |    | 11111   | PA   | XXXXXXX |
        ------------------    -----------------===========
        
        Input: 
            datamart_url: datamart_rest.rest.RESTSearchResult object
        """
        self.json = {}
        
        # ==================================
        # Semantic Processor: information extraction from datasets
        # ==================================
        description = self.datamart.get_descriptions(datamart_url)
        if description:
            sp_restrain = self.geoconcat.read_address(description)
        if sp_restrain is None:
            print("[Semantic Processor] Cannot get helpful info out of descriptions!")
            self.json["sp_restrain"] = []
        else:
            self.json["sp_restrain"] = sp_restrain.geojson
        
        # !!!TBR!!!
        self.json["nb_rows"] = df.shape[0]
        
        # ==================================
        # Fuzzy Filter: column formatter
        # ==================================
        candidate_columns = self.get_candidate_columns(list(df.columns))
        exclude_columns = [col for col in df.columns if col not in candidate_columns]
        df_sample = df.sample(n = 50) if df.shape[0] > 50 else df
        sample_candidate_columns = self.get_candidate_from_sample(df_sample, exclude_columns)
        candidate_columns.update(sample_candidate_columns)
        self.json["candidate_columns"] = candidate_columns
        
        
        # ==================================
        # Ad Hoc Parser: Parse each column
        # ==================================
        df[f"TeamHoWan_address"] = ""
        for column_name, matching_parser_keys in candidate_columns.items():
            for key in matching_parser_keys:
                if key == "address":
                    if not filter_int(df_sample[column_name].values):
                        df[f"TeamHoWan_address"] = df[f"TeamHoWan_address"] + ', ' + df[column_name]
                else:
                    df[f"TeamHoWan_{column_name}_{key}"] = df[column_name]
                    df[f"TeamHoWan_{column_name}_{key}"] = parse_col(key, df[f"TeamHoWan_{column_name}_{key}"], sp_restrain)
        
        df[f"TeamHoWan_address"] = parse_col('address', df[f"TeamHoWan_address"])
        
        # ==================================
        # Geo Concat
        # ==================================
        df['THW_loc'] = self.assemble_parsed_columns(df)
        df['THW_loc'] = df['THW_loc'].apply(lambda x: self.geoconcat.geocoding(x))
        # Geo Concat
        df['thw_parsed_long'] = df['THW_loc'].apply(lambda x: x[0] if x is not None else None)
        df['thw_parsed_lat'] = df['THW_loc'].apply(lambda x: x[1] if x is not None else None)
        
        return df, parse_json(self.json)
    
    def get_fuzz_score(self, str1, str2):
        """
        get_fuzz_score(str1:string, str2:string) -> float
        Input: two strings
        Output: the ratio of the most similar substring
        """
        ratio = fuzz.partial_ratio(str1, str2)
        return ratio
    
    def get_candidate_columns(self, column_names):
        """
        get_candidate_columns(column_names:list) -> list
        Input: original column names
        Output: candidate column names
        first from tokens, second from column_keywords
        """
        rename_dict = {}
        for i in range(len(column_names)):
            normalized_name = normalize_text(column_names[i])
            matched_keyword = set()
            for keyword in self.column_keywords:
                if self.get_fuzz_score(keyword, normalized_name) > 80:
                    matched_keyword.add(self.get_fuzz_rename(keyword))
            if len(matched_keyword) > 0: # candidate column
                rename_dict[column_names[i]] = list(matched_keyword)
        return rename_dict
        
    
    def get_fuzz_rename(self, fuzz_matched_keyword):
        """Input: fuzz matched keyword
        Output: the key of fuzz_rename. a.k.a formatted name
        """
        for rename, keywords in self.fuzz_rename.items():
            if fuzz_matched_keyword in keywords:
                return rename
            
    def is_state_city(self, val):
    #     State Name, e.g. New York, City Name, e.g. Bayamón / Bayamon, & County Name, e.g. Kings for Brooklyn
        return val in self.uscity['state_name'].values or val in self.uscity['city'].values or val in self.uscity['city_ascii'].values or val in self.uscity['county_name'].values

    def is_state_abb(self, val):
    #     State Abbreviation, e.g. NY
        return val in self.uscity['state_id'].values

    def is_county_fips(self, val):
    #     The 5-digit FIPS code for the primary county, the first two digits correspond to the state's FIPS code.
        return val in self.uscity['county_fips'].values
    
    def get_candidate_from_sample(self, df, column_names):
        column_dict = {}
        num_sample = df.shape[0]
        for column in column_names:
            is_state_city_total = df[column].apply(lambda x: self.is_state_city(x)).sum(axis = 0)
            is_state_abb_total = df[column].apply(lambda x: self.is_state_abb(x)).sum(axis = 0)
            # is_county_fips_total = df[column].apply(lambda x: self.is_county_fips(x)).sum(axis = 0)
            if (is_state_city_total / num_sample >= 0.8) or (is_state_abb_total / num_sample >= 0.8):
                column_dict[column] = ['address']
            # else if(is_county_fips_total/ num_sample >= 0.8):
            #     column_dict[column] = ['address']
        return column_dict
            
            
    def assemble_single_row(self, row):
        """Single row logic:
        if higher priority exist, neglect lower priorities
        """
        
        # 1. check lat long
        if row.filter(regex="_longitude$").shape[0] and  row.filter(regex="_latitude$").shape[0]:
            lat = row.filter(regex="_latitude$").values[0]
            long = row.filter(regex="_longitude$").values[0]
            if not pd.isna(lat) and not pd.isna(long):
                return f"{lat}, {long}"
        
        # 2. check geo
        if row.filter(regex="_geojson$").shape[0]:
            geo = row.filter(regex="_geojson$").values[0]
            if not pd.isna(geo):
                return f"{geo[1]}, {geo[0]}"
        
        # 3. check postal
        if row.filter(regex="_zipcode$").shape[0]:
            zipcode = row.filter(regex="_zipcode$").values[0]
            if not pd.isna(zipcode):
                return zipcode
        
        # address
        return row["TeamHoWan_address"]
            
    def assemble_parsed_columns(self, df):
        return df.apply(self.assemble_single_row, axis = 1)
        
    
        