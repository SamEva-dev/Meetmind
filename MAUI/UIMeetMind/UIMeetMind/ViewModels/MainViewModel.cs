using System.Collections.ObjectModel;
using CommunityToolkit.Maui.Alerts;
using CommunityToolkit.Maui.Core;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using UIMeetMind.Models;
using UIMeetMind.Services;
using UIMeetMind.Utils;
using Microsoft.Maui.Media;
using Plugin.Maui.Audio;
using static System.Runtime.InteropServices.JavaScript.JSType;
using Microsoft.Maui.Storage;

namespace UIMeetMind.ViewModels;

public partial class MainViewModel : ObservableObject
{
    private readonly ApiService _apiService;
    private readonly IAudioManager _audioManager;

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

    [ObservableProperty]
    private string _meetingId;

    [ObservableProperty]
    private string _status;

    [ObservableProperty]

    private string _startTimestamp;

    [ObservableProperty]
    private string _endTimestamp;


    public MainViewModel(ApiService apiService, IAudioManager audioManager)
    {
        _apiService = apiService;
        _audioManager = audioManager;
        LoadMeetingsAsync();

        AudioFiles = new ObservableCollection<MeetingFile>
        {
            new MeetingFile(){FileName="Meeting-001.wav", Date=new DateTime(2025,4,28)},
            new MeetingFile(){FileName="Meeting-002.wav", Date=new DateTime(2025,4,28)},
            new MeetingFile(){FileName="Meeting-003.wav", Date=new DateTime(2025,4,28)},
        };

        TranscriptFiles = new ObservableCollection<MeetingFile>
        {
            new MeetingFile(){FileName="Meeting-001_transcript.txt", Date=new DateTime(2025,4,27) },

            new MeetingFile() { FileName = "Meeting-002_transcript.txt", Date = new DateTime(2025, 4, 28) },
        };

        SummaryFiles = new ObservableCollection<MeetingFile>
        {
            new MeetingFile() { FileName =  "Meeting-001_summary.txt", Date = new DateTime(2025, 4, 27) },
        };
    }

    [RelayCommand]
    private async Task LoadMeetingsAsync()
    {
        try
        {
            //if (IsBusy) return;
           
            IsBusy = true;
            var list = await _apiService.GetMeetingsAsync();
            Meetings.Clear();
            foreach (var m in list)
            {
                Meetings.Add(m);
            }
            HasRecordingInProgress = Meetings.Any(m => m.Status == "In Progress");
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
            //HasRecordingInProgress = true;
            if (IsBusy) return;
            IsBusy = true;
            await _apiService.StartRecordingAsync();
            await LoadMeetingsAsync();
            await PlaySoundAsync("start_recording.wav");
            await ShowToastAsync("Enregistrement démarré");
            LoggerConfig.Logger.Information("Enregistrement démarré");
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
            if (IsBusy) return;
            IsBusy = true;
            var toStop = Meetings.FirstOrDefault(m => m.Status == "In Progress")?.MeetingId;
            if (!string.IsNullOrEmpty(toStop))
            {
                await _apiService.StopRecordingAsync(toStop);
                await LoadMeetingsAsync();
                HasRecordingInProgress = false;
                await PlaySoundAsync("stop_recording.wav");
                await ShowToastAsync("Enregistrement arrêté");
                LoggerConfig.Logger.Information("Enregistrement arrêté");
            }
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
            LoggerConfig.Logger.Information("Transcription lancée pour {Id}", id);
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
            LoggerConfig.Logger.Information("Résumé généré pour {Id}", id);
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
            LoggerConfig.Logger.Information("Affichage des résultats pour {Id}", id);
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
            LoggerConfig.Logger.Information("Fichier téléchargé: {Path}", file.FilePath);
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
            LoggerConfig.Logger.Information("Fichier supprimé: {Path}", file.FilePath);
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

    [RelayCommand]
    private async Task TranscribeFileAsync(MeetingFile file)
    {
        if (file == null) return;
        IsBusy = true;
        try
        {
            var id = ExtractMeetingId(file.FileName);
            await _apiService.TranscribeMeetingAsync(id);
            await LoadMeetingsAsync();
            await ShowToastAsync("Transcription lancée pour " + id);
            LoggerConfig.Logger.Information("Transcription lancée pour {Id}", id);
        }
        catch (Exception ex)
        {
            LoggerConfig.Logger.Error(ex, "Erreur lors de la transcription de {Path}", file.FilePath);
            await ShowToastAsync("Échec de la transcription", true);
        }
        finally { IsBusy = false; }
    }

    [RelayCommand]
    private async Task SummarizeFileAsync(MeetingFile file)
    {
        if (file == null) return;
        IsBusy = true;
        try
        {
            var id = ExtractMeetingId(file.FileName);
            await _apiService.SummarizeMeetingAsync(id);
            await LoadMeetingsAsync();
            await ShowToastAsync("Résumé généré pour " + id);
            LoggerConfig.Logger.Information("Résumé généré pour {Id}", id);
        }
        catch (Exception ex)
        {
            LoggerConfig.Logger.Error(ex, "Erreur lors du résumé de {Path}", file.FilePath);
            await ShowToastAsync("Échec du résumé", true);
        }
        finally { IsBusy = false; }
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

    private async Task PlaySoundAsync(string fileName)
    {
        try
        {
            var stream = await FileSystem.OpenAppPackageFileAsync(fileName);
            var player = _audioManager.CreatePlayer(stream);
            player.Play();
        }
        catch (Exception ex)
        {
            LoggerConfig.Logger.Warning(ex, "Impossible de jouer le son {file}", fileName);
        }
    }
}
