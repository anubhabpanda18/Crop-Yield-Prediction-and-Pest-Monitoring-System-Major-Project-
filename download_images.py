#!/usr/bin/env python3
import urllib.request
import os

def download_image(url, filename):
    """Download an image from URL with proper headers"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            with open(filename, 'wb') as out_file:
                out_file.write(response.read())
        print(f"✓ Downloaded {filename}")
        return True
    except Exception as e:
        print(f"✗ Failed to download {filename}: {e}")
        return False

# Create images directory
os.makedirs('static/images', exist_ok=True)

# List of pest images to download
images = [
    ('https://upload.wikimedia.org/wikipedia/commons/5/5e/Nilaparvata_lugens.jpg', 'static/images/nilaparvata_lugens.jpg'),
    ('https://upload.wikimedia.org/wikipedia/commons/9/9e/Spodoptera_frugiperda_caterpillar.jpg', 'static/images/spodoptera_frugiperda.jpg'),
    ('https://upload.wikimedia.org/wikipedia/commons/1/11/Aphis_gossypii_cotton_aphid.jpg', 'static/images/aphis_gossypii.jpg'),
    ('https://upload.wikimedia.org/wikipedia/commons/c/c4/Bemisia_tabaci.jpg', 'static/images/bemisia_tabaci.jpg'),
    ('https://upload.wikimedia.org/wikipedia/commons/8/8e/Helicoverpa_armigera_caterpillar.jpg', 'static/images/helicoverpa_armigera.jpg'),
    ('https://upload.wikimedia.org/wikipedia/commons/4/49/Puccinia_striiformis_on_wheat.jpg', 'static/images/puccinia_striiformis.jpg'),
    ('https://upload.wikimedia.org/wikipedia/commons/e/e6/Tetranychus_urticae_with_silk_threads.jpg', 'static/images/tetranychus_urticae.jpg'),
    ('https://upload.wikimedia.org/wikipedia/commons/6/6c/Chilo_suppressalis.jpg', 'static/images/chilo_suppressalis.jpg'),
]

# Download all images
for url, filename in images:
    download_image(url, filename)

print("Download complete!")