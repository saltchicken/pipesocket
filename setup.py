from setuptools import setup, find_packages

# with open("README.md", "r", encoding="utf-8") as fh:
#     long_description = fh.read()

setuptools.setup(
    name='pipesocket',
    version='0.0.1',
    author='John Eicher',
    author_email='john.eicher89@gmail.com',
    description='Testing installation of Package',
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    url='https://github.com/saltchicken/pipesocket',
    # project_urls = {
    #     "Bug Tracker": "https://github.com/saltchicken/pipesocket/issues"
    # },
    # license='MIT',
    packages=find_packages(),
    install_requires=['websocket']
)