from setuptools import setup, find_packages

# Parse version number
with open('tgraphics/__init__.py') as f:
    info = {}
    for line in f.readlines():
        if line.startswith('TGRAPHICS_VERSION'):
            exec(line, info)
            break

extra_requires = dict(
    pygame = ['pygame'],
    pyglet = ['pyglet'],
)

extra_requires['all'] = list({dep for deps in extra_requires.values() for dep in deps})

setup_info = dict(
    name='tgraphics',
    author='TheerapakG',
    version=info['TGRAPHICS_VERSION'],
    description="TheerapakG's GUI library",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='Other/Proprietary License',

    # Package info
    packages=['tgraphics'] + ['tgraphics.' + pkg for pkg in find_packages('tgraphics')],

    extras_require=extra_requires,
    python_requires='>=3.8.0',

    zip_safe=True,
)

setup(**setup_info)
