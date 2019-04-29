#!venv/bin/python

from flask import Flask, render_template, request
from flask_restful import Api, Resource, reqparse, abort
import json
import name_tag
import config

"""
Here we initialise our Flask app instance and we also create a flask_restful Api instance from it
"""
app = Flask(__name__)
api = Api(app)

"""
At the root ('/') of our web app we want to have a just a simple index page rendered to the user
"""
@app.route('/')
def index():
    return render_template('index.html', docs=config.urlDocumentation)

"""
For now we are storing all the created nametags in a list. This means, when the
app is restarted, also all created items are lost. This can be changed by using
some persinstent store, like in a file or database.
To have an example already there we put a first name tag alread in our nametags
list and generate it with our name tag generator.
"""
nametags = [
    {
        'id': 1,
        'name': 'jackie*',
        'pronouns': 'per, pers, pers',
        'default_color': False,
        'fingerprint': False,
        'gradient': False,
        'file': '/' + config.renderDir + '1.svg'
        # we would like to have the file as a full url, like for those generated
        # by the /nametags POST function later on, but at this point the app does
        # not know yet what the root url is (because no request was made) - probably
        # there is another nifty way to find that out?
    }
]

# Now we are doing a first test run with our NameTagGenerator (defined in the
# name_tag.py file).
firstTag = name_tag.NameTagGenerator()

# The generator is now initialized with some default values. Here we want to
# customize it according to whatever we have set up there in the first nametag
# list item.
if nametags[0]['default_color']:
    firstTag.default_color = nametags[0]['default_color']
if nametags[0]['fingerprint']:
    firstTag.fingerprint = nametags[0]['fingerprint']
if nametags[0]['gradient']:
    firstTag.gradient = nametags[0]['gradient']
    firstTag.template_file = 'gradient.svg'

# Now everyting is set, let us generate the tag.
firstTag.generate(nametags[0]['name'], nametags[0]['pronouns'], config.script_path + config.renderDir + str(nametags[0]['id']) + '.svg')

"""
For the user it might be nice to be able to retrieve the color map(s), so they
know which pronouns are already availbe with a specific color. And maybe in a
later version we want to add a feature so that users can use their own color maps.
Therefore we define another list that holds all colormaps and create a first
item labelled 'default' from our color_mapping.json file.
"""
colormaps = []
colormaps.append({
    'label': 'default',
    'mappings': json.load(open(config.script_path + 'color_mapping.json', "r"))
})

