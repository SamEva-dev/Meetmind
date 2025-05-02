using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace UIMeetMind.Converters;

public class StatutToTextColorConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
    {
        return value?.ToString().ToLowerInvariant() switch
        {
            "summarized" => Color.FromArgb("#7E57C2"), // plus foncé que #D1C4E9
            "transcribed" => Color.FromArgb("#388E3C"), // plus foncé que #C8E6C9
            "inprogress" => Color.FromArgb("#1976D2"), // plus foncé que #BBDEFB
            "completed" => Color.FromArgb("#6091fa"),
            _ => Colors.Gray,
        };
    }

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        => throw new NotImplementedException();
}