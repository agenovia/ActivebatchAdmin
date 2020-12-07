<#
AaronG 2020-04-20

-----
runpy 
    <0> -FilePath (required) [string]
            # this is the path to the python script to run
    <1> -Version (required) [36, 37, 38]
            # (36 -> 3.6.6)  (37 -> 3.7.7)  (38 -> 3.8.2) 
            # support for more versions can be configured if needed
    <2> -EnvName (optional) [string]
            # if provided, genv.ps1 will try to activate this environment using the proper python version
            # if not provided, genv.ps1 will try to activate the __auto__ environment and prompt user
            #    for overwrite if __auto__ is already populated
#>


Param (
    [Parameter(Position=0, Mandatory=$true)] # try pipelining, for passing objects straight from WMI, might be useful for later
    [string]$ScriptName, # this is the path to the python script we want to run

    [Parameter(Position=1, Mandatory=$true)]
    # these are the versions currently supported by genv as of 20200424
    # (36 -> 3.6.6)  (37 -> 3.7.7)  (38 -> 3.8.2) 
    [ValidateSet(36, 37, 38)] # must be one of these
    [int]$Version, # this is the python version to run in, must correspond to a python version that is installed in the execution machine

    [Parameter(Position=2, Mandatory=$false)] 
    [string]$EnvName, # this is the name of a valid conda environment that needs to be set up prior to running a script

    [Parameter(Position=3, Mandatory=$false)] 
    [int[]]$SuccessCodes = @(), # this is the name of a valid conda environment that needs to be set up prior to running a script

    [Parameter(Position=4, Mandatory=$false)] 
    [string[]]$Params= @(), # this is the name of a valid conda environment that needs to be set up prior to running a script

    [Parameter(Position=5, Mandatory=$false)] 
    [switch]$Dev # this is a toggle, if $Dev is toggled, then the script is searched in the $pyDevScripts directory
)


# import the logger function
Import-Module OTK

<#
These paths are defined in the $profileRoot (as of 2020-06-02) and will serve as the virtual landing environment for all scripts that are ran 
with the specified version:
$py36_env = "C:\Users\activebatch\AppData\Local\Programs\Python\Python36\VirtualEnvironments"
$py37_env = "C:\Users\activebatch\AppData\Local\Programs\Python\Python37\VirtualEnvironments"
$py38_env = "C:\Users\activebatch\AppData\Local\Programs\Python\Python38-32\VirtualEnvironments"

FYI, I'm using aliases to map to the landing environments so I have a way to quickly change wherever they are using just the $profileRoot file
#>
if ($Version -eq 36) 
{
    py36_landing
    $env_dir = $py36_env
}
elseif ($Version -eq 37) 
{
    py37_landing
    $env_dir = $py37_env
}
elseif ($Version -eq 38) 
{
    py38_landing
    $env_dir = $py38_env
}

class GENV 
{
    # turning this into a class simply so the return buffer does not get polluted
    [string] GenerateEnv([string]$Path, [string]$EnvDir, [string]$EnvName, [boolean]$AutoDir) 
    {
        $Requirements = Join-Path -Path $Path -ChildPath 'requirements.txt'
		consoleLog(("New requirements file {0}" -f $Requirements))

        # do we want to automatically create an environment for this script?
        if ($AutoDir) 
        {
            $install_dir = Join-Path -Path $EnvDir -ChildPath '__auto__' | Join-Path -ChildPath $EnvName    
        }
        else 
        {
            $install_dir = Join-Path -Path $EnvDir -ChildPath $EnvName
        }

        # this is what we invoke when we want to activate the environment
        $activator = Join-Path -Path $install_dir -ChildPath 'Scripts' | Join-Path -ChildPath 'activate.ps1'

        # does the installation directory already exist?
        if (Test-Path $install_dir) 
        {
            try {
                $old_req = (Join-Path -Path $install_dir -ChildPath 'requirements.txt')
                $old_hash = Get-FileHash -Path $old_req -Algorithm "MD5"
                $new_hash = Get-FileHash -Path $Requirements -Algorithm "MD5"
            }
            catch {
                throw ("The requirements.txt file is either missing in {0} or {1}" -f $Path, $install_dir)
            }
            
			consoleLog(("Old requirements file {0}" -f $old_req))

            # if the file requirements have changed based on the hash
            if ($old_hash.Hash -ne $new_hash.Hash) 
            {
                & $activator | Out-Null # activate existing environment
                consoleLog(("Uninstalling old packages..."))
                & "pip" "uninstall" "-r" ("`"{0}`"" -f $old_req) "-y" | Out-Null # uninstall all the old packages
                consoleLog(("Installing new packages..."))
                & "pip" "install" "-r" ("`"{0}`"" -f $Requirements) | Out-Null # install new requirements
                Copy-Item -Path $Requirements -Destination $old_req
                Invoke-Expression "deactivate"# exit environment
            }

        }
        # else if installation directory doesn't already exist
        else 
        {
			consoleLog(("Creating new environment {0}" -f $EnvName))
			& "py" "-m" "virtualenv" ("`"{0}`"" -f $install_dir) | Out-Null  # this is the cleanest way I've found to run a powershell script
            & $activator | Out-Null
            consoleLog(("Installing new packages..."))
			& "pip" "install" "-r" ("`"{0}`"" -f $requirements) | Out-Null
            Copy-Item -Path $Requirements -Destination $install_dir -Force # create a requirements file
            Invoke-Expression "deactivate"
            consoleLog(("The Virtual Environment {0} is ready!" -f $EnvName))
        }
        # pass the activator command back
        return $activator
    }
}


<# 
Pass the -EnvName command line parameter to genv and it will do the heavy lifting and return the activation script path
GENV will do checks such as attempting to find existing environments and automatically creating new ones if they don't
#>

if (-Not $Dev) {
    $FilePath = Join-Path -Path $prodPyScripts -ChildPath $ScriptName | Join-Path -ChildPath 'main.py'
}
else {
    $FilePath = Join-Path -Path $devPyScripts -ChildPath $ScriptName | Join-Path -ChildPath 'main.py'
}

# was an environment name provided?
if (-Not $PSBoundParameters.ContainsKey('EnvName')) { # if not provided
    $EnvName = (Get-Item $FilePath).Directory.Name  # directory of script file
    $AutoDir = $true  # use AutoDir
}
else { # if provided
    $AutoDir = $false
}

$Requirements = (Get-Item $FilePath).Directory.FullName # parent dir of script

try {
	$virtual_environment = [GENV]::new()
	$activator = $virtual_environment.GenerateEnv($Requirements, $env_dir, $EnvName, $AutoDir)
}
catch {
    consoleLog("Error on virtual environment creation")
	throw
}

try {
	consoleLog(("Activating environment '{0}'..." -f $EnvName))
	consoleLog(($activator))
	& $activator
}
catch {
    consoleLog("Error on virtual environment activation")
	throw
}


try {
	consoleLog(("Running file {0}" -f $FilePath))
	py $FilePath $Params
    if ($LASTEXITCODE -ne 0 -and $LASTEXITCODE -notin $SuccessCodes){
        Write-Error ("The python file {0} has exited with a non-success code of {1}" -f $FilePath, $LASTEXITCODE)
        exit $LASTEXITCODE
    }
    consoleLog(("{0} successfully exited with a code of {1}" -f $FilePath, $LASTEXITCODE))
	Invoke-Expression "deactivate"
    exit $LASTEXITCODE
}
catch {
    consoleLog("Error in attempting to run script")
	Invoke-Expression "deactivate"
	throw
}
