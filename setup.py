from setuptools import setup, find_packages

setup(
    name="eb-fgt-ofgt-crps4",
    version="0.1.0",
    description="Exchange bias analysis in FGT/O-FGT/CrPS4 heterostructures",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
        "scipy",
        "h5py",
    ],
    python_requires=">=3.8",
)
