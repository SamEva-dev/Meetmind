
namespace UIMeetMind.Services;

public class HealthService : IHealthService
{
    private readonly HttpClient _httpClient;

    public HealthService(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }

    public async Task<bool> CheckHealthAsync()
    {
        try
        {
            var response = await _httpClient.GetAsync("/health");
            response.EnsureSuccessStatusCode();
            var json = await response.Content.ReadAsStringAsync();
            return json.Contains("ok");
        }
        catch
        {
            return false;
        }
    }
}