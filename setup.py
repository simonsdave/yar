from setuptools import setup

setup(
    name="yar",
    packages=[
        "yar",
        "yar.util",
        "yar.app_server",
        "yar.auth_server",
        "yar.key_server",
        "yar.key_store",
        # see "data_files" comment on why the next shouldn't be here
        "yar.key_store.design_docs",
    ],
    scripts=[
        "bin/app_server",
        "bin/auth_server",
        "bin/key_server",
        "bin/key_store_installer",
    ],
    install_requires=[
        "httplib2==0.8",
        "jsonschema==1.3.0",
        "tornado==3.0.1",
        "python-keyczar==0.71c",
        "python-memcached==1.52",
#       "tornado-memcache==1.0",
    ],
    dependency_links=[
#       "http://github.com/dpnova/tornado-memcache/tarball/master#egg=tornado-memcache",
    ],
    # MANIFEST.in in same directory as this setup.py should contain
    # a single line:
    #   include yar/key_store/design_docs/creds.json
    # data_files = [
    #     (key_store_package_dir, ["yar/key_store/creds.json"]),
    # ],
    version=1.0,
    description="yar",
    author="Dave Simons",
    author_email="simonsdave@gmail.com",
    url="https://github.com/simonsdave/yar"
)
