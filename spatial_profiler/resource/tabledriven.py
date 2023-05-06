import re
import shapely.wkt
from .utils import convert_to_float

"""This is the Table-Driven method hub of spatial column profiling."""

__author__ = "Eden Wu, Yuqian Li, Zhisheng Hua"
__copyright__ = "Copyright (C) 2023 TeamHoWan"
__version__ = "1.0"



"""=======================================
|                                        |
|            Column Parsers              |
|                                        |
======================================="""

def parser_address(cell):
    cell_remove_empty = [x.strip() for x in cell.split(',') if x.strip()]
    return (', ').join(cell_remove_empty)


def parser_zipcode(zipcode):
    """check if it's a valid zipcode here.
    A valid US zipcode generally has a 5-digit format or a 9-digit format separated by a hyphen (e.g., 12345 or 12345-6789)
    """
    pattern = re.compile(r'^\d{5}(-\d{4})?$')
    if pattern.match(str(zipcode)):
        return str(zipcode)
    else:
        return None

def parser_longitude(long):
    """cheche a valid longitude here, the range is [-180,180]"""
    try:
        long = float(long)
        if -180 <= long <= 180:
            return long
        else:
            return None
    except ValueError:
        return None

def parser_latitude(lat):
    """cheche a valid latitude here, the range is [-90,90]"""
    try:
        lat = float(lat)
        if -90 <= lat <= 90:
            return lat
        else:
            return None
    except ValueError:
        return None

def parser_geojson(geo):
    try:
        data = shapely.wkt.loads(geo)
        
        if data.geom_type == 'Point':
            return (data.x, data.y)
        elif (data.geom_type == 'Polygon' or data.geom_type == 'LineString' or data.geom_type == 'MultiPoint' or data.geom_type == 'MultiLineString' or data.geom_type == 'MultiPolygon'):
            #return data.representative_point()
            return (data.centroid.x, data.centroid.y)
    except:
        return None   

def parser_default(dump):
    return ""


def check_in_sp_range(cor, limit):
    return cor >= limit[0] and cor <= limit[1]

def sample_check_sp_restrain_longlat(column, sp_restrain):
    sample_len = 50
    if len(column) < 50:
        sample_len = len(column)
    samples = column.sample(n = sample_len)
    total = samples.apply(lambda x: check_in_sp_range(x, sp_restrain)).sum(axis = 0)
    return total/sample_len >= 0.8

def sp_parse_longlat(cor, sp_restrain):
    if check_in_sp_range(cor, sp_restrain):
        return cor
    else:
        print("Dump invalid value!")
        return None

"""=======================================
|                                        |
|       Parser Check Up Table            |
|                                        |
======================================="""


DATATYPE_PARSER_TABLE = {
    'address': parser_address,
    'zipcode': parser_zipcode,
    'longitude': parser_longitude,
    'latitude': parser_latitude,
    'geojson': parser_geojson,
    # Add the new parser here

    'default': parser_default,
}

SP_RESTRAIN = None

def parse_col(column_name, column, sp_restrain=None):
    """Column parse
    Matching the cleaned column name with the parser function registered.
    If do not have a parser function, ignore it.
    """
    try:
        parser = DATATYPE_PARSER_TABLE[column_name]
    except (KeyError, IndexError):
        parser = DATATYPE_PARSER_TABLE['default']
        
    # convert longlat to float
    if column_name == 'longitude' or column_name == 'latitude':
        column = column.apply(lambda x: convert_to_float(x))
        
    # Semantic Processor checking and dumping invalid values
    if sp_restrain is not None:
        lat_strain = (sp_restrain.bbox['southwest'][0], sp_restrain.bbox['northeast'][0])
        long_strain = (sp_restrain.bbox['southwest'][1], sp_restrain.bbox['northeast'][1])
        if column_name == 'longitude' and sample_check_sp_restrain_longlat(column, long_strain):
            column = column.apply(lambda x: sp_parse_longlat(x, long_strain))
        elif column_name == 'latitude' and sample_check_sp_restrain_longlat(column, lat_strain):
            column = column.apply(lambda x: sp_parse_longlat(x, lat_strain))
            
    return column.apply(lambda x: parser(x))