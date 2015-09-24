#!/usr/bin/python
import argparse
import json
import os
import os.path
import common

JS_DIR = "js/" # must end in "/"
IMAGE_INDEX_PATH = JS_DIR + "image_index.js"
INSTRUMENTS_PATH = JS_DIR + "instruments.js"
AVAIL_PATH = JS_DIR + "avail.js"
IMG_DIR = "images/" # must end in "/"
# SIDES = ["A","B"] # instruments are redundant as "A side" and "B side"; both have been in use this mission
INSTRUMENTS={
  "navcams": {
    "human_readable":"Navigation Cameras",
    "dir":"navcam",
    "inst_prefix":{
      "r":"NAV_RIGHT_",
      "l":"NAV_LEFT_",
    },
  },
  "front_hazcams": {
    "human_readable":"Front Hazard Avoidance Cameras",
    "dir":"f_hazcam",
    "inst_prefix":{
      "r":"FHAZ_RIGHT_",
      "l":"FHAZ_LEFT_",
    },  
  },
  "rear_hazcams": {
    "human_readable":"Rear Hazard Avoidance Cameras",
    "dir":"r_hazcam",
    "inst_prefix":{
      "r":"FHAZ_RIGHT_",
      "l":"FHAZ_LEFT_",
    },  
  },
  "mastcams":{
    "human_readable":"Mast Cameras",
    "dir":"mastcam",
    "inst_prefix":{
      "r":"MAST_RIGHT", # No A and B sides for this one
      "l":"MAST_LEFT",
    },  
  },
}
def update_main_manifest():
  if not os.path.isdir(common.JSON_DIR):
    os.makedirs(common.JSON_DIR)
  common.download_file(common.MANIFEST_PATH, "http://mars.jpl.nasa.gov/msl-raw-images/image/image_manifest.json")

def update_json(start_sol, end_sol):
  update_main_manifest()
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
  r_insts = [{"prefix":INSTRUMENTS[inst]["inst_prefix"]['r'], "dir":INSTRUMENTS[inst]["dir"]} for inst in instruments]
  l_insts = [{"prefix":INSTRUMENTS[inst]["inst_prefix"]['l'], "dir":INSTRUMENTS[inst]["dir"]} for inst in instruments]
  for image_list in common.load_image_lists():
    sol = image_list["sol"]
    sol_dir = "sol%d"%sol
    if not sol_dir in sol_dirs:
      os.makedirs(IMG_DIR + sol_dir)
    instrument_dirs = os.listdir(IMG_DIR + sol_dir)
    for image in image_list["images"]:
      correct_instrument = None
      for inst in r_insts:
        if image["instrument"].startswith(inst["prefix"]):
          correct_instrument = inst
          instrument_dir = inst["dir"] + '/' + "r"
          break
      if not correct_instrument:
        for inst in l_insts:
          if image["instrument"].startswith(inst["prefix"]):
            correct_instrument = inst
            instrument_dir = inst["dir"] + '/' + "l"
            break
      if not inst["dir"] in instrument_dirs:
        os.makedirs(IMG_DIR + sol_dir + "/" + inst["dir"] + "/r")
        os.makedirs(IMG_DIR + sol_dir + "/" + inst["dir"] + "/l")
        instrument_dirs.append(inst["dir"])  
      if correct_instrument != None and image["sampleType"] == "full":
        url = image["urlList"]
        local_path = IMG_DIR + sol_dir + "/" + instrument_dir + "/" + url.split("/")[-1]
        if os.path.isfile(local_path):
          print "Present; won't download: " + local_path
        else:
          common.download_file(local_path, url)

# Makes an index for use by the javascript
# This ignores the manifests, and only looks at the filesystem.
def make_index_of_downloaded_photos():
  inst_for_dir = {INSTRUMENTS[inst]["dir"]:inst for inst in INSTRUMENTS}
  image_index = {}
  sol_dirs = os.listdir(IMG_DIR)
  for sol_dir in sol_dirs:
    sol_num = int(sol_dir[3:])
    sol = {}
    inst_dirs = os.listdir(IMG_DIR + sol_dir)
    for inst_dir in inst_dirs:
      images = []
      if inst_dir in inst_for_dir:
        inst = inst_for_dir[inst_dir]
        
        # Lucky for us, the directories are both sorted the same way.
        # We assume they didn't delete just one.
        r_img_filenames = os.listdir(IMG_DIR + sol_dir + '/' + inst_dir + '/r')
        l_img_filenames = os.listdir(IMG_DIR + sol_dir + '/' + inst_dir + '/l')
        for pair in zip(r_img_filenames, l_img_filenames):
          image = {
            "r_file_path": IMG_DIR + sol_dir + '/' + inst_dir + '/r/' + pair[0],
            "l_file_path": IMG_DIR + sol_dir + '/' + inst_dir + '/l/' + pair[1]
          }
          images.append(image)
        sol[inst] = images
    image_index[sol_num] = sol
  return image_index

# Returns a dictionary showing which sols are available for a particular instrument
def make_availability_list(image_index):
  avail = {};
  for sol in image_index:
    for inst in image_index[sol]:
      if(len(image_index[sol][inst]) > 0):
        if not inst in avail:
          avail[inst] = []
        avail[inst].append(sol)
  return avail

def main():
  parser = argparse.ArgumentParser(description="Downloads photos from NASA's Mars Science Laboratory public API for use in stereo viewing.")
  group_range = parser.add_argument_group('Range', 'An inclusive range of sols to download')
  group_range.add_argument("-s", "--start",    metavar="<sol>", dest="start",type=int, help="Start of range")
  group_range.add_argument("-e", "--end",      metavar="<sol>", dest="end",  type=int, help="End of range")
  
  parser.add_argument("-n", "--latest",   metavar="<N>", dest="latest",  type=int, help="Download images from the latest N sols")
  args = parser.parse_args()
  if (args.start != None) != (args.end != None): # Need either both or none
    parser.error("Must specify both start and end if you specify one")
  elif args.start and args.end and args.end < args.start:
    parser.error("Must specify an end sol after the start sol")
  
  # Set up a reasonable default
  start = args.start
  end = args.end
  latest = args.latest
  if start == None and end == None and latest == None:
    latest = 10
  
  # If they ask for the latest N sols, ignore any specified start and end
  if latest != None:
    update_main_manifest()
    manifest = common.load_manifest()
    end = manifest["latest_sol"]
    start = end - latest
    print "Will download the latest %d sols, %d-%d."%(latest,start,end)
  else:
    print "Will download sols %d-%d."%(start,end)
  
  if not os.path.isdir(JS_DIR):
    os.makedirs(JS_DIR)
  get_full_images(start, end, ["navcams", "front_hazcams"])
  image_index = make_index_of_downloaded_photos()
  avail = make_availability_list(image_index)
  index_str = "var image_index=" + json.dumps(image_index)
  instrument_str = "var instruments=" + json.dumps(INSTRUMENTS)
  avail_str = "var avail=" + json.dumps(avail)
  with open(IMAGE_INDEX_PATH, 'w') as outfile:
    outfile.write(index_str)
  with open(INSTRUMENTS_PATH, 'w') as outfile:
    outfile.write(instrument_str)
  with open(AVAIL_PATH, 'w') as outfile:
    outfile.write(avail_str)

if __name__ == "__main__":
    main()