A customizable name tag generator.

Try it out live at https://nametags.tantemalkah.at

# Intro

This project grew in the context of the [Feminist Python Meetups](https://feminist-python.diebin.at) in Vienna.
Check out the [name-tags](https://github.com/feminist-python-meetup/name-tags) repo
for the original name tag generator written by Saara and Zoé, which we build on
here. There you also find more infos on usage and background for the standalone
name tag generator.

This project is basically a REST API wrapper around this name tag generator.
Additionally we want to provide a simple web form for everyone to be able
to quickly generate a name tag for themselves.

This is all written not for efficiency but for accessibility to people who are
probably new to Python or Flask and want to know how this works.

# Starting it locally

This is all designed to run on a current version of Debian or Ubuntu Linux.

To start this web service locally, just clone this repository and create a
python virtual environment with the name of the virtual environment being
`venv` (you can also choose something else, but then you have to change the
first line in `server.py` if you want to start the script directly from the
shell).

You can do this with either:
```bash
virtualenv venv
```
or:
```bash
python3 -m venv venv
```
This depends on what you have installed.

Then start the virtual environment and install all the dependencies:
```bash
source venv/bin/activate
pip3 install -r requirements.txt
```

Now you are good to go. Just start the server:
```bash
./server.py
```

# Deployment to a (public) web server

This is a bit more tricky. I'll describe how to do that on a plain and fresh minimal
Debian Stretch with Apache2 and _mod_wsgi_ installed. For that I followed the
[mod_wsgi Deployment Guide](http://flask.pocoo.org/docs/1.0/deploying/mod_wsgi/)
from the Flask documentation.

To get the server running clone this repository into your `/var/www/html` folder.
After you have enabled _mod_wsgi_ you need to change the `/etc/apache2/sites-enabled/000-default.conf`
config file to this:
```
<VirtualHost *:80>
        ServerName nametags

        WSGIDaemonProcess server user=jackie group=jackie threads=5
        WSGIScriptAlias / /var/www/html/server.wsgi

        <Directory /var/www/html>
                WSGIProcessGroup server
                WSGIApplicationGroup %{GLOBAL}
                Require all granted
        </Directory>
</VirtualHost>
```

Of course you can switch the name of the server in the `ServerName` directive
to your domain. But in my case I installed this system in a virtual machine.
On the host machine I have a Apache2 VirtualHost running as a proxy. This way
I can provide the whole site over secure `https` and use my Lets Encrypt
configuration, which I have already set up there, to obtain the SSL certificate.

I suggest using some similar approach or either changing the configuration in
order to support `https`.

# Roadmap

Things that are on the list to be implemented next (without any particular ordering):

* better handling of url_root (i.e. for initialisation of the first item)
* check if we catch everything that can be caught (e.g. with open)
* make data persistent with database
* implement DELETE on single name tags, with a token only the generating person gets
* implement some auto cleanup method (which deletes tags after certain amount of time)
* implement methods to provide own tag templates and color mappings
* add support for PNG and PDF output with scaling options
