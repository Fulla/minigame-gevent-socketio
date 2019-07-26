#!/usr/bin/env python

from gevent import monkey
from socketio.server import SocketIOServer
# import django.core.handlers.wsgi
import os
import sys

monkey.patch_all()

from django.core.wsgi import get_wsgi_application


try:
    import geventiotest.settings
except ImportError:
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

PORT = 9000



# app = django.core.handlers.wsgi.WSGIHandler()

sys.path.insert(0, os.path.join(geventiotest.settings.BASE_DIR, "apps"))


if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE','geventiotest.settings')
    app = get_wsgi_application()
    print('Listening on port 9000 and on port 843 (flash policy server)')
    SocketIOServer(('0.0.0.0', PORT), app, resource="socket.io", policy_server=True,
        policy_listener=('0.0.0.0', 10843)).serve_forever()

# if __name__ == '__main__':
#     print 'Listening on port 9000 and on port 843 (flash policy server)'
#     SocketIOServer(('0.0.0.0', PORT), app, resource="socket.io").serve_forever()
