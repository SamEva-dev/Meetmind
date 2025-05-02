using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace UIMeetMind.Models;

public class SettingsModel
{
    public bool AutoTranscribe { get; set; }
    public bool AutoSummarize { get; set; }
    public bool AutoStartEnabled { get; set; }
    public bool AutoStopEnabled { get; set; }
    public int PreNotifyDelay { get; set; }
    public int RepeatNotifyDelay { get; set; }
}