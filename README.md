# ProjectB


![ProjectB Logo](https://github.com/udoniyor/projectb/raw/master/logo.png)


ProjectB is a graphical user interface, which allows untrained users to optimize any model that can be
invoked through a command line. The GUI is built on top of a modular Bayesian Optimization library, [pybo](https://github.com/mwhoffman/pybo),
which includes most common acquisition functions and kernels and more.

Installation
============

The easiest way to install this package is by running

    pip install -r https://github.com/udoniyor/projectb/raw/master/requirements.txt
    pip install git+https://github.com/udoniyor/projectb.git

The first line installs any dependencies of the package and the second line
installs the package itself. Alternatively the repository can be cloned directly
in order to make any local modifications to the code. In this case the
dependencies can easily be installed by running

    pip install -r requirements.txt

from the main directory.

Tips
============
If you are having trouble installing via pip, try installing scipy and numpy prior the commands. For more details on how to
install SciPy stack on your machine look [here](http://www.scipy.org/install.html)

If you are on Windows and having troubles with pip, try [Anaconda](http://continuum.io/downloads). It includes numpy and scipy, therefore
reducing the chances of running into an error.

Usage (GUI)
============
To invoke the Graphical User Interface, you need to type in following command into the command line:
	
		python -m projectb

This will launch the GUI of the framework. You may also specify the settings file to prefill the fields in the UI.

		python -m projectb /home/user/settingsfile.projectb

Your settings file can have any extension name, but for clarity purposes keep it simple and relevant. 

Usage (Command Line)
============
The framework can be executed via commandline, but you must specify a settings file. Settings file format is a CSV file, with one parameters per line. You will find the specification for the settings file in the next section. Alternatively, you may create a settings file via the GUI by exporting the settings defined in the UI. To invoke the command line, you simply add -cli to the command.

		python -m projectb /home/user/settingsfile.projectb -cli

Optionally, you can specify the output directory during the invokation.

		python -m projectb /home/user/settingsfile.projectb /home/user/outputhere/ -cli

It is adviced to provide an output directory, otherwise the framework will write to the directory called from. 

File Format Specification
============
 The file format the framework uses is a CSV based file. Each line is used for one parameter. First column are the key words, and the second
 and further columns are the parameters for the corresponding parameter. 


To Do
============
 - Finalize Tutorial 
 - Update CLI module
 - Add comments
 - Unit tests
 - Update data file parser