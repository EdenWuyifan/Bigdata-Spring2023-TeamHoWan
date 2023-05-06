import datamart
import datamart_rest

"""
Auctus datamart REST API
Auctus
Everything related to auctus
"""

__author__ = "Eden Wu"
__copyright__ = "Copyright (C) 2023 TeamHoWan"
__version__ = "1.0"

class DataMartAPI():
    def __init__(self):
        self.client = datamart_rest.RESTDatamart('https://auctus.vida-nyu.org/api/v1')
        self.query = None
        self.cursor = None
        self.result = []
        
    def search(self, keywords="", variables=""):
        """make a datamart search
        Input:
            keyword: search keywords, seperate by comma, e.g. "new york,yellow taxi"]
            variables:
        
        Output:
            cursor
        """
        self.result = []
        self.query = datamart.DatamartQuery(
            keywords=[s.strip() for s in keywords.split(",")],
            variables=[s.strip() for s in variables.split(",")],
        )
        
        self.cursor = self.client.search(query=self.query)
        return self.cursor
    
    def next_page(self):
        if self.cursor is None:
            return
        page_data = self.cursor.get_next_page()
        if page_data:
            self.result.extend(page_data)
        return page_data
    
    def get_single_result(self, index):
        try:
            return self.result[index]
        except (IndexError, KeyError):
            print(f"Out of range, archived result: {len(self.result)}")
            return None
        
    def download_as_dataframe(self, single_data):
        downloaded_data = single_data.download(supplied_data=None)['learningData']
        column_names = [column['name'] for column in single_data.get_json_metadata()['metadata']['columns']]
        print(f"Name:\n {single_data.get_json_metadata()['metadata']['name']}\n==============================================================")
        if 'description' in single_data.get_json_metadata()['metadata']:
            print(f"Description: \n{single_data.get_json_metadata()['metadata']['description']}\n==============================================================")
        print(f"Column Names:\n{column_names}")
        return downloaded_data
    def get_column_names(self, single_data):
        return [column['name'] for column in single_data.get_json_metadata()['metadata']['columns']]
    
    def get_descriptions(self, single_data):
        metadata = single_data.get_json_metadata()['metadata']
        description = metadata['description'] if 'description' in metadata else ""
        return metadata['name']+". Description: " + description
    