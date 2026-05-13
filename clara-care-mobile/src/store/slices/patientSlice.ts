import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Patient, Conversation, Alert, PatientDetail } from '../../types';
import * as api from '../../api/endpoints';

interface PatientState {
  patients: Patient[];
  activePatientId: string | null;
  detail: PatientDetail | null;
  conversations: Conversation[];
  alerts: Alert[];
  loading: boolean;
  error: string | null;
}

const initialState: PatientState = {
  patients: [],
  activePatientId: null,
  detail: null,
  conversations: [],
  alerts: [],
  loading: false,
  error: null,
};

export const fetchPatients = createAsyncThunk('patient/fetchAll', async () => {
  return await api.getPatients();
});

export const fetchPatientDetail = createAsyncThunk('patient/fetchDetail', async (patientId: string) => {
  return await api.getPatientDetail(patientId);
});

export const fetchConversations = createAsyncThunk('patient/fetchConversations', async (patientId: string) => {
  return await api.getConversations(patientId);
});

export const fetchAlerts = createAsyncThunk('patient/fetchAlerts', async (patientId: string) => {
  return await api.getAlerts(patientId);
});

const patientSlice = createSlice({
  name: 'patient',
  initialState,
  reducers: {
    setActivePatient(state, action: PayloadAction<string>) {
      state.activePatientId = action.payload;
    },
  },
  extraReducers: (builder) => {
    // fetchPatients
    builder.addCase(fetchPatients.pending, (state) => { state.loading = true; state.error = null; });
    builder.addCase(fetchPatients.fulfilled, (state, action) => {
      state.loading = false;
      state.patients = action.payload;
      if (action.payload.length > 0 && !state.activePatientId) {
        state.activePatientId = action.payload[0].id;
      }
    });
    builder.addCase(fetchPatients.rejected, (state, action) => {
      state.loading = false;
      state.error = action.error.message || 'Failed to fetch patients';
    });

    // fetchPatientDetail
    builder.addCase(fetchPatientDetail.fulfilled, (state, action) => { state.detail = action.payload; });

    // fetchConversations
    builder.addCase(fetchConversations.fulfilled, (state, action) => { state.conversations = action.payload; });

    // fetchAlerts
    builder.addCase(fetchAlerts.fulfilled, (state, action) => { state.alerts = action.payload; });
  },
});

export const { setActivePatient } = patientSlice.actions;
export default patientSlice.reducer;
