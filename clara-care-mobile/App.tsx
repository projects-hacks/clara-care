import * as Sentry from '@sentry/react-native';
import { Provider } from 'react-redux';
import { store } from './src/store';
import AppNavigator from './src/navigation/AppNavigator';
import { SafeAreaProvider } from 'react-native-safe-area-context';

// Initialize Sentry for crash reporting
Sentry.init({
  dsn: 'https://deaa70b66ff1d058322dc566f38a7122@o4511385064767488.ingest.us.sentry.io/4511385074663424',
  tracesSampleRate: 0.3,
  profilesSampleRate: 0.1,
  debug: __DEV__, // Show Sentry logs in dev mode
});

function App() {
  return (
    <Provider store={store}>
      <SafeAreaProvider>
        <AppNavigator />
      </SafeAreaProvider>
    </Provider>
  );
}

export default Sentry.wrap(App);
