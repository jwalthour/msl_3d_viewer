#!/usr/bin/python
import argparse
import json
import os
import os.path
import common

JS_DIR = "js/" # must end in "/"
IMAGE_INDEX_PATH = JS_DIR + "image_index.js"
INSTRUMENTS_PATH = JS_DIR + "instruments.js"
IMG_DIR = "images/" # must end in "/"
# SIDES = ["A","B"] # instruments are redundant as "A side" and "B side"; both have been in use this mission
INSTRUMENTS={
  "navcams": {
    "human_readable":"Navigation Cameras",
    "inst_prefix":{
      "r":"NAV_RIGHT_",
      "l":"NAV_LEFT_",
    },
  },
  "front_hazcams": {
    "human_readable":"Front Hazard Avoidance Cameras",
    "inst_prefix":{
      "r":"FHAZ_RIGHT_",
      "l":"FHAZ_LEFT_",
    },  
  },
  "rear_hazcams": {
    "human_readable":"Front Hazard Avoidance Cameras",
    "inst_prefix":{
      "r":"FHAZ_RIGHT_",
      "l":"FHAZ_LEFT_",
    },  
  },
  "mastcams":{
    "human_readable":"Mast Cameras",
    "inst_prefix":{
      "r":"MAST_RIGHT", # No A and B sides for this one
      "l":"MAST_LEFT",
    },  
  },
}
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

#start_sol: an integer
#end_sol: an integer
#instruments: a list of strings, which must be keys of INSTRUMENTS structure
def get_full_images(start_sol, end_sol, instruments):
  clear_downloaded_manifests()
  update_json(start_sol, end_sol)
  if not os.path.isdir(IMG_DIR):
    os.makedirs(IMG_DIR)
  sol_dirs = os.listdir(IMG_DIR)
  prefixes = [INSTRUMENTS[inst]["inst_prefix"][side] for side in ['r','l'] for inst in instruments]
  for image_list in common.load_image_lists():
    sol = image_list["sol"]
    sol_dir = "sol%d"%sol
    if not sol_dir in sol_dirs:
      os.makedirs(IMG_DIR + sol_dir)
    for image in image_list["images"]:
      correct_instrument = False
      for prefix in prefixes:
        if image["instrument"].startswith(prefix):
          correct_instrument = True
          break
      if correct_instrument and image["sampleType"] == "full":
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
# This ignores the manifests, and only looks at the filesystem.
def make_index_of_downloaded_photos():
  return []

def main():
  parser = argparse.ArgumentParser(description="Downloads photos from NASA's Mars Science Laboratory public API for use in stereo viewing.")
  parser.add_argument("-s", "--start",    metavar="sol", dest="start",type=int,  default=1090, help="Download images from sols starting at this one")
  parser.add_argument("-e", "--end",      metavar="sol", dest="end",  type=int,  default=1100, help="Download images from sols ending at this one")
  args = parser.parse_args()
  
  if not os.path.isdir(JS_DIR):
    os.makedirs(JS_DIR)
  print "Downloading data from sol %d to sol %d."%(args.start, args.end)
#  get_full_images(args.start, args.end, ["navcams", "front_hazcams"])
  js_index = make_index_of_downloaded_photos()
  index_str = "var image_index=" + json.dumps(js_index)
  instrument_str = "var instruments=" + json.dumps(INSTRUMENTS)
  with open(IMAGE_INDEX_PATH, 'w') as outfile:
    outfile.write(index_str)
  with open(INSTRUMENTS_PATH, 'w') as outfile:
    outfile.write(instrument_str)

if __name__ == "__main__":
    main()