
namespace UIMeetMind.Services;

public interface IHealthService
{
    Task<bool> CheckHealthAsync();
}
