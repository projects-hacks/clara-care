import apiClient from './client';
import { Patient, Conversation, Alert, CreatePatientPayload, PersonalizePayload, SchedulePayload } from '../types';

export const getPatients = async () => {
  const { data } = await apiClient.get<{ patients: Patient[] }>('/api/patients');
  return data.patients;
};

export const getPatientDetail = async (patientId: string) => {
  const { data } = await apiClient.get(`/api/patients/${patientId}`);
  return data;
};

export const getConversations = async (patientId: string) => {
  const { data } = await apiClient.get<{ conversations: Conversation[] }>(`/api/conversations?patient_id=${patientId}`);
  return data.conversations;
};

export const getAlerts = async (patientId: string) => {
  const { data } = await apiClient.get<{ alerts: Alert[] }>(`/api/alerts?patient_id=${patientId}`);
  return data.alerts;
};

export const acknowledgeAlert = async (alertId: string, acknowledgedBy: string) => {
  const { data } = await apiClient.patch<{ success: boolean }>(`/api/alerts/${alertId}`, { acknowledged_by: acknowledgedBy });
  return data.success;
};

// Onboarding Endpoints
export const createPatient = async (patientData: CreatePatientPayload) => {
  const { data } = await apiClient.post<{ patient_id: string }>('/api/onboarding/patient', patientData);
  return data;
};

export const personalizePatient = async (payload: PersonalizePayload) => {
  const { data } = await apiClient.post('/api/onboarding/personalize', payload);
  return data;
};

export const schedulePatient = async (payload: SchedulePayload) => {
  const { data } = await apiClient.post('/api/onboarding/schedule', payload);
  return data;
};
