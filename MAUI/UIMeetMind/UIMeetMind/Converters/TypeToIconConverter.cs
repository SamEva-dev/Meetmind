using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace UIMeetMind.Converters;

public class TypeToIconConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
    {
        return value?.ToString() switch
        {
            "pre_notify" => "bell_icon.png",
            "auto_start" => "play_icon.png",
            "auto_stop" => "stop_icon.png",
            _ => "info_icon.png"
        };
    }

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture) => throw new NotImplementedException();
}

public class TypeToBackgroundConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
    {
        return value?.ToString() switch
        {
            "pre_notify" => Color.FromArgb("#FFFBEA"),
            "auto_start" => Color.FromArgb("#E6FFFA"),
            "auto_stop" => Color.FromArgb("#FEF2F2"),
            _ => Color.FromArgb("#F3F4F6")
        };
    }

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture) => throw new NotImplementedException();
}

public class TypeToBorderConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
    {
        return value?.ToString() switch
        {
            "pre_notify" => Color.FromArgb("#FBBF24"),
            "auto_start" => Color.FromArgb("#10B981"),
            "auto_stop" => Color.FromArgb("#EF4444"),
            _ => Color.FromArgb("#9CA3AF")
        };
    }

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture) => throw new NotImplementedException();
}