<#
Aaron Genovia 2020-07-13

Operations Toolkit (OTK) 

Contains:
1. [Class] Logger 
    - [Function] consoleLog = outputs a $Message  with the timestamp appended to the console 
        using Write-Host
2. [Class] CheckFileLock 
    - [Function] isUnlocked = polls a file path every $PollRate seconds until it is unlocked
        or $Timeout is reached
#>


class Logger {
    <#
    The logger class takes a $Message, formats it and returns a string
    Can be extended by using functions to output to wherever you need it
    #>

    [string]$Message

    [string]timestamp() {
        return "[{0:yyyy-MM-dd} {0:HH:mm:ss}]" -f (Get-Date)
    }

	[string]buildMessage() {
		$msg = $this.Message
        $timestamp = $this.timestamp()
		return "$timestamp $msg"
	}

    [void]logToConsole() {
        Write-Host $this.buildMessage()
    }
}


class CheckFileLock {
    <#
    Contains methods to check whether a file is locked and poll until it is unlocked
    #>

    [string]$FilePath
    [uint64]$Timeout
    [uint64]$PollRate

    [bool]isLocked() {
        # verify that the provided path is a file and not a directory
        If ([System.IO.File]::Exists($this.FilePath)) {
            Try {
                $fileAccess = [System.IO.File]::Open($this.FilePath, 'Open', 'Write')
                $fileAccess.Close()
                $fileAccess.Dispose()
                $isLocked = $False
            }
            Catch [System.UnauthorizedAccessException] {
                # file is inaccessible by the user
                throw
            }
            Catch {
                # any other thrown exception indicates that it's locked
                $isLocked = $True
            }
            return $isLocked
        }
        Else {
            # it is not a valid file path
            $fp = $this.FilePath
            consoleLog("`"$fp`" is not a valid file path. Please double check parameters and try again.")
            throw "FileNotFound"
        }
    }

    [bool]poll() {
        # returns True if the file is accessible after polling for a maximum of $Timeout seconds
        # returns False if the file is inaccessible even after $Timeout seconds

        $start = [int][double]::Parse((Get-Date -UFormat %s))  # get unix timestamp with ms accuracy
        $end = $start + $this.Timeout  # add whatever timeout, this is our upper limit
        $now = $start
        $fp = $this.FilePath
        $to = $this.Timeout
        $pr = $this.PollRate

        while ($now -lt $end) {
            try {
				# check if the file is locked
                If ($this.isLocked() -eq $True) {

                    If ($pr -eq 1) {
                        $s = "second"
                    }
                    Else {
                        $s = "seconds"
                    }

                    consoleLog("The file `"$fp`" is locked. Trying again in $pr $s.")
                    Start-Sleep $pr
                    $now = [int][double]::Parse((Get-Date -UFormat %s))  # update timestamp
                }
                Else {
                    # if the file is accessible within the alloted $Timeout window, return $True
                    return $True
                }
            }
            catch {
                throw
            }
   
        }
        # if the $Timeout is exceeded and the file is still locked, log and return $False
        consoleLog("The timeout of $to seconds has been reached while waiting for `"$fp`" to become unlocked.")
        return $False
    }
}
    

Function consoleLog {
    # Use the Logger class to format a message and output it to the console

    Param(
        [parameter(mandatory=$True)]
		[AllowEmptyString()]
        [string]$Message
    )

    $logger = [Logger]::new()
    $logger.Message = $message
    $logger.logToConsole()
}


Function isUnlocked {
    # Use the CheckFileLock class to poll a $FilePath every $PollRate seconds
    # for a maximum of $Timeout seconds to check if it is accessible, return $True
    # if it is accessible and $False if it is not

    Param(
        [parameter(mandatory=$True, position=0)]
        [string]$FilePath,

        [parameter(mandatory=$False, position=1)]
        [uint64]$Timeout = 300,  # timeout in seconds

        [parameter(mandatory=$False, position=2)]
        [uint64]$PollRate = 5  # interval for polling in seconds
    )

    $checkfile = [CheckFileLock]::new()
    $checkfile.FilePath = $FilePath
    $checkfile.Timeout = $Timeout
    $checkfile.PollRate = $PollRate

    try {
        $isUnlocked = $checkfile.poll()
        return $isUnlocked
    }
    catch {
        throw
    }
}


Function moveFile {
    # This is a wrapper over Move-Item to always perform a CheckFileLock
    # before proceeding with moving an item
    # For a comprehensive explanation of how Powershell handles wrappers
    # look for the topic "Splatting" and $PSBoundParameters


    Param(
        [parameter(mandatory=$True, position=0)]
        [string]$Path,
        [parameter(mandatory=$True, position=1)]
        [string]$Destination,
        [parameter(mandatory=$False, position=2)]
        [switch]$Force,
        [parameter(mandatory=$False, position=3)]
        [string]$Filter,
        [parameter(mandatory=$False, position=4)]
        [string]$Include,
        [parameter(mandatory=$False, position=5)]
        [string]$Exclude
    )

    # only poll for 10 seconds so it doesn't hold up too long
    # if a longer $Timeout is needed, make an explicit call to 
    # isUnlocked() in your code, this is only for convenience to
    # cover most use cases

    # FOREWARNING: if foregoing the usage of this convenience script, be
    # aware that Move-Item does not throw a terminating 
    # exception when encountering a locked file and your code
    # could continue on as if it was a successful call when
    # that is not what you intended 

    # I have encountered this when attempting to Move-Item an incomplete 
    # file (still being written by a process) and it threw an error and
    # was unable to actually move the file BUT it still continued on with
    # the code as if it was a successful operation--this is highly 
    # undesirable
    $isUnlocked = (isUnlocked -FilePath $Path -Timeout 10 -PollRate 1)
    If ($isUnlocked) {
        Move-Item @PSBoundParameters
    }
    Else {
        consoleLog("Cannot move the file `"$Path`" since it is locked. Please try again.")
        throw "FileLocked"
    }
}

