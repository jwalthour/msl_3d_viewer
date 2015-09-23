#!/usr/bin/python
import json
import os
import os.path
import common

IMG_DIR = "images/" # must end in "/"

def update_json(start_sol, end_sol):
  if not os.path.isdir(common.JSON_DIR):
    os.makedirs(common.JSON_DIR)
  common.download_file(common.MANIFEST_PATH, "http://mars.jpl.nasa.gov/msl-raw-images/image/image_manifest.json")
  
  manifest = common.load_manifest()
  for sol in manifest["sols"]:
    if sol["sol"] >= start_sol and sol["sol"] <= end_sol:
      url = sol["catalog_url"]
      outfile = common.JSON_DIR + url.split("/")[-1]
      common.download_file(outfile, url)

def clear_downloaded_manifests():
  if os.path.isdir(common.JSON_DIR):
    for filename in os.listdir(common.JSON_DIR):
      os.remove(common.JSON_DIR + filename)

def get_full_images(start_sol, end_sol, instrument_startswith):
  clear_downloaded_manifests()
  update_json(start_sol, end_sol)
  if not os.path.isdir(IMG_DIR):
    os.makedirs(IMG_DIR)
  sol_dirs = os.listdir(IMG_DIR)
  for image_list in common.load_image_lists():
    sol = image_list["sol"]
    sol_dir = "sol%d"%sol
    if not sol_dir in sol_dirs:
      os.makedirs(IMG_DIR + sol_dir)
    for image in image_list["images"]:
      if image["instrument"].startswith(instrument_startswith) and image["sampleType"] == "full":
        url = image["urlList"]
        instrument_dir = image["instrument"]
        instrument_dirs = os.listdir(IMG_DIR + sol_dir)
        if not instrument_dir in instrument_dirs:
          os.makedirs(IMG_DIR + sol_dir + "/" + instrument_dir)
        local_path = IMG_DIR + sol_dir + "/" + instrument_dir + "/" + url.split("/")[-1]
        if os.path.isfile(local_path):
          print "Present; won't download: " + local_path
        else:
          common.download_file(local_path, url)

# Makes an index for use by the javascript
def make_index_of_downloaded_photos():
  pass

get_full_images(0, 10, "NAV_")