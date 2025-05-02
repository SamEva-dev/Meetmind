
using System.Net.Http.Json;
using UIMeetMind.Models;

namespace UIMeetMind.Services;

public class FileService : IFileService
{
    private readonly HttpClient _httpClient;

    public FileService(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }

    public async Task<List<MeetingFile>> GetAudioFilesAsync()
    {
        var result = await _httpClient.GetFromJsonAsync<List<MeetingFile>>("files/audio");
        return result ?? new List<MeetingFile>();
    }

    public async Task<List<MeetingFile>> GetTranscriptFilesAsync()
    {
        var result = await _httpClient.GetFromJsonAsync<List<MeetingFile>>("files/transcript");
        return result ?? new List<MeetingFile>();
    }

    public async Task<List<MeetingFile>> GetSummaryFilesAsync()
    {
        var result = await _httpClient.GetFromJsonAsync<List<MeetingFile>>("files/summary");
        return result ?? new List<MeetingFile>();
    }
}