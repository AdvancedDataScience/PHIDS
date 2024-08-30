from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

print(counties["features"][0])
import geopandas as gpd
trat = gpd.GeoDataFrame.from_file("Map/Trat/Tambol/Trat.shx", encoding = 'utf-8')
trat['geo_index'] = trat.index
print(trat)
trat['geo_index'] = trat.index