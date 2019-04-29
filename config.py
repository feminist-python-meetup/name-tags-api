import os

# for starters we have to find out what our working directory is, because
# this will be different for the local development environment and the
# final production server
script_path = os.path.dirname(os.path.realpath(__file__)) + '/'

# default settings for the server
urlDocumentation = "https://github.com/feminist-python-meetup/name-tags-api" # should be changed to the final repo, when online
renderDir = "static/rendered/"
templateDir = "static/templates/"

# default settings for the NameTagGenerator
template_file = 'template.svg'
colors = 'color_mapping.json'
default_color = '009e73'
fingerprint = None
gradient = False
