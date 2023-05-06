# THW Spatial Profiler - A Modular Spatial Profiler Using Fuzzy Matching And Natural Language Processing
[![Python Version](https://img.shields.io/badge/python-3.7-brightgreen.svg)](https://python.org)

## Introduction

This application addresses the challenge of insufficient metadata in open datasets by profiling them and identifying their spatial attributes. We employ data profiling strategies to recognize and extract spatial information, including address, geographic coordinates, administrative divisions, postal information, and geometric objects. By converting these attributes into a unified format, we enhance the usability and availability of open data. Furthermore, it holds promising potential for future applications in both merchandising and research fields.



## Terminologies
  
Terminology | Abbreviation | Notes
-- | -- | --
Original Dataset | dataset | NA
Fuzzy Filter | fuzzy | NA
Column Parser | parser | Parser for each filtered column
Address | address | State City Street Borough, etc.
Zipcode | zip | Zip, Postal
Geometric Object | geo/geometry | Point, Polygon, etc.
Semantic Processor | SP | ChatGPT information extraction from datasets
Geocoding Concatenator | GeoConcat | Concat a standardized geo column to the dataset
Auctus datamart REST API | Auctus | Everything related to auctus


## Application Topology
  
```mermaid
flowchart TB
	db[(dataset)]
	dbnew[(parsed dataset)]
	dbfin[(profiled dataset)]
	fuzzy{Fuzzy Filter}
	sample{Sampling Filter}
	semen{Sementic Processor}
	long{Longitude Parser}
	lat{Latitude Parser}
	zip{Zipcode Parser}
	geo{Geo Parser}
	addr{Address Parser}
	stash[Stash]
	concat{Geocoding Concatenator}
	json[[Json Profile]]
	db==>fuzzy
	db-."pass descrintion and title to Sp".->semen
	subgraph "Spatial Profiler"
		fuzzy-->sample
		semen--"help parser clean data"-->long
		sample--"filtered as `longitude`"-->long
		sample--"filtered as `latitude`"-->lat
		sample--"filtered as `zipcode`"-->zip
		sample--"filtered as `geo`"-->geo
		sample--"filtered as `address`"-->addr
		sample--"filtered as nonspatial"-->stash
		long-->dbnew
		lat-->dbnew
		zip-->dbnew
		geo-->dbnew
		addr-->dbnew
		dbnew-->concat
		
	end
	concat=="add profiled column"==>dbfin
	concat.->json
	
```
As shown in the flow chart, our Profiler contains following steps:

1. Acquire datasets: Access datasets using Auctus datamart REST API.
2. Apply Semantic Processor(SP): Extract geo-related keywords from dataset titles and descriptions, and then pass them to our long-lat parser for further processing.
3. Apply Fuzzy Filter(fuzzy): Employ fuzzy matching to extract and categorize all potential spatial columns using pre-set, distinguishable keywords and context correlation matching. Examine sampled data to verify and improve the fuzzy-matched results.
4. Parse Candidate Column: Develop ad hoc parsers for each keyword type to eliminate noise and outliers, enhancing data accuracy and precision by prioritizing data types on a row-by-row basis.
5. Concatenate Standardized Column: Use the Geocoding Concatenator (GeoConcat) to transform high-priority spatial attributes in the parsed dataset into a single, standardized geo column.

Our entire project is designed with a modular structure and offers an interface for the datamart API. This allows users to seamlessly search for relevant datasets using keywords, identify spatial attributes within those datasets, and visualize the results. Our project empowers clients to perform real-time searches and quickly obtain the desired outcomes.


## References
- [Google MAP python API](https://github.com/googlemaps/google-maps-services-python)
- [Auctus Datamart Rest python API](https://docs.auctus.vida-nyu.org/python/datamart-rest.html)
- [Auctus Search](https://auctus.vida-nyu.org/)


## Project Backlog
[**Google doc**: TeamHoWan - Spatial profiling](https://docs.google.com/document/d/1W1LeSPhxjzlYhPPTPXXu1eGAOy8k51mtLsnEzQjs3hk)

## Prototype
1. Pull data from Auctus using datamart or else.
2. Filter out non-spatial columns (Sence spatial columns). State-machine that read columns or else?
3. Data Cleansing (Filter out rows that are invalid)
4. Generate new column with standardized format (using Google API, or better)
5. Visualization (R, matlab)
