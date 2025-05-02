
using CommunityToolkit.Maui.Alerts;
using CommunityToolkit.Maui.Core;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using UIMeetMind.Services;

namespace UIMeetMind.ViewModels;

public partial class SettingsViewModel : ObservableObject
{
    private readonly ISettingsService _settingsService;

    [ObservableProperty] private bool _autoTranscribe;
    [ObservableProperty] private bool _autoSummarize;
    [ObservableProperty] private bool _autoStartEnabled;
    [ObservableProperty] private bool _autoStopEnabled;
    [ObservableProperty] private int _preNotifyDelay;
    [ObservableProperty] private int _repeatNotifyDelay;
    [ObservableProperty] private bool _isBusy;

    public SettingsViewModel(ISettingsService settingsService)
    {
        _settingsService = settingsService;
        _ = LoadSettingsAsync();
    }

    [RelayCommand]
    public async Task LoadSettingsAsync()
    {
        try
        {
            IsBusy = true;
            var settings = await _settingsService.GetSettingsAsync();
            AutoTranscribe = settings.AutoTranscribe;
            AutoSummarize = settings.AutoSummarize;
            AutoStartEnabled = settings.AutoStartEnabled;
            AutoStopEnabled = settings.AutoStopEnabled;
            PreNotifyDelay = settings.PreNotifyDelay;
            RepeatNotifyDelay = settings.RepeatNotifyDelay;
        }
        catch (Exception ex)
        {
            await ShowToastAsync($"Erreur de chargement des paramètres : {ex.Message}", true);
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    public async Task SaveSettingsAsync()
    {
        try
        {
            IsBusy = true;
            await _settingsService.SaveSettingsAsync(new Models.SettingsModel
            {
                AutoTranscribe = AutoTranscribe,
                AutoSummarize = AutoSummarize,
                AutoStartEnabled = AutoStartEnabled,
                AutoStopEnabled = AutoStopEnabled,
                PreNotifyDelay = PreNotifyDelay,
                RepeatNotifyDelay = RepeatNotifyDelay
            });
            await ShowToastAsync("Paramètres enregistrés avec succès");
        }
        catch (Exception ex)
        {
            await ShowToastAsync($"Erreur lors de l'enregistrement : {ex.Message}", true);
        }
        finally
        {
            IsBusy = false;
        }
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
