
using System.Net.Http.Json;
using UIMeetMind.Models;

namespace UIMeetMind.Services;

public class MeetingService : IMeetingService
{
    private readonly HttpClient _httpClient;

    public MeetingService(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }

    public async Task<List<MeetingModel>> GetTodayMeetingsAsync()
    {
        var response = await _httpClient.GetFromJsonAsync<List<MeetingModel>>("meeting/today");
        return response ?? new List<MeetingModel>();
    }
}