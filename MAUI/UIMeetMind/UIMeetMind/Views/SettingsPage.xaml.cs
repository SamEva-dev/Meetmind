using UIMeetMind.ViewModels;

namespace UIMeetMind.Views;

public partial class SettingsPage : ContentPage
{
	public SettingsPage(SettingsViewModel settings)
	{
		InitializeComponent();

        BindingContext = settings;
    }
}