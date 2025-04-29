using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using UIMeetMind.Models;
using UIMeetMind.Services;

namespace UIMeetMind.ViewModels;

public partial class MainViewModel : ObservableObject
{
    private readonly ApiService _apiService;

    public ObservableCollection<MeetingModel> Meetings { get; } = new();
    public ObservableCollection<MeetingFile> AudioFiles { get; } = new();
    public ObservableCollection<MeetingFile> TranscriptFiles { get; } = new();
    public ObservableCollection<MeetingFile> SummaryFiles { get; } = new();

    [ObservableProperty]
    private bool _isBusy;

    [ObservableProperty]
    private MeetingFile selectedFile;

    public MainViewModel(ApiService apiService)
    {
        _apiService = apiService;
        //RefreshMeetingsCommand = new AsyncRelayCommand(LoadMeetingsAsync);
        //StartRecordingCommand = new AsyncRelayCommand(StartRecordingAsync);
        //StopRecordingCommand = new AsyncRelayCommand(StopRecordingAsync);
    }

    [RelayCommand]
    private async Task LoadMeetingsAsync()
    {
        if (IsBusy) return;
        IsBusy = true;
        var list = await _apiService.GetMeetingsAsync();
        Meetings.Clear();
        foreach (var m in list)
        {
            Meetings.Add(m);
        }
        IsBusy = false;
    }

    [RelayCommand]
    private async Task StartRecordingAsync()
    {
        if (IsBusy) return;
        IsBusy = true;
        var id = await _apiService.StartRecordingAsync();
        await LoadMeetingsAsync();
        IsBusy = false;
    }

    [RelayCommand]
    private async Task StopRecordingAsync()
    {
        if (IsBusy) return;
        IsBusy = true;
        // Assuming the last started meeting is in progress
        var toStop = Meetings.FirstOrDefault(m => m.Status == "In Progress")?.MeetingId;
        if (!string.IsNullOrEmpty(toStop))
        {
            await _apiService.StopRecordingAsync(toStop);
            await LoadMeetingsAsync();
        }
        IsBusy = false;
    }

    [RelayCommand]
    private async Task TranscribeAsync()
    {
        if (SelectedFile == null) return;
        IsBusy = true;
        var id = ExtractMeetingId(SelectedFile.FileName);
        await _apiService.TranscribeMeetingAsync(id);
        await LoadMeetingsAsync();
        IsBusy = false;
    }

    [RelayCommand]
    private async Task SummarizeAsync()
    {
        if (SelectedFile == null) return;
        IsBusy = true;
        var id = ExtractMeetingId(SelectedFile.FileName);
        await _apiService.SummarizeMeetingAsync(id);
        await LoadMeetingsAsync();
        IsBusy = false;
    }

    [RelayCommand]
    private async Task ShowResultsAsync()
    {
        if (SelectedFile == null) return;
        var id = ExtractMeetingId(SelectedFile.FileName);
        var result = await _apiService.GetMeetingResultsAsync(id);
        await Application.Current.MainPage.DisplayAlert("Résultat", result, "OK");
    }

    [RelayCommand]
    private async Task DownloadFileAsync(MeetingFile file)
    {
        if (file == null) return;
        await _apiService.DownloadFileAsync(file.FilePath);
    }

    [RelayCommand]
    private async Task DeleteFileAsync(MeetingFile file)
    {
        if (file == null) return;
        await _apiService.DeleteFileAsync(file.FilePath);
        await LoadAllFilesAsync();
    }

    [RelayCommand]
    private void SelectFile(MeetingFile file)
    {
        SelectedFile = file;
    }

    public async Task LoadAllFilesAsync()
    {
        var files = await _apiService.ListAllFilesAsync();
        AudioFiles.Clear();
        TranscriptFiles.Clear();
        SummaryFiles.Clear();
        foreach (var f in files)
        {
            switch (f.Type)
            {
                case "audio": AudioFiles.Add(f); break;
                case "transcript": TranscriptFiles.Add(f); break;
                case "summary": SummaryFiles.Add(f); break;
            }
        }
    }

    private string ExtractMeetingId(string fileName)
    {
        return fileName.Split("_")[0].Replace(".txt", "").Replace(".wav", "");
    }

}
