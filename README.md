# Configurable Webhook Handler

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
            {"fmt": "{obj[other_key][0]}"}
        ],
        "run": [
            {
                "args": [
                    "/tmp/newfile.json"
                ],
                "command": "tee",
                "json_in": true
            },
            {
                "args": [
                    "/tmp/{obj[repository][name]}"
                ],
                "command": "touch"
            }
        ]
    }

## CLI Options

There are many things that can be overridden. For more cli options:

    twistd --help
    twistd web --help

For more information head to http://twistedmatrix.com/documents/
