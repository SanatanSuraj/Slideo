'use client';

import { Provider } from 'react-redux';
import { store } from '../store/store';
import { AuthInitializer } from './AuthInitializer';

export function Providers({ children }: { children: React.ReactNode }) {
  return <Provider store={store}>
      <AuthInitializer>
        {children}
      </AuthInitializer>
  </Provider>;
}
