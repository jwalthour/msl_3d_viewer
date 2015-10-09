#!/usr/bin/python
import urllib2
import os
import json
import shutil

DOWNLOAD_BLOCK_SIZE = 32 * 1024 #in bytes

JSON_DIR = "manifests/"
MANIFEST_NAME = "image_manifest.json"
MANIFEST_PATH = JSON_DIR + MANIFEST_NAME

def download_file(local_path, url):
  # Method credit http://stackoverflow.com/questions/1517616/
  #print "Downloading: " + local_path
  resp = urllib2.urlopen(url)
  with open(local_path, 'wb') as f:
    while True:
      block = resp.read(DOWNLOAD_BLOCK_SIZE)
      if not block: break
      f.write(block)

# Loads the master manifest of sols
def load_manifest():
  with open(MANIFEST_PATH) as manifest_file:
    return json.load(manifest_file)

# Loads all sols image indices
def load_image_lists():
  lists = []
  filenames = os.listdir(JSON_DIR)
  filenames.remove(MANIFEST_NAME)
  # Sort numerically.  Assumes filenames are all of the form 'images_solXXX.json'.
  filenames.sort(key=lambda fn: int(fn.split('sol')[1].split('.')[0]))
  for filename in filenames:
    with open(JSON_DIR + filename) as images_file:
      lists.append(json.load(images_file))
  return lists

# Returns true if the two strings match,
# disregarding the character at idx
def strings_match_ignoring_char(string0, string1, idx):
  if len(string0) != len(string1): return False
  else:
    if idx > len(string0) - 1 or idx < 0:
      return string0 == string1
    else:
      return string0[0:idx] == string1[0:idx] and string0[idx + 1:] == string1[idx + 1:]
      
