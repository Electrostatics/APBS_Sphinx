# Sphinx Prototype
This is still very much in the prototype phase.  Beyond here there be monsters!

## Building the Beast
First off, you'll need Python 3.4.3.  Python 3.4 may work just as well, but I haven't tried.  You'll also need a C++11 compiler and CMake.

The process is anything but automagic, and we hope to fix that before too much longer.

7. `cd <sphinx_repo>/prototype/plugins/Geoflow/src`
7. `mkdir build`
7. `cd build`
7. `cmake ..`
7. `make`
7. `cp geoflow.so ../..`

## Running the Beast
From `<sphinx_repo>` try this:
`./apbs.py example/geoflow.apbs infile=example/imidazole.xyzr outfile=imidazole.txt`

You'll know it's done when you see `solv[iloop-1] = -3.5836` on stdout.  Ctrl-C to escape.  Yes, lame.  Yes, rough.  Yes prototype.  Yes, it works.

It just ran the geometric flow solver on *imidazole.xyzr* and printed some electrostatic information about the molecule into *imidazole.txt*.  It also (without you explicitly asking for it to do so) did the same for *diet.xyzr* and printed it's output to *diet.txt*.

Oh, there's this crazy *io.mc* file too, although there's not really much in it that's useful.

It's worth noting that the file *geoflow.apbs* is Python code, and that it's really just for playing with what's possible using Python to specify instructions.  In reality we may provide a file like it, but minus the hardcoded *diet* bits.

###This is important here
The main takeaway is that the user can use, on the command line, a **pre-written** APBS command file that takes named parameters and operates on what those parameters specify.  In this case, run the Geometric Flow solver on the *imidazole.xyzr* file and put the results in *imidazole.txt*.
###Thanks for paying extra-special attention

## Anatomy of the Beast
More to come.

## TODO
7. It should run asynchronously, but there's still some work to be done getting our plugins to cooperate and do that.
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
