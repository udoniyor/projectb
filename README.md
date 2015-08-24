# ProjectB

<p align="center">
  <img src="https://github.com/udoniyor/projectb/raw/master/logo.png" alt="ProjectB Logo"/>
</p>


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
If you are having trouble installing via pip, try installing scipy and numpy with package manager on UNIX based systems. For more details on how to
install SciPy stack on your machine look [here](http://www.scipy.org/install.html)

If you are on Windows and having troubles with pip, try [Anaconda](http://continuum.io/downloads). It includes numpy and scipy, therefore
reducing the chances of running into an error.

Usage (GUI)
============
To invoke the Graphical User Interface, you need to type in following command into the command line:
	
		python -m projectb.start

This will launch the GUI of the framework. You may also specify the settings file to prefill the fields in the UI.

		python -m projectb.start /home/user/settingsfile.projectb

Your settings file can have any extension name, but for clarity purposes keep it simple and relevant. 

Usage (Command Line)
============
The framework can be executed via commandline, but you must specify a settings file. Settings file format is a CSV file, with one parameters per line. You will find the specification for the settings file in the next section. Alternatively, you may create a settings file via the GUI by exporting the settings defined in the UI. To invoke the command line, you simply add -cli to the command.

		python -m projectb.start /home/user/settingsfile.projectb -cli

Optionally, you can specify the output directory during the invokation.

		python -m projectb.start /home/user/settingsfile.projectb /home/user/outputhere/ -cli

It is adviced to provide an output directory, otherwise the framework will write to the directory called from. 

File Format Specification 
============
The Framework defines a simple CSV (Comma Separated Values) as a file format which specifies the parameters of the Bayesian Optimization and model details; such as the input file, command and the output directory. 

The file structure follows a simple pattern, each line stores only one parameter. First value is the parameter key, for example “policies”; followed by the value of the parameter, separated by a comma such as “ei” (expected improvement policy). The structure allows having multiple values for each parameter, but this is limited only to the kernel and policy parameters. The limitation is imposed by the graphical user interface, where only multiple kernel and policies can be selected.

Another exception is the bounds parameter. The bounds can be described by stating the key "bounds", followed by a comma, lower bound, comma and upper bound. The key can be defined multiple times to specify many bounds. For example if function has three inputs with bounds between 0 and 100, it should be specified as follows:

		...
		bounds,0,100
		bounds,0,100
		bounds,0,100
		...

In addition, to the parameters, the file format stores the data gathered during optimization or user pre-processed data. The order of the parameters does not matter, except for the data parameter. The data parameter must be defined last followed by the data where the second column is y values and starting from the 4th column are the x inputs. The purpose of the strict data column layout is to match the output of the framework. The framework, output is structured in a following way: time per iteration in seconds, objective value achieved at the iteration, mean calculated from the posterior for the point prior evaluation, variance calculated from the posterior for the point prior evaluation, followed by the input values separated via commas. 

You do not need to specify all the kays and parameters for the framework, most have reasonable default values. Only following are required for the framework: command, modelinput, modeloutput, and bounds. By default, the framework maximizes with EI policy and SE kernel for 150 iterations with sobol initialzer.

Basic Settings Spefication:
	
	Keys	|	Parameters
	command |	command line string to invoke the function
	modelinput | input file for the function. One parameter per line
	modeloutput | output file for the function.
	bounds | lowerbound,upperbound
	outputdir | directory to output the results to
	policies | ei,pi,ucb,thompson
	kernels | matern1,matern3,matern5,se
	iter | number of iterations
	objective | min/max
	solver | direct*/lbfgs 
	initializer | sobol/middle/uniform
	initializernum | number of samples to sample by the initializer
	recommender | latent/incumbent/observed
	normalize | True/False **


* Requires nlopt python library
** Normalize the bounds between 0 and 1. Experiments have shown normalizing the input helps
with performence of the lbfgs solver. Preferably, use direct solver without normalization. 
*** Dimension Scheduler is a technique to improve the performence of the Bayesian Optimization. 

Advanced Settings Specification:
	
	dims | If dimension scheduler enabled, number of dimensions per permutation
	dimscheudler | True/False ***
	mcmcburn | Burn number
	mcmcn | Number of GPs
	eixi | Exploration parameter for the EI policy
	pixi | Exploration parameter for the PI policy
	ucbxi | Exploration parameter for the UCB policy
	ucbdelta | Probability of that the upper bound holds
	thompsonn | number of Fourier components
	thompsonrng | Random seed

Following keys have python code snippets as parameters:
	
	Gaussian Process Settings:
	gpsf, gpmu, gpell, gpsn

	Hyper-prior Settings
	priorsnscale, priorsnmin, priorsfmu
	priorsfsigma, priorsfmin 
	priorella, priorellb
	priormumu, priormuvar

