This is a fork of the original relion from https://github.com/3dem/relion/

It adds a new feature in the "relion_display" program to select classes and "Recenter and save" them. This function opens each selected class average one-by-one in a new GUI, waits for the user to mouse-click the center of the class average, and writes a new particles.star file with the user-inputed shifts accounted for in the rlnOriginX and rlnOriginY columns. Recentered classes are saved as "Select/jobXXX/particles-recenter-year-month-day--hour-minute-second.star" alongside the original particles.star file in the Select/jobxxx folder.

RELION
======


RELION (for REgularised LIkelihood OptimisatioN) is a stand-alone computer
program for Maximum A Posteriori refinement of (multiple) 3D reconstructions
or 2D class averages in cryo-electron microscopy. It is developed in the
research group of Sjors Scheres at the MRC Laboratory of Molecular Biology.

The underlying theory of MAP refinement is given in a [scientific publication](https://www.ncbi.nlm.nih.gov/pubmed/22100448)
. If RELION is useful in your work, please cite this paper.


The more comprehensive documentation of RELION is stored on the [Wiki](http://www2.mrc-lmb.cam.ac.uk/relion)

## Installation


More extensive options and configurations are available
[here](http://www2.mrc-lmb.cam.ac.uk/relion/index.php/Download_%26_install),
but the outlines to clone and install relion for typical use are made easy
through [cmake](https://en.wikipedia.org/wiki/CMake).

On ubuntu machines, installing cmake, the compiler, and additional dependencies (mpi, fftw) is as easy as:

```
sudo apt install cmake build-essential mpi-default-bin mpi-default-dev libfftw3-dev
```

On other systems it is typically just as easy, you simply have to modify "apt" to
the appropriate package manager. You will also need [git](https://en.wikipedia.org/wiki/Git), which is just as easy;

```
sudo apt install git
```


Once git and cmake are installed, relion can be easily installed through
```
git clone https://github.com/Rick-Baker/relion-recenter.git
cd relion
mkdir build
cd build
cmake -DCMAKE_INSTALL_PREFIX=/where/to/install/ ..
make -j4
make install
```
(NOTES: "/where/to/install/.." is typically "/usr/local/relion".
 Make sure you create this directory beforehand.
 Installing to that location requires sudo, so in this case be sure to use
 "sudo make install" instead of "make install" in the last step.)

These steps will download the source-code, create a build-directory,
then configure and build relion, and lastly install it to be generally
available on the system.


## Updating


RELION is intermittently updated, with both minor and major features.
To update an existing installation, simply use the following commands

```
cd relion
git pull
cd build
make -j4
make install    # (or "sudo make install")

```

## Known bug

If the user applied shift would place the center of the particle outside of the boundary of the micrograph, Relion will throw an errer during particle extraction. This will be fixed in a later update. Right now, the user can simply delete the offending particles from the particles-date-time.star file.
