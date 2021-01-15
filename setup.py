import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()



setuptools.setup(name='flame_db',
      version='0.32',
      description='Causal Inference Covariate Matching',
      long_description=long_description,
      keywords='Causal Inference Matching Econometrics Data Machine Learning FLAME DAME',
      url='https://github.com/almost-matching-exactly/DAME-FLAME-Python-Package',
      author='Neha Gupta',
      author_email='neha.r.gupta@duke.edu',
      license='MIT',
      packages=setuptools.find_packages(),
      install_requires=[
          'scikit-learn>=0.21.3',
          'scipy>=0.14',
          'pandas>=0.11.0',
          'numpy>=1.6.1'
      ],
      extras_require={
        "postgreSQL":  ["psycopg2>=2.8.6"],
        "sqlserver":  ["pyodbc>=4.0.0"],
        "mySQL":  ["mysql-connector>=1.1.0","mysql-connector-python>=8.0.22"]
    }
     long_description_content_type="text/markdown",
     classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    )
