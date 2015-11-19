from setuptools import setup

from webhook_handler import __version__, __doc__, WHHResource

setup(
    name = "webhook-handler",
    version = __version__,
    author = 'Stuart Fable',
    author_email = 'stuart.fable@gmail.com',
    license = 'MIT',
    keywords = 'webhook service twisted',
    description = WHHResource.__doc__,
    long_description = __doc__,
    url = 'https://github.com/sfable/webhook-handler',
    download_url = 'https://github.com/sfable/webhook-handler/archive/master.zip',
    py_modules = ['webhook_handler'],
    install_requires = [
        'sh',
        'Twisted'
    ],
    zip_safe = True,
    entry_points = {
        'console_scripts': ['webhook-handler=webhook_handler:main']
    },
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4'
    ]
)
