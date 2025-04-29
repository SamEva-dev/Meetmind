
using Serilog;

namespace UIMeetMind.Utils;

public static class LoggerConfig
{
    public static ILogger Logger;

    public static void Init()
    {
        var logDirectory = Path.Combine(FileSystem.AppDataDirectory, "logs");
        Directory.CreateDirectory(logDirectory);
        var logPath = Path.Combine(logDirectory, $"meetmind_log_{DateTime.Now:yyyyMMdd}.txt");

        Logger = new LoggerConfiguration()
            .MinimumLevel.Debug()
            .WriteTo.File(logPath, rollingInterval: RollingInterval.Day, retainedFileCountLimit: 7)
            .CreateLogger();
    }
}