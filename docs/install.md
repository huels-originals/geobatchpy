# How to install `geoapify`

## Install the package into your active environment

Install the latest release from public [PyPI](https://pypi.org/project/geobatchpy/):

```shell
pip install geobatchpy
```

Append a `==<version>` if you prefer an older release. Or install the latest development state from the master branch:

```shell
pip install git+https://github.com/huels-originals/geobatchpy.git
```

This package comes with a command line interface named `geobatch`. Verify the installation on the command line with

```shell
geobatch version
```

## Install the latest release into a Conda virtual environment

We recommend using virtual environments to avoid headaches down the road. The easiest way how to do this is by using
[Miniconda](https://docs.conda.io/en/latest/miniconda.html). It works with Linux, Mac, and Windows. 

Assuming you have installed the `conda` command, create a file called `environment.yaml` with the following content:

```
# your environment.yaml
name: my-env  # pick any name you like
channels:
  - defaults
dependencies:
  - python=3.9
  - pip
  - pip:
      - geobatchpy
      # Add optional dependencies below, e.g.:
      - geopandas
```

From within the same directory hosting this file, execute

```shell
conda env create -f environment.yaml
```

Wait for the installation to complete and activate the environment by

```shell
conda activate my-env
```
You can verify the installation by printing the installed version with `geobatch version`. If you are done, deactivate the environment
with `conda deactivate`.

See the official documentation if you want to know more about
[Conda environments](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).
