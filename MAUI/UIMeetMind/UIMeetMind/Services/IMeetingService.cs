
using UIMeetMind.Models;

namespace UIMeetMind.Services;

public interface IMeetingService
{
    Task<List<MeetingModel>> GetTodayMeetingsAsync();
}