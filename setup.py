import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
        name="fio-plot",
        version="1.0.28",
        author="louwrentius",
        description="Create charts from FIO storage benchmark tool output",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/louwrentius/fio-plot/", 
        packages=setuptools.find_packages(),
        install_requires=['numpy','matplotlib','Pillow', 'pyan3', 'pyparsing'],
        include_package_data=True,
        package_data={'bench_fio': ['templates/*.fio',
                                 'scripts/*.sh']},
        entry_points = {
            'console_scripts': [
                'fio-plot = fio_plot:main',
                'bench-fio = bench_fio:main'
            ],
        },
        scripts=['bin/fio-plot', 'bin/bench-fio'],
)
