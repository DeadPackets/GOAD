################################
### Script to execute F-Secure/Chainsaw - Identify Malicious activity recorded in WinEvtLogs using Sigma Rules
################################

##########
# Chainsaw will be run against all event logs found in the default location
# Output converted to JSON and appended to active-responses.log
##########

##########
# Chainsaw Version: v2.0-alpha
##########

$ErrorActionPreference = "SilentlyContinue"

# State file to track processed events
$state_file = "C:\Program Files\socfortress\chainsaw\processed_events.txt"
If(!(test-path $state_file)) {
    New-Item -ItemType File -Force -Path $state_file | Out-Null
}

# Load previously processed event hashes
$processed_events = @{}
if (Test-Path $state_file) {
    Get-Content $state_file -ErrorAction SilentlyContinue | ForEach-Object {
        $parts = $_ -split '\|', 2
        if ($parts.Length -eq 2) {
            $processed_events[$parts[0]] = $parts[1]
        }
    }
}

# Clean up old entries (keep only last 2 minutes to prevent memory issues)
$cutoff_time = (Get-Date).AddMinutes(-2)
$processed_events = $processed_events.GetEnumerator() | Where-Object {
    [DateTime]::ParseExact($_.Value, 'yyyy-MM-dd HH:mm:ss', $null) -gt $cutoff_time
} | ForEach-Object -Begin { $h = @{} } -Process { $h[$_.Key] = $_.Value } -End { $h }

# Analyse events recorded in last 1 minute with proper time boundaries
$repo_path = "C:\Program Files\socfortress\chainsaw\sigma"
$current_date = (Get-Date).toUniversalTime()
$end_date = $current_date
$start_date = (Get-Date -Date $current_date).AddMinutes(-1)
$from = Get-Date -Date $start_date -UFormat '+%Y-%m-%dT%H:%M:%S'
$to = Get-Date -Date $end_date -UFormat '+%Y-%m-%dT%H:%M:%S'


# Create Chainsaw Output Folder if it doesn't exist
$chainsaw_output = "$env:TMP\chainsaw_output"
If(!(test-path $chainsaw_output)) {
    New-Item -ItemType Directory -Force -Path $chainsaw_output
}

# Windows Sigma Path
# Removed -r 'C:\Program Files\socfortress\chainsaw\rules'
$windows_path = "C:\Program Files\socfortress\chainsaw\sigma\rules\windows"

# Run Chainsaw and store JSONs in TMP folder with both --from and --to parameters
echo "$from TO $to";
& 'C:\Program Files\socfortress\chainsaw\chainsaw_x86_64-pc-windows-msvc.exe' hunt C:\Windows\System32\winevt -s $windows_path --mapping 'C:\Program Files\socfortress\chainsaw\mappings\sigma-event-logs-all.yml' --from "$from" --to "$to" --output $env:TMP\chainsaw_output\results.json --level critical --level high --level medium --json --skip-errors

# Convert JSON to new line entry for every 'group'
function Convert-JsonToNewLine($json) {
    $new_events = @()
    foreach($document in $json) {
        $document.document | ConvertTo-Json -Compress -Depth 99 | foreach-object {
            # Create a unique hash for this event (using id, timestamp, and a portion of document)
            $event_key = "$($document.id)_$($document.timestamp)_$($_.GetHashCode())"

            # Only process if we haven't seen this event before
            if (-not $processed_events.ContainsKey($event_key)) {
                $output = [pscustomobject]@{
                    group = $document.group
                    kind = $document.kind
                    document = $_
                    name = $document.name
                    timestamp = $document.timestamp
                    authors = $document.authors
                    level = $document.level
                    source = $document.source
                    status = $document.status
                    falsepositives = $document.falsepositives
                    id = $document.id
                    logsource = $document.logsource
                    references = $document.references
                    tags = $document.tags
                } | ConvertTo-Json -Compress

                # Track this event
                $processed_events[$event_key] = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
                $new_events += "$event_key|$($processed_events[$event_key])"

                # Output the event
                $output
            }
        }
    }
    # Return new events to track
    return ,$new_events
}

# Convert JSONs to new line entry and append to active-responses.log
$all_new_events = @()
Get-ChildItem $env:TMP\chainsaw_output -Filter *.json | Foreach-Object {
    $Chainsaw_Array = Get-Content $_.FullName | ConvertFrom-Json
    $result = Convert-JsonToNewLine $Chainsaw_Array
    if ($result -and $result.Count -gt 0) {
        # Separate the new events tracking from the JSON output
        $json_output = $result | Where-Object { $_ -notmatch '^\S+\|\d{4}-\d{2}-\d{2}' }
        $tracking_entries = $result | Where-Object { $_ -match '^\S+\|\d{4}-\d{2}-\d{2}' }

        # Write JSON output to log
        if ($json_output) {
            $json_output | Out-File -Append -Encoding ascii 'C:\Program Files (x86)\ossec-agent\active-response\active-responses.log'
        }

        # Collect tracking entries
        $all_new_events += $tracking_entries
    }
}

# Save updated state file with new events
if ($all_new_events.Count -gt 0) {
    $all_new_events | Out-File -Append -Encoding ascii $state_file
}

# Remove TMP JSON Folder
rm -r $chainsaw_output

# Output status if Sigma rules were updated
if ($LASTEXITCODE -eq 0) {
    $status_payload = @{
        group = 'sigma'
        sigma_rules = 'updated'
    } | ConvertTo-Json
    Write-Output $status_payload
}