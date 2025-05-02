using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http.Json;
using System.Text;
using System.Threading.Tasks;
using UIMeetMind.Models;

namespace UIMeetMind.Services;

public class SettingsService : ISettingsService
{
    private readonly HttpClient _httpClient;

    public SettingsService(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }

    public async Task<SettingsModel> GetSettingsAsync()
    {
        var response = await _httpClient.GetAsync("settings");
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<SettingsModel>();
    }

    public async Task SaveSettingsAsync(SettingsModel settings)
    {
        var response = await _httpClient.PutAsJsonAsync("settings", settings);
        response.EnsureSuccessStatusCode();
    }
}