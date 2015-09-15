#!/usr/bin/python
import os
import json

DATA_DIR = "data/"
MANIFEST_PATH = "%simage_manifest.json"%DATA_DIR

def parse_manifest():
  with open(MANIFEST_PATH) as manifest_file:
    return json.load(manifest_file)

# Downloads copies
def update_json(start_sol, end_sol):
  os.system("rm %s"%MANIFEST_PATH);
  os.system("wget -O%s http://mars.jpl.nasa.gov/msl-raw-images/image/image_manifest.json"%MANIFEST_PATH);
  manifest = parse_manifest()
  for sol in manifest["sols"]:
    if sol["sol"] >= start_sol and sol["sol"] <= end_sol:
      url = sol["catalog_url"]
      outfile = "%s%s"%(DATA_DIR,url.split("/")[-1])
      os.system("wget -O%s %s"%(outfile,url))

def get_full_images(start_sol, end_sol, instrument_startswith):
  update_json(start_sol, end_sol)
      
      
get_full_images(0, 10, "NAV_")