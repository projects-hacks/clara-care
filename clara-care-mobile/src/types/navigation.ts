export type RootStackParamList = {
  Login: undefined;
  Signup: undefined;
  Main: undefined;
  Onboarding: undefined;
};

export type OnboardingStackParamList = {
  Step1: undefined;
  Step2: { patient_id: string };
  Step3: { patient_id: string };
};
