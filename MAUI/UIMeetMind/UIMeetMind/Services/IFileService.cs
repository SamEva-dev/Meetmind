using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using UIMeetMind.Models;

namespace UIMeetMind.Services;

public interface IFileService
{
    Task<List<MeetingFile>> GetAudioFilesAsync();
    Task<List<MeetingFile>> GetTranscriptFilesAsync();
    Task<List<MeetingFile>> GetSummaryFilesAsync();
}