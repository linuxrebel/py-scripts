####### Functions ########
Function Get-PrimaryResolution{ Param ($monitorArray)
    foreach ($monitor in $monitorArray){
        if($monitor.Primary){       
            $primaryResolution = [System.Tuple]::Create($monitor.Bounds.Width, $monitor.Bounds.Height);
            return $primaryResolution;
        }
    }
}

####### Information Collection #########

## Resolution Information
#$PrimaryResolution = Get-PrimaryResolution([System.Windows.Forms.Screen]::AllScreens);
$PrimaryResolution = "1920 x 1080";
#$Horizontal = $PrimaryResolution.Item1;
$Horizontal = 1920;
#$Vertical = $PrimaryResolution.Item2;
$Vertical = 1080;
## Uptime Information
$uptime = PsInfo64.exe | grep.exe "Uptime" | gawk -F: '{ print $2 }' | sed -e 's/^[ \t]*//'

## Disk Information
# Available Space
$FreeDiskSize = (Get-WMIObject Win32_LogicalDisk).FreeSpace | select -f 1;
$FreeDiskSizeGB = $FreeDiskSize / 1073741824;
$FreeDiskSizeGB = "{0:N0}" -f $FreeDiskSizeGB;
# Total Space
$DiskSize = (Get-WMIObject Win32_LogicalDisk).size | select -f 1;
$DiskSizeGB = $DiskSize / 1073741824;
$DiskSizeGB = "{0:N0}" -f $DiskSizeGB;
$FreeDiskPercent = ($FreeDiskSizeGB / $DiskSizeGB) * 100;
$FreeDiskPercent = "{0:N0}" -f $FreeDiskPercent;
# Used Space
$UsedDiskSizeGB = $DiskSizeGB - $FreeDiskSizeGB;
$UsedDiskPercent = ($UsedDiskSizeGB / $DiskSizeGB) * 100;
$UsedDiskPercent = "{0:N0}" -f $UsedDiskPercent;

## Environment Information
$Username = $env:username;
$Machine = (Get-WMIObject Win32_OperatingSystem).CSName;
$OS = (Get-WMIObject Win32_OperatingSystem).Caption;
$BitVer = (Get-WMIObject Win32_OperatingSystem).OSArchitecture;
$Kernel = (Get-WMIObject Win32_OperatingSystem).Version;

## Hardware Information
$Motherboard = Get-CimInstance Win32_BaseBoard | Select-Object Manufacturer, Product;
$CPU = (((Get-WMIObject Win32_Processor).Name) -replace '\s+', ' ');
$GPU = (Get-WMIObject Win32_DisplayConfiguration).DeviceName;
$FreeRam = ([math]::Truncate((Get-WMIObject Win32_OperatingSystem).FreePhysicalMemory / 1KB)); 
$TotalRam = ([math]::Truncate((Get-WMIObject Win32_ComputerSystem).TotalPhysicalMemory / 1MB));
$UsedRam = $TotalRam - $FreeRam;
$FreeRamPercent = ($FreeRam / $TotalRam) * 100;
$FreeRamPercent = "{0:N0}" -f $FreeRamPercent;
$UsedRamPercent = ($UsedRam / $TotalRam) * 100;
$UsedRamPercent = "{0:N0}" -f $UsedRamPercent;

####### Printing Output #########

# Line 1 - HostName
#Write-Host "                         ....::::       " -f Cyan -NoNewline;
Write-Host "                         ....::::       " -f Green -NoNewline;
Write-Host $Username -f red -nonewline; 
Write-Host "@" -f gray -nonewline; 
Write-Host $Machine -f red;

# Line 2 - OS
Write-Host "                 ....::::::::::::       " -f Green -NoNewline;
Write-Host "OS: " -f Red -NoNewline;
Write-Host $OS $BitVer;

