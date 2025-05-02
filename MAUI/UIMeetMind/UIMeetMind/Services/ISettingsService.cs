
using UIMeetMind.Models;

namespace UIMeetMind.Services;

public interface ISettingsService
{
    Task<SettingsModel> GetSettingsAsync();
    Task SaveSettingsAsync(SettingsModel settings);
}