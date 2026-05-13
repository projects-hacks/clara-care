import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { User } from '@supabase/supabase-js';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isInitializing: boolean;
  hasPatients: boolean;
  onboardingCompleted: boolean;
}

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isInitializing: true,
  hasPatients: false, // We'll update this later
  onboardingCompleted: false,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setAuthSession(state, action: PayloadAction<{ user: User | null }>) {
      state.user = action.payload.user;
      state.isAuthenticated = !!action.payload.user;
      state.isInitializing = false;
    },
    setOnboardingCompleted(state, action: PayloadAction<boolean>) {
      state.onboardingCompleted = action.payload;
      state.hasPatients = action.payload; // If onboarding is done, they have patients
    },
  },
});

export const { setAuthSession, setOnboardingCompleted } = authSlice.actions;
export default authSlice.reducer;
