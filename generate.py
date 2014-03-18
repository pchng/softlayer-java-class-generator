#!/usr/bin/env python

# Tested in Python 2.7.x
import requests
import argparse
from bs4 import BeautifulSoup

import logging

# Argparse setup.
parser = argparse.ArgumentParser(
  description="Generate data classes based on SoftLayer Data Types. This will save the output into a ClassName.java file, overwriting any existing file unless the --output option is used.",
  add_help=True
)
parser.add_argument(
  'datatype_url',
  type=str,
  help="URL of the SoftLayer Data Type in the API documentation",
)
parser.add_argument(
  '-n', '--name',
  type=str,
  default=None,
  help="The name of the class; defaults to name of the data type minus the 'SoftLayer_' prefix with underscores converted to CamelCase.",
  dest='name',
)
parser.add_argument(
  '-p', '--package',
  type=str,
  default=None,
  help="The package of the class; default is no package.",
  dest='package',
)
parser.add_argument(
  '-v',
  type=str,
  default='private',
  help="The visibility of the data fields.",
  dest='visibility',
)
parser.add_argument(
  '--logger',
  type=str,
  default='output.log',
  help="Log file name. Default: output.log",
  dest='log_file'
)
parser.add_argument(
  '--output',
  action='store_true',
  help="Output to console instead of saving to file.",
  dest='output_to_console'
)
args = parser.parse_args()

# Logging configuration.
log_date_format = "%Y-%m-%d %H:%M:%S %Z"
logging.basicConfig(
  format="[%(levelname)s:%(asctime)s] %(message)s", 
  datefmt=log_date_format,
  filename=args.log_file
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Read mapping data.
sl_to_java = {}
java_imports = {}
with open('mapping.csv') as map_file:
  for line in map_file:
    if line[0] == '#':
      continue

    parts = [part.strip() for part in line.split(',')]
    if len(parts) < 2:
      logger.warn("Ignoring invalid line in mapping file: {}".format(line))
      continue

    sl_to_java[parts[0]] = parts[1]
    if len(parts) > 2:
      java_imports[parts[1]] = parts[2]

# It is completely insecure to set verify=false, but some systems may not trust the root CA for the SoftLayer TLS certificate.
r = requests.get(args.datatype_url, verify=False)
html = BeautifulSoup(r.text)

class_name = args.name
if not class_name:
  # Will encounter IndexError if this doesn't exist.
  class_name = html.select('h1.title .service')[0].text
  class_name = class_name.replace('SoftLayer_', '').replace('_', '')

# NOTE: The markup is invalid in that there are two elements with id="properties"; 
# assume the first is the local properties we are concerned about.
properties = html.select('#properties')
if len(properties) < 2:
  raise Exception("No properties found.")

properties = properties[0]

# Sanity check, not strictly necessary; makes things more fragile.
title = properties.find(name='h2', class_='pane-title')
if not title or "Local Properties" not in title.text:
  raise Exception("Could not find any local properties.")

output_fields = ''
converted_types = set()
properties = properties.select('.views-row')
for prop in properties:
  # If anything changes, should encounter an IndexError since the result list will be empty.
  field_name = prop.select('.views-field-title .field-content')[0].text
  sl_data_type = prop.select('.views-field-field-type-value .field-content')[0].text

  if sl_data_type not in sl_to_java:
    logger.warn("Excluding {} because the type {} was not recognized.".format(field_name, sl_data_type))
    continue

  # This isn't really needed since we build the output field list here.
  java_type = sl_to_java[sl_data_type]
  converted_types.add(java_type)
  output_fields += '  {} {} {};\n'.format(args.visibility, java_type, field_name)

# Build the list of imports.
imports = ''
for java_type, import_statement in java_imports.iteritems():
  if java_type in converted_types:
    imports += import_statement + '\n';

with open('class.template') as template_file:
  template = template_file.read()
  package_statement = 'package {};\n\n'.format(args.package) if args.package else ''
  output = template.format(
    package=package_statement, 
    import_statements=imports, 
    class_name=class_name, 
    fields=output_fields
  )

  if args.output_to_console:
    print output
  else:
    with open('{}.java'.format(class_name), 'w') as output_file:
      output_file.write(output)
