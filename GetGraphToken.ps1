Connect-MgGraph -NoWelcome

$Parameters = @{
  Method = "GET"
  URI = "/v1.0/me"
  OutputType = "HttpResponseMessage"
}
$Response = Invoke-GraphRequest @Parameters
$Headers = $Response.RequestMessage.Headers
$Token = $Headers.Authorization.Parameter
Write-Host $Token