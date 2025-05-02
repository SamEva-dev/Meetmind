using UIMeetMind.Views;

namespace UIMeetMind
{
    public partial class App : Application
    {
        public App()
        {
            InitializeComponent();
            MainPage = new AppShell();
        }
       
    }
}