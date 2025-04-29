using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http.Json;
using System.Text;
using System.Threading.Tasks;
using UIMeetMind.Models;

namespace UIMeetMind.Services;

public class ApiService
{
    private readonly HttpClient _httpClient;
    private const string BaseUrl = "http://127.0.0.1:5000"; // adjust if needed

    public ApiService()
    {
        _httpClient = new HttpClient { BaseAddress = new Uri(BaseUrl) };
    }

    public async Task<List<MeetingModel>> GetMeetingsAsync()
    {
        return await _httpClient.GetFromJsonAsync<List<MeetingModel>>("/meetings");
    }

    public async Task<string> StartRecordingAsync()
    {
        var response = await _httpClient.PostAsJsonAsync("/start_record", new { });
        response.EnsureSuccessStatusCode();
        var result = await response.Content.ReadFromJsonAsync<Dictionary<string, string>>();
        return result["meetingId"];
    }

    public async Task StopRecordingAsync(string meetingId)
    {
        var response = await _httpClient.PostAsJsonAsync("/stop_record", new { meetingId = meetingId });
        response.EnsureSuccessStatusCode();
    }

    public async Task TranscribeMeetingAsync(string meetingId)
    {
        var response = await _httpClient.PostAsJsonAsync("/transcribe", new { meetingId = meetingId });
        response.EnsureSuccessStatusCode();
    }

    public async Task SummarizeMeetingAsync(string meetingId)
    {
        var response = await _httpClient.PostAsJsonAsync("/summarize", new { meetingId = meetingId });
        response.EnsureSuccessStatusCode();
    }

    public async Task<string> GetMeetingResultsAsync(string meetingId)
    {
        var response = await _httpClient.GetAsync($"/meetings/{meetingId}");
        response.EnsureSuccessStatusCode();
        var data = await response.Content.ReadFromJsonAsync<Dictionary<string, object>>();
        return $"Status: {data["status"]}\nTranscript: {data["transcriptPath"]}\nSummary: {data["summaryPath"]}";
    }

    public async Task<List<MeetingFile>> ListAllFilesAsync()
    {
        var response = await _httpClient.GetFromJsonAsync<List<MeetingFile>>("/files");
        return response ?? new List<MeetingFile>();
    }

    public async Task DownloadFileAsync(string filePath)
    {
        var response = await _httpClient.GetAsync($"/files/download?path={Uri.EscapeDataString(filePath)}");
        response.EnsureSuccessStatusCode();

        var bytes = await response.Content.ReadAsByteArrayAsync();
        var fileName = Path.GetFileName(filePath);
        var localPath = Path.Combine(FileSystem.AppDataDirectory, fileName);
        await File.WriteAllBytesAsync(localPath, bytes);

        await Launcher.OpenAsync(new OpenFileRequest { File = new ReadOnlyFile(localPath) });
    }

    public async Task DeleteFileAsync(string filePath)
    {
        var response = await _httpClient.DeleteAsync($"/files/delete?path={Uri.EscapeDataString(filePath)}");
        response.EnsureSuccessStatusCode();
    }
}