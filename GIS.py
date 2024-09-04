import pandas as pd
import geopandas as gpd
import folium
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# Read the CSV file
file_path = 'csv-data.csv'
data = pd.read_csv(file_path)

# Correct column names (adjust these if needed based on your CSV)
year_column = 'Year'
easting_column = 'Easting'
northing_column = 'Northing'
emission_column = 'Emission'

# Convert the easting and northing to a GeoDataFrame
gdf = gpd.GeoDataFrame(
    data,
    geometry=gpd.points_from_xy(data[easting_column], data[northing_column]),
    crs="EPSG:27700"  # British National Grid
)

# Convert to WGS84 (latitude and longitude)
gdf = gdf.to_crs(epsg=4326)

# Extract the latitude and longitude
gdf['latitude'] = gdf.geometry.y
gdf['longitude'] = gdf.geometry.x

# Extract the coordinates (latitude and longitude)
X = gdf[['longitude', 'latitude']].values  # Only use lat and lon as features

# Normalize the data
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Input for the number of clusters
n_clusters = int(input("Enter the number of clusters: "))

# Perform K-means clustering
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
kmeans.fit(X_scaled)

# Add the cluster labels back to the GeoDataFrame
gdf['cluster'] = kmeans.labels_

# Get the cluster centroids and convert them back to the original scale
centroids = scaler.inverse_transform(kmeans.cluster_centers_)

# Create a folium map centered around the UK
m = folium.Map(location=[55.3781, -3.4360], zoom_start=6)

# Define a list of colors for the clusters and centroids
centroid_colors = ['red', 'blue', 'green', 'purple', 'orange']

# Ensure that the number of colors matches the number of clusters
if n_clusters > len(centroid_colors):
    from matplotlib import cm
    import numpy as np
    cmap = cm.get_cmap('tab10', n_clusters)
    centroid_colors = [cm.colors.to_hex(cmap(i)) for i in range(n_clusters)]

# Add existing carbon sources to the map with the same color as the cluster centroid
for _, row in gdf.iterrows():
    cluster = row['cluster']
    color = centroid_colors[cluster]
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=(f"Year: {row[year_column]}\n"
               f"Emissions: {row[emission_column]} tons\n"
               f"Cluster: {row['cluster']}"),
        icon=folium.Icon(color=color),
        tooltip="Click for more info"
    ).add_to(m)

# Add the centroids of each cluster to the map with the same color
for i, centroid in enumerate(centroids):
    folium.Marker(
        location=[centroid[1], centroid[0]],  # centroid[1] is latitude, centroid[0] is longitude
        popup=f"Centroid of Cluster {i}",
        icon=folium.Icon(color=centroid_colors[i], icon="star"),
        tooltip=f"Centroid {i}"
    ).add_to(m)

# Save the map to an HTML file
m.save('carbon_sources_map_with_centroids.html')
