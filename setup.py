import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
    
setuptools.setup(
    name = 'ScraperFC',
    version = '0.0.7',
    author = 'Owen Seymour',
    author_email = 'osmour043@gmail.com',
    description = 'Package for scraping soccer data from a variety of sources.',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/oseymour/ScraperFC',
    packages = setuptools.find_packages(include=['ScraperFC', 'ScraperFC.*']),
#     py_modules=['FBRef', 'FiveThirtyEight','ScraperFC','shared_functions','Understat'],
    keywords = ["soccer","football","Premier League","Serie A",
                "La Liga","Bundesliga","Ligue 1"],
    classifiers = [
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent'
    ],
    python_requires = '>=3.6'
)
  