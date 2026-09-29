import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export const fetchHealth = () => axios.get(`${API_URL}/health`);
export const fetchTwinState = (engineId) => axios.get(`${API_URL}/twin/state/${engineId}`);
export const fetchEngineHistory = (engineId) => axios.get(`${API_URL}/engine/${engineId}/history`);
export const fetchExplanation = (engineId) => axios.get(`${API_URL}/explain/${engineId}`);
export const startReplay = (engineId) => axios.post(`${API_URL}/replay/start`, { engine_id: engineId });
export const stopReplay = () => axios.post(`${API_URL}/replay/stop`);
export const getReplayStatus = () => axios.get(`${API_URL}/replay/status`);
