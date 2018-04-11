from distutils.core import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='landsatxplore',
    version='0.1',
    description='Search and download Landsat scenes from EarthExplorer.',
    packages=['landsatxplore',],
    license='MIT',
    long_description=readme(),
    keywords='remote_sensing landsat satellite',
    url='https://github.com/yannforget/landsatxplore',
    author='Yann Forget',
    author_email='yannforget@mailbox.org',
    install_requires=[
        'requests',
        'tqdm',
        'click'
    ],
    include_package_data=True,
    zip_safe=False,
    entry_points="""
        [console_scripts]
        landsatxplore=landsatxplore.cli:cli
    """,
)