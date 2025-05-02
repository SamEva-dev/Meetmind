using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace UIMeetMind.Models;

public class UserSettings
{
    public bool AutoTranscribe { get; set; } = true;
    public bool AutoSummarize { get; set; } = true;
    public bool AutoStartMeeting { get; set; } = false;
    public List<int> NotifyMinutes { get; set; } = new() { 10, 5, 1 };

    public static string DefaultPath => Path.Combine(FileSystem.AppDataDirectory, "user_settings.json");
}