#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from pprint import pprint

import re
from fileinput import input
import csv

from fuzzywuzzy import fuzz
from fuzzywuzzy import process

articles = ['the', 'a']
prepositions = ['at', 'of']
hospital_words = ['hospital', 'medical', 'center']
word_exclusions = articles + prepositions + hospital_words

class FuzzyHospitals:
  class Result:
    def __init__(self, hospital, score):
      self.hospital = hospital
      self.score = score

  def __init__(self, hospitals):
    self._hospitals = list(filter(lambda x: x.name, hospitals))
    self._name_cache = list(map(lambda x: x.name, self._hospitals))
    self._name_dict = {hospital.name: hospital for hospital in self._hospitals}

  def match(self, name):
    normal_name = normalize_hospital_name(name)
    result = process.extract(normal_name, self._name_cache, limit = 1)
    name, score = None, 0
    if len(result) == 1:
      name, score = result[0]
    return FuzzyHospitals.Result(self._name_dict[name] if name else Hospital("No Match", "No Match"), score)

class Hospital:
  def __init__(self, name, data):
    self.original_name = name
    self.name = normalize_hospital_name(name)
    self.data = data

def normalize_hospital_name(name):
  return " ".join(filter(
    lambda x: x not in word_exclusions,
    re.sub(
      "[^abcdefghijklmnopqrstuvwxyz ]",
      "",
      name.casefold().replace("-", " ")).split()))

def fetch_hospitals(lines):
  return list(filter(None, [re.findall(r"\".*?\"", line)[-1].strip('"') for line in lines]))

def extract_hospital(line):
  words = line.split()
  return Hospital(" ".join(words[1:-2]), " ".join(words[-2:]))

def fetch_hospital_data(lines):
  return [extract_hospital(line) for line in lines]

def write_table_to_file(filename, table):
  with open(filename, 'w') as f:
    tablewriter = csv.writer(f)
    tablewriter.writerows(table)


def match_files(file_a, file_b, outfile):
  hospitals = fetch_hospitals([line for line in input(file_a)][1:])
  hospital_data = FuzzyHospitals(fetch_hospital_data([line for line in input(file_b)][1:]))

  output_table = []

  for hospital in hospitals:
    match = hospital_data.match(hospital)
    output_table.append((hospital, match.hospital.original_name, match.hospital.data))
    pprint(output_table[-1])

  write_table_to_file(outfile, output_table)

######## Main ########
if __name__ == '__main__':
  from sys import argv
  if len(argv) >= 4:
    match_files(argv[1], argv[2], argv[3])
  else
    print("Invalid number of arguments. Please pass FileA, FileB, and the name of the output file respectively.")
