
using System.Globalization;

namespace UIMeetMind.Converters;

public class StatutToColorConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
    {
        return value?.ToString() switch
        {
            "Summarized" => Color.FromArgb("#D1C4E9"),
            "Transcribed" => Color.FromArgb("#C8E6C9"),
            "In Progress" => Color.FromArgb("#BBDEFB"),
            "Completed" => Color.FromArgb("#60faf8"),
            _ => Colors.LightGray,
        };
    }

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        => throw new NotImplementedException();
}