Installed pygit2 v0.22.3 manually on the jessie.
Installed meson to run test_hotdoc
Installed ninja for the same reason
Installed libgirepository1.0-dev and gobject-introspection

As a different user / group is used, I had to chown the virtualenv
and mkdir /srv/docs.apertis.org/.python-eggs and chown it too.

Get flask-social-blueprint here : https://github.com/MathieuDuponchelle/flask-social-blueprint/tree/redirect
pending review of the remaining patch

Don't forget to call manage.py initdb in hotdoc_server

Had to install facebook from git too, as the last pip version is way too old
