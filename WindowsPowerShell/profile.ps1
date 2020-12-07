# Aaron Genovia [2020-07-15]
<#
												  Path Schematic

The path inside the square brackets ([ ]) is the path on the TFS server. The path inside the 
	
	
	
									< C:\Users\activebatch\Documents\WindowsPowerShell >
									[  $/Production/ActiveBatch/WindowsPowerShell	   ]
													   |
													   |
													   |
													   +---- C:\Users\activebatch\Documents\WindowsPowerShell\Dev_Scripts
#>

# setting profileRoot to the base path of invocation and get the parent path
# append this path to the environment to let the shell know where to source scripts
$profileRoot = (Split-Path -Parent $MyInvocation.MyCommand.Path)
$prodScripts = Join-Path -Path $profileRoot -ChildPath "Scripts"
$devScripts = Join-Path -Path $profileRoot -ChildPath "Dev_Scripts"
$prodPyScripts = "C:\Users\activebatch\Documents\Python\Scripts"
$devPyScripts = "C:\Users\activebatch\Documents\Python\Dev_Scripts"
$env:path += ";$prodScripts;$devScripts"

# add a default Powershell Module path
$psModulePath = "C:\Users\activebatch\Documents\WindowsPowerShell\Modules"
$env:PSModulePath += ";$psModulePath"

# add a default Python Module path
$pyModulePath = "C:\Users\activebatch\Documents\Python\Modules"
$env:Path += ";$pyModulePath"

# this will be necessary for the runpy script
$py36_env = "C:\Users\activebatch\AppData\Local\Programs\Python\Python36\VirtualEnvironments"
$py37_env = "C:\Users\activebatch\AppData\Local\Programs\Python\Python37\VirtualEnvironments"
$py38_env = "C:\Users\activebatch\AppData\Local\Programs\Python\Python38-32\VirtualEnvironments"

# these are globals, as a default, python should NEVER install anything on the base env
# these ensure that you are always at least inside a virtual environment called "landing"
# before you can pip install anything; however, installing too many non-administrative
# packages in landing is also not advised and you should always create new environments for 
# projects requiring complex dependencies. Read more in my documentation on Virtual Envs

New-Alias py36 "C:\Users\activebatch\AppData\Local\Programs\Python\Python36\python.exe"
New-Alias py37 "C:\Users\activebatch\AppData\Local\Programs\Python\Python37\python.exe"  # choosing this as base python
New-Alias py38 "C:\Users\activebatch\AppData\Local\Programs\Python\Python38-32\python.exe"

New-Alias py36_landing "C:\Users\activebatch\AppData\Local\Programs\Python\Python36\VirtualEnvironments\py36_landing\Scripts\activate.ps1"
New-Alias py37_landing "C:\Users\activebatch\AppData\Local\Programs\Python\Python37\VirtualEnvironments\py37_landing\Scripts\activate.ps1"
New-Alias py38_landing "C:\Users\activebatch\AppData\Local\Programs\Python\Python38-32\VirtualEnvironments\py38_landing\Scripts\activate.ps1"

# set the tfs alias
New-Alias tf "C:\Program Files (x86)\Microsoft Visual Studio\2017\Professional\Common7\IDE\CommonExtensions\Microsoft\TeamFoundation\Team Explorer\TF.exe"

# I'm setting python 3.7 as the base landing for everybody
# If it ever gets messed up due to improper package management, then all we need 
# to do is rebuild landing for python 3.7 (alias py37) located in $py37_env
py37_landing