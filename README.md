# Sphinx Prototype
This is still very much in the prototype phase.  Beyond here there be monsters!

## Building the Beast
First off, you'll need Python 3.4.3.  Python 3.4.x may work just as well, but I haven't tried.  You'll also need a C++11 compiler and CMake (3.2.x).

### Install Python Virtual Environment, install dependencies and generate JSON schema from PDBx/mmCIF star file
1. `cd <sphinx_repo>/prototype`
2. `python3 bootstrap.py`
3. `source sphinx-env/bin/activate`

### Build the Geometric Flow plugin
7. `cd <sphinx_repo>/prototype/plugins/Geoflow/src`
7. `mkdir build`
7. `cd build`
7. `cmake ..`
7. `make`
7. `cp geoflow.so ../..`
*Check the README file in the Geoflow/src directory if building on Windows or OSX*

## Testing the Beast
We are currently using Nose to run the unit tests.  From the `prototype` directory just run `nosetests`.

## Running the Beast
From `<sphinx_repo>/prototype` try this:
`python apbs.py example/geoflow.apbs infile=example/imidazole.xyzr outfile=imidazole.txt`

It just ran the geometric flow solver on *imidazole.xyzr* and printed some electrostatic information about the molecule into *imidazole.txt*.

Oh, there's this crazy *io.mc* file too, although there's not really much in it that's useful.

It's worth noting that the file *geoflow.apbs* is Python code, and that it's really just for playing with what's possible using Python to specify pipelines.  Whether or not we continue to use the same Python syntax is still up in the air.  It may make more sense to create a DSL for specifying pipelines.

###*This is important here*
The main takeaway is that \*.apbs files specify *plugin pipelines*.  A typical user can specify, on the command line, a **pre-written** APBS command file (\*.apbs) that takes named parameters and operates on what those parameters specify.  In this case, run the Geometric Flow solver on the *imidazole.xyzr* file and put the results in *imidazole.txt*.

An atypical user may choose to create their own pipeline files, and thus gain much more control over how the data is processed.  We provide different levels of control to suit both typical and power users.
###*Thanks for paying extra-special attention*

## Running Solvers in Parallel
There is a really simple example of running two geoflow jobs in example/dual-geoflow.apbs.  It may be run as above.  It will solve the imidazole molecule, as well as *diet.xyzr*.  The latter is hardcoded to print it's results to *diet.txt*.  This example shows that two solvers may run concurrently, as well as how it's possible to hardcode information (the input and output files) into a command file (.apbs).

## Anatomy of the Beast
There is a [work-in-progress white paper](https://github.com/Electrostatics/APBS_Sphinx/wiki/Sphinx%20White%20Paper) on Sphinx that dwells on some of the details.

## TODO
7. The Geometric Flow plugin needs a means of taking parameters.  I suggest that all the solver plug-ins take a parameter file.  Something like the .in files of yore.
7. Remove all the debug junk that's printed in Geoflow.
7. Get the Semantic Databus idea into working shape
7. Validate plug-in pipelines
7. Extend this command line mode with something more user friendly.  Hey maybe extend that *SillyServer* plugin (what's that there for anyway?) to spawn a browser and connect to Sphinx, thus providing the user a GUI?  What?  That's crazy talk!
7. Moar solvers!
...
7. There are a lot of TODO's in the source code.
...
7. *Ad nauseum*
