# Python Project Template

![Sea-Bird Logo](https://www.seabird.com/mdf_cb6d67ba3dcf931f6a6394cdc677d16018/en/seabird_com/images/header-logo.png "Sea-Bird logo image")

[This a crude fork of this PyPA sample project.][pypa src]

Here's a template for your Python project with a few tools working.
Reconfigure according to your needs.

Here's a new project checklist:
1. Create a new repository using this repository as a template.
1. Clone your new repository to your workspace.
1. Set your import name by renaming the directory `src/packageimportname`. The import name is used in Python code.
1. Set your distribution name by setting the project name in the `pyproject.toml` file. The distribution name is used with pip. I advise [normalizing your import name][norm] and prepending `sbs-`.
1. Install your package for development by calling `python -m pip install -e .` in the project directory. This will also install the necessary development tools to your Python environment.
1. Confirm the distribution installation by reading the `python -m pip list` output.
1. Test the ability to import by calling `python -c "import packageimportname"`. No exception should be thrown.
1. Test the ability to build by calling `python -m build` in the project directory. This should create a `dist` directory containing the wheel file.
1. Test the unit testing demo by calling `python -m pytest` in the project directory.
1. Edit the environment list in `tox.ini` based on available Python versions. Check your versions in Windows by calling `py -0`.
1. Test tox by calling `python -m tox` in the project directory. This should build, install, and test in virtual environments for all specified Python versions.
1. Update this `README.md`.
1. Update LICENSE.txt. The default is an MIT license. Do not use the MIT license for proprietary software.
1. Commit often.

## Github Actions

The `.github/workflows` directory contains a working Github workflow in `test.yml` which will test across interpreter versions and operating systems as part of the pull request process.

## Project Structure

The [src layout][src v flat] is used to enforce editable installation and prevent workspace code from conflicting with environment code.
Remember that the `src` directory should always only contain one subdirectory. That subdirectory is your package!

[packaging guide]: https://packaging.python.org
[distribution tutorial]: https://packaging.python.org/tutorials/packaging-projects/
[pypa src]: https://github.com/pypa/sampleproject
[norm]: https://packaging.python.org/en/latest/specifications/name-normalization/
[pytest]: https://docs.pytest.org/en/7.4.x/
[tox]: https://tox.wiki/en/4.11.3/
[src v flat]: https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/
