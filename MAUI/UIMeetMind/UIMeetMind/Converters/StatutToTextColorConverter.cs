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
        return value?.ToString() switch
        {
            "Summarized" => Color.FromArgb("#7E57C2"), // plus foncé que #D1C4E9
            "Transcribed" => Color.FromArgb("#388E3C"), // plus foncé que #C8E6C9
            "In Progress" => Color.FromArgb("#1976D2"), // plus foncé que #BBDEFB
            "Completed" => Color.FromArgb("#6091fa"),
            _ => Colors.Gray,
        };
    }

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        => throw new NotImplementedException();
}