# Line 3 - Kernel
Write-Host "        ....::::" -f Red -NoNewline;
Write-Host " ::::::::::::::::       " -f Green -NoNewline;
Write-Host "Kernel: " -f Red -nonewline;
Write-Host $Kernel;

# Line 4 - Uptime
Write-Host "....::::::::::::" -f Red -NoNewline;
Write-Host " ::::::::::::::::       " -f Green -NoNewline;
Write-Host "Uptime: " -f Red  -nonewline;
#Write-Host $uptime.Days"d " $uptime.Hours"h " $uptime.Minutes"m " $uptime.Seconds"s " -separator "";
Write-Host $uptime

# Line 5 - Motherboard
Write-Host "::::::::::::::::" -f Red -NoNewline;
Write-Host " ::::::::::::::::       " -f Green -NoNewline;
Write-Host "Motherboard: " -f Red -nonewline; 
Write-Host $Motherboard.Manufacturer $Motherboard.Product;

# Line 6 - Shell (Hardcoded since it is unlikely anybody can run this without powershell)
Write-Host "::::::::::::::::" -f Red -NoNewline;
Write-Host " ::::::::::::::::       " -f Green -NoNewline;
Write-Host "Shell: " -f Red -nonewline; 
Write-Host "PowerShell $($PSVersionTable.PSVersion.ToString())"

# Line 7 - Resolution (for primary monitor only)
Write-Host "::::::::::::::::" -f Red -NoNewline;
Write-Host " ::::::::::::::::       " -f Green -NoNewline;
Write-Host "Resolution: " -f Red -NoNewline; 
Write-Host $Horizontal "x" $Vertical;

# Line 8 - Windows Manager (HARDCODED, sorry bbzero users)
Write-Host "::::::::::::::::" -f Red -NoNewline;
Write-Host " ::::::::::::::::       " -f Green -NoNewline;
Write-Host "Window Manager: " -f Red -nonewline; 
Write-Host "DWM";

# Line 10 - Font (HARDCODED)
Write-Host "................" -f Cyan -NoNewline;
Write-Host " ................       " -f Yellow -NoNewline;
Write-Host "Font: " -f Red -nonewline; 
Write-Host "Segoe UI";

# Line 11 - CPU
Write-Host "::::::::::::::::" -f Cyan -NoNewline;
Write-Host " ::::::::::::::::       " -f Yellow -NoNewline;
Write-Host "CPU: " -f Red -nonewline; 
Write-Host $CPU;

# Line 12 - GPU
Write-Host "::::::::::::::::" -f Cyan -NoNewline;
Write-Host " ::::::::::::::::       " -f Yellow -NoNewline;
Write-Host "GPU: " -f Red -nonewline; 
Write-Host $GPU;

# Line 13 - Ram
Write-Host "::::::::::::::::" -f Cyan -NoNewline;
Write-Host " ::::::::::::::::       " -f Yellow -NoNewline;
Write-Host "RAM: " -f Red -nonewline;
Write-Host $UsedRam "MB / $TotalRam MB" -NoNewline;
Write-Host " (" -NoNewline
Write-Host $UsedRamPercent"%" -f Green -NoNewline;
Write-Host ")";

# Line 13 - Disk Usage
Write-Host "''''::::::::::::" -f Cyan -NoNewline;
Write-Host " ::::::::::::::::       " -f Yellow -NoNewline;
Write-Host "Disk: " -f Red -NoNewline;
Write-Host $UsedDiskSizeGB"GB" " / " $DiskSizeGB"GB" -NoNewline;
Write-Host " (" -NoNewline; 
Write-Host $UsedDiskPercent"%" -f Green -NoNewline;
Write-Host ")"; 

# Empty Lines
Write-Host "        ''''::::" -f Cyan -NoNewline;
Write-Host " ::::::::::::::::       " -f Yellow;
Write-Host "                 ''''::::::::::::       " -f Yellow;
Write-Host "                         ''''::::       " -f Yellow;