Function copyFile {
    # This is a wrapper over Copy-Item to always perform a CheckFileLock
    # before proceeding with moving an item
    # For a comprehensive explanation of how Powershell handles wrappers
    # look for the topic "Splatting" and $PSBoundParameters


    Param(
        [parameter(mandatory=$True, position=0)]
        [string]$Path,
        [parameter(mandatory=$True, position=1)]
        [string]$Destination,
        [parameter(mandatory=$True, position=2)]
        [switch]$Container,
        [parameter(mandatory=$False, position=3)]
        [switch]$Force,
        [parameter(mandatory=$False, position=4)]
        [switch]$Filter,
        [parameter(mandatory=$False, position=5)]
        [string]$Include,
        [parameter(mandatory=$False, position=6)]
        [string]$Exclude,
        [parameter(mandatory=$False, position=7)]
        [switch]$Recurse
    )

    # only poll for 10 seconds so it doesn't hold up too long
    # if a longer $Timeout is needed, make an explicit call to 
    # isUnlocked() in your code, this is only for convenience to
    # cover most use cases

    # FOREWARNING: if foregoing the usage of this convenience script, be
    # aware that Copy-Item does not throw a terminating 
    # exception when encountering a locked file and your code
    # could continue on as if it was a successful call when
    # that is not what you intended 

    # I have encountered this when attempting to Copy-Item an incomplete 
    # file (still being written by a process) and it continued on as if
    # it was a valid operation and copied the incomplete file--this is
    # highly undesirable
    $isUnlocked = (isUnlocked -FilePath $Path -Timeout 10 -PollRate 1)
    If ($isUnlocked) {
        Copy-Item @PSBoundParameters
    }
    Else {
        consoleLog("Cannot copy the file `"$Path`" since it is locked. Please try again.")
        throw "FileLocked"
    }
}

Function isEmpty {
	# Check if a file is empty "0kb"
    Param (
	[parameter(mandatory=$True, position=0)]
	[string]$Path
    )

	$is_empty = ((Get-Item $Path).length -eq 0kb)
	return $is_empty
}


# export only the functions that we need
Export-ModuleMember -Function consoleLog
Export-ModuleMember -Function isUnlocked
Export-ModuleMember -Function moveFile
Export-ModuleMember -Function copyFile
Export-ModuleMember -Function isEmpty