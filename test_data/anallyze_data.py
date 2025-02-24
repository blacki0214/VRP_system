def analyze_cities():
    import pandas as pd

    # Load distance data
    distance_df = pd.read_csv('distance.csv')
    
    # Get unique cities from Source and Destination columns
    source_cities = set(distance_df['Source'].unique())
    dest_cities = set(distance_df['Destination'].unique())
    
    # Combine unique cities
    all_cities = source_cities.union(dest_cities)
    
    print("\nCity Analysis:")
    print(f"Number of unique cities: {len(all_cities)}")
    print(f"Source cities: {len(source_cities)}")
    print(f"Destination cities: {len(dest_cities)}")
    print("\nSample cities:")
    print(list(all_cities)[:5])

# Let's analyze the data
analyze_cities()