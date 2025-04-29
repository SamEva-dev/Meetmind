using UIMeetMind.ViewModels;

namespace UIMeetMind
{
    public partial class MainPage : ContentPage
    {
        private readonly IDispatcherTimer _blinkTimer;
        private bool _blinkState = true;
        public MainPage(MainViewModel viewModel)
        {
            InitializeComponent();
            BindingContext = viewModel;

            _blinkTimer = Dispatcher.CreateTimer();
            _blinkTimer.Interval = TimeSpan.FromMilliseconds(700);
            _blinkTimer.Tick += (s, e) => {
                if (recordIcon != null)
                {
                    _blinkState = !_blinkState;
                    recordIcon.Opacity = _blinkState ? 1 : 0.3;
                }
            };

            BindingContextChanged += (s, e) => {
                if (BindingContext is ViewModels.MainViewModel vm)
                {
                    vm.PropertyChanged += (sender, args) => {
                        if (args.PropertyName == nameof(vm.HasRecordingInProgress))
                        {
                            if (vm.HasRecordingInProgress) _blinkTimer.Start();
                            else
                            {
                                _blinkTimer.Stop();
                                recordIcon.Opacity = 0; // Masqué par défaut
                            }
                        }
                    };
                }
            };
        }
    }
}
