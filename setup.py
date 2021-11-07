import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="webpage-compressor",
    version="0.0.4",
    author="Lucas Maillet",
    author_email="loucas.maillet.pro@gmail.com",
    description="Web Page Compressor to create one page website.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LoucasMaillet/WPC/edit/main",
    project_urls={
        "Bug Tracker": "https://github.com/LoucasMaillet/WPC/edit/main/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: Unix",
        "Operating System :: Microsoft :: Windows",
    ],
    scripts=['./wpc'],
    package_dir={"webpage-compressor": "src"},
    packages=["webpage-compressor"],
    install_requires=[
        "python-datauri >=1.0.0",
    ],
    python_requires=">=3",
)
