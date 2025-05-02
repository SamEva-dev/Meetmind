
using UIMeetMind.Models;

namespace UIMeetMind.Services;

public interface INotificationService
{
    Task<List<NotificationModel>> GetNotificationsAsync();
    Task ClearNotificationsAsync();
}
