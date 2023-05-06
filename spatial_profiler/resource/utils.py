import re
import json
from nltk import word_tokenize
from nltk import WordNetLemmatizer
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
import geopandas as gpd
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt
import contextily as ctx


__author__ = "Zhisheng Hua"
__copyright__ = "Copyright (C) 2023 TeamHoWan"
__version__ = "1.0"

def normalize_text(text):
    """normalize_text(text:string) -> list
    Input: original text String
    Output: list of normalized words
    """
    ps = PorterStemmer()
    text = re.sub("[^a-zA-Z]+", " ", text)
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word.isalpha()]
    tokens = [word.lower() for word in tokens]
    tokens = [word for word in tokens if not word in stopwords.words("english")]
    tokens = [ps.stem(word) for word in tokens]
    lemma = WordNetLemmatizer()
    tokens = [lemma.lemmatize(word) for word in tokens]
    return ' '.join(tokens)

def filter_int(values):
    count = 0
    num = 0
    for v in values.tolist():
        if str(v).strip():
            count += 1
        try:
            float(v)
            num += 1
        except:
            continue
    return num/count >= 0.8

def convert_to_float(x):
    try:
        return float(x)
    except:
        return 0.0
    
def create_map(long, lat):
    geometry = [Point(xy) for xy in zip(long, lat)]
    gdf = gpd.GeoDataFrame(geometry=geometry, crs='epsg:4326')
    boundary = gdf.geometry.unary_union.convex_hull
    gdf2 = gpd.GeoDataFrame(geometry=[boundary], crs=gdf.crs)
    fig, ax = plt.subplots(figsize=(12,15))
    ax = gdf2.plot(ax = ax, alpha = .3, marker = 'o', color='blue')
    gdf.plot(ax = ax, markersize = 30, label = 'Delhi', zorder = 3, alpha = .6, marker = 'o', color='blue')
    ctx.add_basemap(ax, crs=gdf2.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik, alpha = .9)
    plt.show()
    

def parse_json(input_dict):
    return json.dumps(input_dict)