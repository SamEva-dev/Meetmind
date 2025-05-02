using CommunityToolkit.Maui;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Plugin.Maui.Audio;
using UIMeetMind.Services;
using UIMeetMind.Utils;
using UIMeetMind.ViewModels;
using UIMeetMind.Views;


namespace UIMeetMind
{
    public static class MauiProgram
    {
        public static MauiApp CreateMauiApp()
        {
            LoggerConfig.Init();

            var builder = MauiApp.CreateBuilder();

            // Charger configuration
            builder.Configuration.AddJsonFile("appsettings.json", optional: false, reloadOnChange: true);
            var config = builder.Configuration;

            // Base address dynamique
            var baseUrl = DeviceInfo.Platform == DevicePlatform.Android
                ? config["ApiBaseUrl"] ?? "http://10.0.2.2:8000/"
                : config["ApiBaseUrl"] ?? "http://localhost:8000/";

            builder
                .UseMauiApp<App>()
                .UseMauiCommunityToolkit(options => options.SetShouldEnableSnackbarOnWindows(true))
                .ConfigureFonts(fonts =>
                {
                    fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
                    fonts.AddFont("OpenSans-Semibold.ttf", "OpenSansSemibold");
                });

#if DEBUG
            builder.Logging.AddDebug();
#endif
            builder.Services.AddSingleton(AudioManager.Current);

            // 🔧 Enregistrement du HttpClient + service API
            builder.Services.AddHttpClient<ISettingsService, SettingsService>(client =>
            {
                client.BaseAddress = new Uri(baseUrl);
            });

            builder.Services.AddHttpClient<IHealthService, HealthService>(client =>
            {
                client.BaseAddress = new Uri(baseUrl);
            });

            builder.Services.AddHttpClient<INotificationService, NotificationService>(client =>
            {
                client.BaseAddress = new Uri(baseUrl);
            });

            builder.Services.AddHttpClient<IMeetingService, MeetingService>(client =>
    client.BaseAddress = new Uri(baseUrl));
            builder.Services.AddHttpClient<IFileService, FileService>(client =>
                client.BaseAddress = new Uri(baseUrl));


            builder.Services.AddSingleton<ApiService>();

            // 💡 Enregistrement des pages et ViewModels
            builder.Services.AddSingleton<MainViewModel>();
            builder.Services.AddSingleton<MainPage>();
            builder.Services.AddTransient<SettingsPage>();
            builder.Services.AddTransient<SettingsViewModel>();

            return builder.Build();
        }
    }
}
