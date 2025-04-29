using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace UIMeetMind.Models;

public class MeetingFile
{
    public string FileName { get; set; }
    public string FilePath { get; set; }
    public string Type { get; set; } 
    public DateTime Date { get; set; }
}