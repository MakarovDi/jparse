
if __name__ == '__main__':
    # import info without executing __init__
    import sys
    sys.path.append('uplot')
    import info
    import setuptools

    setuptools.setup(
        name='jparse',
        version=info.__version__,
        description=info.__description__,
        author=info.__author__,
        author_email=info.__email__,
        license=info.__license__,
        url='https://github.com/MakarovDi/jparse',
        packages=setuptools.find_namespace_packages(),
        python_requires='>=3.7'
    )