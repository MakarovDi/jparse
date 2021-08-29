
if __name__ == '__main__':
    import setuptools

    setuptools.setup(name='jparse',
                     version='0.1.1',
                     description='JPEG structure and Exif metadata parsing library',
                     author='Dmitry Makarov',
                     author_email='makarovdmv@gmail.com',
                     url='https://github.com/MakarovDi/jparse',
                     packages=setuptools.find_namespace_packages(),
                     python_requires='>=3.7.0'
    )