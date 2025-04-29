using Berry.Maui;
using CommunityToolkit.Maui;
using Microsoft.Extensions.Logging;
using Plugin.Maui.Audio;
using UIMeetMind.Services;
using UIMeetMind.Utils;
using UIMeetMind.ViewModels;

namespace UIMeetMind
{
    public static class MauiProgram
    {
        public static MauiApp CreateMauiApp()
        {
            LoggerConfig.Init();

            var builder = MauiApp.CreateBuilder();
            builder
                .UseMauiApp<App>()
                .UseMauiCommunityToolkit(options => options.SetShouldEnableSnackbarOnWindows(true))
                .ConfigureFonts(fonts =>
                {
                    fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
                    fonts.AddFont("OpenSans-Semibold.ttf", "OpenSansSemibold");
                });

            builder.Services
                .AddSingleton(AudioManager.Current)
           .AddSingleton<MainViewModel>()
           .AddSingleton<MainPage>()
            .AddSingleton<ApiService>();

#if DEBUG
            builder.Logging.AddDebug();
#endif

            return builder.Build();
        }
    }
}
