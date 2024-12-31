export $(grep -v '^#' .env.production | xargs)


Get-Content .env.production | Where-Object { $_ -notmatch '^\s*#' } | ForEach-Object {
    $key, $value = $_ -split '=', 2
    [System.Environment]::SetEnvironmentVariable($key.Trim(), $value.Trim(), [System.EnvironmentVariableTarget]::Process)
}
