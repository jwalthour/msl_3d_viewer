#!/usr/bin/python
import json
import os
import common

IMG_DIR = "images/"

def update_json(start_sol, end_sol):
  common.download_file(common.MANIFEST_PATH, "http://mars.jpl.nasa.gov/msl-raw-images/image/image_manifest.json")
  
  manifest = common.load_manifest()
  for sol in manifest["sols"]:
    if sol["sol"] >= start_sol and sol["sol"] <= end_sol:
      url = sol["catalog_url"]
      outfile = common.JSON_DIR + url.split("/")[-1]
      common.download_file(outfile, url)

def clear_downloaded_manifests():
  for filename in os.listdir(common.JSON_DIR):
    os.remove(common.JSON_DIR + filename)

def get_full_images(start_sol, end_sol, instrument_startswith):
  clear_downloaded_manifests()
  update_json(start_sol, end_sol)
  img_dirs = os.listdir(IMG_DIR)
  for image_list in common.load_image_lists():
    sol = image_list["sol"]
    img_dir = "sol%d"%sol
    if not img_dir in img_dirs:
      os.makedirs(IMG_DIR + img_dir)
    for image in image_list["images"]:
      if image["instrument"].startswith(instrument_startswith) and image["sampleType"] == "full":
        url = image["urlList"]
        common.download_file(IMG_DIR + img_dir + "/" + url.split("/")[-1], url)


get_full_images(0, 10, "NAV_")