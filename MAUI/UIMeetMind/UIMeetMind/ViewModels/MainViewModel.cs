using System.Collections.ObjectModel;
using CommunityToolkit.Maui.Alerts;
using CommunityToolkit.Maui.Core;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using UIMeetMind.Models;
using UIMeetMind.Services;
using UIMeetMind.Utils;

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
    private MeetingFile _selectedFile;

    [ObservableProperty]
    private bool _hasRecordingInProgress;


    public MainViewModel(ApiService apiService)
    {
        _apiService = apiService;

        LoadMeetingsAsync();
        //RefreshMeetingsCommand = new AsyncRelayCommand(LoadMeetingsAsync);
        //StartRecordingCommand = new AsyncRelayCommand(StartRecordingAsync);
        //StopRecordingCommand = new AsyncRelayCommand(StopRecordingAsync);
    }

    [RelayCommand]
    private async Task LoadMeetingsAsync()
    {
        try
        {
            if (IsBusy) return;
            IsBusy = true;
            var list = await _apiService.GetMeetingsAsync();
            Meetings.Clear();
            foreach (var m in list)
            {
                Meetings.Add(m);
            }
            HasRecordingInProgress = Meetings.Any(m => m.Status == "In Progress");
            IsBusy = false;
        } catch (Exception ex) {
                LoggerConfig.Logger.Error(ex, "Erreur lors du chargement des réunions");
                await ShowToastAsync("Erreur lors du chargement des réunions", true);
        } finally 
        {
          IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task StartRecordingAsync()
    {
        try
        {
            //if (IsBusy) return;
            //IsBusy = true;
            var id = await _apiService.StartRecordingAsync();
            await LoadMeetingsAsync();
            // IsBusy = false;
        }
        catch (Exception ex)
        {
            LoggerConfig.Logger.Error(ex, "Erreur lors du démarrage de l'enregistrement");
            await ShowToastAsync("Échec du démarrage", true);
        }
        finally
        {
            IsBusy = false;
        }

    }

    [RelayCommand]
    private async Task StopRecordingAsync()
    {
        try
        {
            //if (IsBusy) return;
            //IsBusy = true;
            // Assuming the last started meeting is in progress
            var toStop = Meetings.FirstOrDefault(m => m.Status == "In Progress")?.MeetingId;
            if (!string.IsNullOrEmpty(toStop))
            {
                await _apiService.StopRecordingAsync(toStop);
                await LoadMeetingsAsync();
            }
            //IsBusy = false;
        }
        catch (Exception ex)
        {
            LoggerConfig.Logger.Error(ex, "Erreur lors de l'arrêt de l'enregistrement");
            await ShowToastAsync("Erreur lors de l'arrêt", true);
        }
        finally
        {
            IsBusy = false;
        }

    }

    [RelayCommand]
    private async Task TranscribeAsync()
    {
        try
        {
            if (SelectedFile == null) return;
            IsBusy = true;
            var id = ExtractMeetingId(SelectedFile.FileName);
            await _apiService.TranscribeMeetingAsync(id);
            await LoadMeetingsAsync();
            await ShowToastAsync("Transcription lancée !");
            IsBusy = false;
        }
        catch (Exception ex)
        {
            LoggerConfig.Logger.Error(ex, "Erreur lors de la transcription");
            await ShowToastAsync("Échec de la transcription", true);
        }
        finally
        {
            IsBusy = false;
        }

    }

    [RelayCommand]
    private async Task SummarizeAsync()
    {
        try
        {
            if (SelectedFile == null) return;
            IsBusy = true;
            var id = ExtractMeetingId(SelectedFile.FileName);
            await _apiService.SummarizeMeetingAsync(id);
            await LoadMeetingsAsync();
            IsBusy = false;
        }
        catch (Exception ex)
        {
            LoggerConfig.Logger.Error(ex, "Erreur lors du résumé");
            await ShowToastAsync("Erreur de résumé", true);
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task ShowResultsAsync()
    {
        try
        {
            if (SelectedFile == null) return;
            var id = ExtractMeetingId(SelectedFile.FileName);
            var result = await _apiService.GetMeetingResultsAsync(id);
            await Application.Current.MainPage.DisplayAlert("Résultat", result, "OK");
        }
        catch (Exception ex)
        {
            LoggerConfig.Logger.Error(ex, "Erreur lors de l'affichage des résultats");
            await ShowToastAsync("Impossible d'afficher les résultats", true);
        }
    }

    [RelayCommand]
    private async Task DownloadFileAsync(MeetingFile file)
    {
        try
        {
            if (file == null) return;
            await _apiService.DownloadFileAsync(file.FilePath);
            await ShowToastAsync("Fichier téléchargé");
        }
        catch (Exception ex)
        {
            LoggerConfig.Logger.Error(ex, "Erreur téléchargement fichier");
            await ShowToastAsync("Échec du téléchargement", true);
        }
    }

    [RelayCommand]
    private async Task DeleteFileAsync(MeetingFile file)
    {
        try
        {
            if (file == null) return;
            await _apiService.DeleteFileAsync(file.FilePath);
            await LoadAllFilesAsync();
            await ShowToastAsync("Fichier supprimé !");
        }
        catch (Exception ex)
        {
            LoggerConfig.Logger.Error(ex, "Erreur suppression fichier");
            await ShowToastAsync("Échec suppression fichier", true);
        }

    }

    [RelayCommand]
    private void SelectFile(MeetingFile file)
    {
        SelectedFile = file;
    }

    public async Task LoadAllFilesAsync()
    {
        try
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
        catch (Exception ex)
        {
            LoggerConfig.Logger.Error(ex, "Erreur lors du chargement des fichiers");
            await ShowToastAsync("Erreur chargement fichiers", true);
        }
    }

    private string ExtractMeetingId(string fileName)
    {
        return fileName.Split("_")[0].Replace(".txt", "").Replace(".wav", "");
    }

    private async Task ShowToastAsync(string message, bool isError = false)
    {
        var snackbar = Snackbar.Make(message,
            visualOptions: new SnackbarOptions
            {
                BackgroundColor = isError ? Colors.DarkRed : Colors.Black,
                TextColor = Colors.White,
                CornerRadius = 6,
                Font = Microsoft.Maui.Font.Default // Fix: Changed from Microsoft.Maui.Graphics.Font.Default to Microsoft.Maui.Font.Default
            },
            duration: TimeSpan.FromSeconds(3));
        await snackbar.Show();
    }


}
