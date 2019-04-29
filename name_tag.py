from jinja2 import Environment, FileSystemLoader, select_autoescape
from bs4 import BeautifulSoup
import json
import hashlib
import config

"""
This draws mostly on the work of Saara and Zoé, who wrote the name tag generator
for the feminist python meetup 0x09 (https://feminist-python.diebin.at). You
can find their source on https://github.com/feminist-python-meetup/name-tags

For the purpos of wrapping a REST API around it, i just stripped away the
argparse handling (as this is done separately in server.py) and refactored
the code into a NameTagGenerator class with one generate method.
"""
class NameTagGenerator:
    """
    Here we just define some default values which can be set in the config.py
    """
    template_file = config.template_file
    colors = config.script_path + config.colors
    default_color = config.default_color
    fingerprint = config.fingerprint
    gradient = config.gradient

    """
    This is the method generating the name tag as a SVG file from all the parameters
    """
    def generate(self, name, pronouns, output_file):
        color_map = json.load(open(self.colors, "r"))

        """
        load the specified template for the name tag from static/templates/ folder
        """
        env = Environment(
            loader=FileSystemLoader(config.script_path + config.templateDir),
            autoescape=select_autoescape(["html", "xml", "svg"]),
        )
        template = env.get_template(self.template_file)

        """
        set the jinja2 variables in the template to the values we got from the command line
        """
        name_tag = template.render(name=name, pronouns=pronouns)

        """
        unfortunately we can't use jinja2 to set all variable things (such as background color) in the template :( so we'll use beautifulsoup to manipulate the xml
        """
        soup = BeautifulSoup(name_tag, "xml")

        """
        find the backgound and change the color of the "fill" element to the color according to the mapping file
        """
        background_tag = soup.find(id="background-rectangle")
        background = background_tag["style"].replace(
            "fill:#ffdd55", "fill:#{}".format(color_map.get(pronouns, self.default_color))
        )
        background_tag["style"] = background

        """
        generate the fun squiggly in the top left corner, one way to get numeric data is by getting the unicode code point of each letter in the user's name
        """
        # 3,3 14.5,10.5 20,3 26,18
        squiggly_tag = soup.find(id="squiggly")

        points = []
        start_x = 3
        start_y = 3
        max_length = 23
        max_height = 15
        x_position = max_length / len(name)
        for i, char in enumerate(name):
            x = i * x_position + start_x
            y = ord(char) % max_height + start_y
            point = "{},{}".format(x, y)
            points.append(point)
        generated_squiggly = "M " + " ".join(points)

        squiggly_tag["d"] = generated_squiggly

        """
        add barcode under name block if user gave a public key
        """
        breakUpBy = 6
        if self.fingerprint is not None:
            hexstring = hex(self.fingerprint)[2:]
            colorArray = [
                hexstring[i : i + breakUpBy] for i in range(0, len(hexstring), breakUpBy)
            ]
            lastColor = colorArray[-1]
            colorArray.remove(colorArray[-1])
            lastColor = lastColor + (breakUpBy - len(lastColor)) * "8"
            colorArray.append(lastColor)
            hashboxes = len(colorArray)
            hash_height = 2.5
            hash_width = 79 / hashboxes
            hash_origin = [2.75, 38.12]  # originX, originY
            for idx, color in enumerate(colorArray):
                hash_tag = soup.new_tag("rect")
                hash_tag["id"] = "hash-" + str(idx)
                hash_tag["height"] = hash_height
                hash_tag["width"] = hash_width
                hash_tag["x"] = idx * hash_width + hash_origin[0]
                hash_tag["y"] = hash_origin[1]
                color = "#" + color
                hash_tag["style"] = "fill:" + color + ";stroke:none;"
                squiggly_tag.insert_after(hash_tag)

        """
        make pretty gradient in background by hashing the name and using the hash for 3 hex codes!
        """
        if self.gradient:
            pretty_gradient_tag = soup.find(id="prettyGradient")
            if pretty_gradient_tag is not None:
                hashed_name = hashlib.sha1(name.encode("utf-8")).hexdigest()
                color_one, color_two, color_three = (
                    color_map.get(pronouns, self.default_color),
                    "c" + hashed_name[:5],
                    "c" + hashed_name[5:10],
                )

                top_left = soup.find(id="topLeft")
                top_left["style"] = top_left["style"].replace(
                    "stop-color:#ff0000", "stop-color:#{}".format(color_one)
                )

                middle = soup.find(id="middle")
                middle["style"] = middle["style"].replace(
                    "stop-color:#00cc99", "stop-color:#{}".format(color_two)
                )

                bottom_right = soup.find(id="bottomRight")
                bottom_right["style"] = bottom_right["style"].replace(
                    "stop-color:#ff99ff", "stop-color:#{}".format(color_three)
                )

        """
        write the created/rendered svg to the output file so that you can admire your name tag in inkscape!
        """
        output_svg = open(output_file, "w")
        output_svg.write(str(soup))
        return output_file