"""
To access our API the users will different endpoints which in turn are mapped to
differnt classes which implement the different HTTP medhots (GET, POST, DELETE, etc.)
which can be used on the single enpdoints. The mapping is done at the hand. Here
we create a NameTagList resource, which has a GET method to list all available
nametags and a POST method to create a new nametag. This will later be mapped to
the endpoint /nametags
"""
class NameTagList(Resource):
    def __init__(self):
        """
        Here we initialise our resource and the request parser, which can be used
        in those methodes that need it. For the arguments we could be more efficient
        and use default parameters and do some other tricks, but we want to have a
        strict (and secure) API, so we will be doing thorough input validation later.
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, location='json')
        self.reqparse.add_argument('pronouns', type=str, location='json')
        self.reqparse.add_argument('gradient', type=str, location='json')
        self.reqparse.add_argument('fingerprint', type=str, location='json')
        self.reqparse.add_argument('default_color', type=str, location='json')
        super(NameTagList, self).__init__()

    def get(self):
        """
        For a GET request on the nametags endpoint we just have to return the
        current contents of the nametags list.
        """
        return nametags

    def post(self):
        """
        A POST request on the nametags endpoint should add a new nametag to our
        list of nametags and create a corresponding SVG file. So first we start
        our argument parser to parse the request body.
        """
        args = self.reqparse.parse_args()

        """
        Now, we could be more efficient here, but we will be doing quite explicit
        input validation to be sure nothing is fishy. It also is good and secure
        practice to do explicit input validation. This way you make sure that
        you did not just assume some specific input. And of course we trust a
        lot of users, but certainly not all of them. Well, you know, its the internet!
        """
        name = False
        pronouns = False
        default_color = False
        fingerprint = False
        gradient = False

        # Name and pronouns obviously have to be provided. If they are missing
        # we'll abort and return an error message.
        if not args['name'] or len(args['name']) == 0:
            abort(400, message="Use the name argument. No nametag without a name here.")
        if not args['pronouns'] or len(args['pronouns']) == 0:
            abort(400, message="Use the pronouns argument. No nametag without your pronouns here.")
        name = args['name']
        pronouns = args['pronouns']

        # default_color does not have to be provided. But if it is has to stick to
        # the 6-digit hex format.
        if args['default_color']:
            if len(args['default_color']) != 6:
                abort(400, message="default_color has to be a 6-digit hexadecimal value")
            try:
                testval = int(args['default_color'], 16)
            except ValueError:
                abort(400, message="default_color has to be a 6-digit hexadecimal value")
        default_color = args['default_color']

        # fingerprint is also optional. But if provided, it has to be a hex value
        if args['fingerprint']:
            try:
                fingerprint = int(args['fingerprint'], 16)
            except ValueError:
                abort(400, message="fingerprint has to be a hexadecimal value")

        # gradient is also optional (defaults to false), but if provided only
        # the strings 'true' and 'false are allowed'
        if args['gradient'] == 'true':
            gradient = True
        elif args['gradient'] != 'false':
            abort(400, message="gradient has to be either 'true' or 'false'")

        """
        Nice, our input is validated. So let's get to creating the name tag
        """

        # First, we need to generate a new ID for the new name tag. One easy
        # way out here is to just increase the ID from the last name tag by 1.
        id = nametags[-1]['id'] + 1 if len(nametags) > 0 else 1

        # Also we'll just create the output file in our static/rendered directory
        # with the ID as its name
        output_file = 'static/rendered/' + str(id) + '.svg'

        # Now lets create a NameTagGenerator object (defined in name_tag.py) and
        # set all (validated) arguments, that have been provided in the request body
        gen = name_tag.NameTagGenerator()

        if gradient:
            gen.gradient = True
            gen.template_file = 'gradient.svg'

        if fingerprint:
            gen.fingerprint = fingerprint

        if default_color:
            gen.default_color = default_color

        # We're good to go, now we can generate a name tag - and check if the
        # generate method actually returns the output file we wanted it to produce.
        # While the local dev server can work with relative paths, that might not
        # work on the production server. Therefore we add the script_path here
        # to use the absolute path to the rendered file.
        of = gen.generate(name, pronouns, config.script_path + output_file)
        if of != config.script_path + output_file:
            abort(400, message="Uupsie, something went wrong. NameTagGenerate.gen did not return valid output file.")

        """
        Now that our SVG name tag was created we'll have to add it to our list
        of name tags, before we also return the newly created tag itself through
        the API, so the user gets the new ID and the link to the file
        """
        tag = {
            'id': id,
            'name': name,
            'pronouns': pronouns,
            'file': request.url_root + output_file
        }
        nametags.append(tag)
        return tag


"""
The NameTag resources is here to output single nametags if accessed through
the /nametags/<int:id> endpoint, as well as to delete single endpoints - provided
the user has a valid deletion tag (has yet to be implemented).
"""
class NameTag(Resource):
    def get(self, id):
        """
        For the GET request we just have to search in our nametag list for the
        name tag with the id that was used as an argument and then return it.
        Here we use a neat list comprehension to do it in one line. If you are
        not sure how list comprehensions work, Lisa Tagliaferri wrote a good
        article on that:
        https://www.digitalocean.com/community/tutorials/understanding-list-comprehensions-in-python-3
        """
        found_tags = [tag for tag in nametags if tag['id'] == id]
        # if our list comprehension returned an empty array, because there is
        # no name tag with the given id, we return a 404 Not Found error
        if len(found_tags) == 0:
            abort(404, message="There is no name tag with ID {}".format(id))
        # if a name tag was found it should be the only item in the list
        return found_tags[0]

"""
This will be connected to the /colormaps endpoint and so far just prints out
the available color maps. Should be extended later, so users can provide their
own color maps.
"""
class ColorMaps(Resource):
    def get(self):
        return colormaps

"""
This will be connected to the /templates endpoint. And well, so far, it is not
implemented, as a GET request to this will clearly reveal. But it could be
extended in a way, so that users can check out which templates are available
and to even provide their own templates.
"""
class NameTagTemplates(Resource):
    def get(self):
        return {'notice': 'By the mighty witchcraftry of the mother of time! This feature is not yet implemented.'}

"""
This resource will handle the root endpoint of the API (/), and print some info
on which endpoints are available as well as where you can get more info.
"""
class Root(Resource):
    def get(self):
        description = {
            'endpoints': ['nametags', 'nametags/<int:id>', 'colormaps', 'templates'],
            'documentation': config.urlDocumentation
        }
        return description

"""
So, everything else is set up, now we only have to connect the endpoints with
the corresponding resource classes. We will prefix our endoints with /api/v1
so that it gets easier to manage different versions of the API.
"""
api.add_resource(Root, '/api/v1')
api.add_resource(ColorMaps, '/api/v1/colormaps')
api.add_resource(NameTagTemplates, '/api/v1/templates')
api.add_resource(NameTagList, '/api/v1/nametags')
api.add_resource(NameTag, '/api/v1/nametags/<int:id>')

"""
Finally, we start the app right here, if we are starting it from our local
development environment by calling ./server.py directly. This way we'll
get some debug info and some nice lazy loading (so we don't have to restart
the app every time we change and save some of the code). But this should not
be used in a production environment (therefor the if clause).
"""
if __name__ == '__main__':
    app.run(debug=True)
