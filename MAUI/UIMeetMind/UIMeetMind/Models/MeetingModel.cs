using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace UIMeetMind.Models;

public class MeetingModel
{
    public string MeetingId { get; set; }
    public string Status { get; set; }

    public string StartTimestamp { get; set; }
    public string EndTimestamp { get; set; }
}