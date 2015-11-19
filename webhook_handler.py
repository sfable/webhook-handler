'''# Configurable Webhook Handler

Takes a webhook call from a service and handles it.

## Installation

    pip install --user https://github.com/sfable/webhook-handler/archive/master.zip

## Basic Usage

It is built as a twisted resource class. It is run by calling:

    webhook-handler -n

Or it can be run with twistd:

    twistd -n web --class webhook_handler.WHHResource

By default this will start a web server on 0.0.0.0:8080 and a twistd.pid file in current working directory.
To have it run in daemon mode simply remove the -n flag.

## Configuation

Configuation is applied using the WEBHOOK_CFG environment variable.

    WEBHOOK_CFG=/path/to/config.json

### Example

To configure the handlers create a JSON config file:

    {
        "dump": [
            {
                "fnfmt": "/tmp/{method}.{obj[json_object_key]}.log"
            }
        ],
        "print": [
            {"fmt": "{headers[Content-Type]}"},
            {"fmt": "{obj[other_key][-1]}"}
        ],
        "run": [
            {
                "args": [
                    "-p",
                    "/tmp/{path}"
                ],
                "command": "mkdir"
            },
            {
                "args": [
                    "/tmp/{path}/newfile.json"
                ],
                "command": "tee",
                "json_in": true
            }
        ]
    }

## CLI Options

There are many things that can be overridden. For more cli options:

    twistd --help
    twistd web --help

For more information head to http://twistedmatrix.com/documents/

'''
import os
import sh
import sys
import json
from twisted.web import resource
from twisted.python.log import msg, err

__version__ = '0.0.1'

default_cfg = {
    'print': {'fmt': '{obj[repository][name]}: {obj[push][changes][0][new][target][hash]}'},
    'dump': {
        'fnfmt': '{obj[repository][name]}.{obj[push][changes][0][commits][0][hash]}.log',
        'append': True
    },
    'run': {
        'command': 'echo',
        'args': ['{obj[repository][name]}'],
        'json_in': False
    }
}

def do_nothing(cfg, **data):
    pass

def printer(cfg, **data):
    msg(cfg.get('fmt', default_cfg['print']['fmt']).format(**data))

def dumper(cfg, **data):
    name = os.path.expanduser(cfg.get('fnfmt', default_cfg['dump']['fnfmt']).format(**data))
    write_mode = cfg.get('append', default_cfg['dump']['append']) and 'a' or 'w'
    with open(name, write_mode) as fp:
        json.dump(data['obj'], fp)

def runner(cfg, **data):
    cmd = sh.Command(cfg.get('command', default_cfg['run']['command']).format(**data))
    args = [a.format(**data) for a in cfg.get('args', default_cfg['run']['args'])]
    if cfg.get('json_in', default_cfg['run']['json_in']):
        cmd(*args,_in=json.dumps(data['obj']))
    else:
        cmd(*args)

default_handlers = {
    'dump': dumper,
    'null': do_nothing,
    'print': printer,
    'run': runner
}


def handle_request(cfg, method, request, handlers=default_handlers, debug=False):
    try:
        if request.appRootURL is None:
            request.rememberRootURL()
        assert request.getHeader('Content-Type').lower()=='application/json'
        data = {
            'env': os.environ,
            'obj': json.load(request.content),
            'req': request,
            'method': method,
            'path': '/'.join(request.postpath),
            'headers': request.getAllHeaders()
        }
        for k, v in cfg.items():
            handler = handlers.get(k, do_nothing)
            for cfg in v:
                handler(cfg, **data)
    except Exception as e:
        if debug:
            err("Error: {0!r}".format(e))
    return 'OK\n'

def load_config_file(filename, config=None, handlers=default_handlers):
    if config is None:
        config = {}
    with open(filename) as fp:
        cfg = json.load(fp)
        for k,v in cfg.items():
            if k in handlers:
                if isinstance(v, list):
                    config[k] = v
                else:
                    config[k] = [v]
    return config

class WHHResource(resource.Resource):
    """Configurable JSON POST webhook receiver service."""
    isLeaf = True

    def __init__(self, 
                 cfg=None,
                 filename=os.environ.get('WEBHOOK_CFG', None),
                 handlers=default_handlers,
                 debug=os.environ.get('WEBHOOK_DEBUG', False),
                 post_only=True
                 ):
        resource.Resource.__init__(self)
        self.cfg = cfg or {}
        self.debug = debug
        self.handlers = handlers
        self.post_only = post_only
        if filename and os.path.exists(filename):
            if self.debug:
                print('Loading Config from {0}'.format(filename))
            load_config_file(filename, self.cfg, self.handlers)
            if self.debug:
                print('done.')
        elif self.debug and not self.cfg:
            self.cfg['print'] = [default_cfg['print']]

    def render_DELETE(self, request):
        if self.post_only:
            return 'OK\n'
        return handle_request(self.cfg, r'DELETE', request)

    def render_GET(self, request):
        if self.post_only:
            return 'OK\n'
        return handle_request(self.cfg, r'GET', request)

    def render_POST(self, request):
        return handle_request(self.cfg, r'POST', request)

    def render_PUT(self, request):
        if self.post_only:
            return 'OK\n'
        return handle_request(self.cfg, r'PUT', request)

def main(res='{0.__module__}.{0.__name__}'.format(WHHResource),args=list(sys.argv[1:])):
    if '--' in args:
        args[args.index('--')] = 'web'
    else:
        args = args+['web']
    sh.twistd(args+['--class',res],_out=sys.stdout,_err=sys.stderr)

if __name__ == '__main__':
    main('webhook_handler.WHHResource')
