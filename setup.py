import setuptools

setuptools.setup(
    name="seisclient",
    version="0.0.1",
    author="Liang Ding",
    author_email="myliang.ding@mail.utoronto.ca",
    description="Python package to request accurate 3D Greens' function and synthetic waveform from SeisCloud.",
    long_description="Python package to request accurate 3D Greens' function and synthetic waveform from SeisCloud.",
    long_description_content_type="text/markdown",
    url="https://seis.cloud",
    project_urls={
        "Bug Tracker": "https://github.com/Liang-Ding/seisclient/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    keywords=[
        "seismology"
    ],
    # package_dir={"": "seisclient"},
    python_requires='>=3.6.0',
    install_requires=[
        "numpy", "scipy", "obspy",
        "h5py", "seisgen"
    ],
    # packages=setuptools.find_packages(where="seisclient"),
    packages=setuptools.find_packages(),
)
