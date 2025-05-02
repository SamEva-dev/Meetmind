using System.Net.Http.Json;

using UIMeetMind.Models;

namespace UIMeetMind.Services;

public class NotificationService : INotificationService
{
    private readonly HttpClient _httpClient;

    public NotificationService(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }

    public async Task<List<NotificationModel>> GetNotificationsAsync()
    {
        return await _httpClient.GetFromJsonAsync<List<NotificationModel>>(
                "/notifications",
                new System.Text.Json.JsonSerializerOptions { PropertyNameCaseInsensitive = true }
            ) ?? new();
    }

    public async Task ClearNotificationsAsync()
    {
        await _httpClient.DeleteAsync("/notifications");
    }
}