import axios, { AxiosInstance } from 'axios';
import {
  User,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
  Camera,
  CameraCreate,
  CameraUpdate,
  Recording,
  Event,
  RecordingType,
  EventType,
} from '@/types';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: '/api',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add token to requests
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle 401 errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth endpoints
  async login(data: LoginRequest): Promise<AuthResponse> {
    const formData = new FormData();
    formData.append('username', data.username);
    formData.append('password', data.password);

    const response = await this.client.post<AuthResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async register(data: RegisterRequest): Promise<User> {
    const response = await this.client.post<User>('/auth/register', data);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/auth/me');
    return response.data;
  }

  // Camera endpoints
  async getCameras(): Promise<Camera[]> {
    const response = await this.client.get<Camera[]>('/cameras');
    return response.data;
  }

  async getCamera(id: number): Promise<Camera> {
    const response = await this.client.get<Camera>(`/cameras/${id}`);
    return response.data;
  }

  async createCamera(data: CameraCreate): Promise<Camera> {
    const response = await this.client.post<Camera>('/cameras', data);
    return response.data;
  }

  async updateCamera(id: number, data: CameraUpdate): Promise<Camera> {
    const response = await this.client.put<Camera>(`/cameras/${id}`, data);
    return response.data;
  }

  async deleteCamera(id: number): Promise<void> {
    await this.client.delete(`/cameras/${id}`);
  }

  // Stream endpoints
  async startStream(cameraId: number): Promise<{ playlist_url: string }> {
    const response = await this.client.post(`/stream/${cameraId}/start`);
    return response.data;
  }

  async stopStream(cameraId: number): Promise<void> {
    await this.client.post(`/stream/${cameraId}/stop`);
  }

  async getStreamStatus(cameraId: number): Promise<{ is_active: boolean }> {
    const response = await this.client.get(`/stream/${cameraId}/status`);
    return response.data;
  }

  // Recording endpoints
  async startRecording(
    cameraId: number,
    recordingType: RecordingType = RecordingType.MANUAL,
    duration?: number
  ): Promise<{ recording_id: number }> {
    const response = await this.client.post(`/recordings/${cameraId}/start`, null, {
      params: { recording_type: recordingType, duration },
    });
    return response.data;
  }

  async stopRecording(recordingId: number): Promise<void> {
    await this.client.post(`/recordings/${recordingId}/stop`);
  }

  async getCameraRecordings(cameraId: number): Promise<Recording[]> {
    const response = await this.client.get<Recording[]>(`/recordings/camera/${cameraId}`);
    return response.data;
  }

  getRecordingDownloadUrl(recordingId: number): string {
    return `/api/recordings/${recordingId}/download`;
  }

  getRecordingThumbnailUrl(recordingId: number): string {
    return `/api/recordings/${recordingId}/thumbnail`;
  }

  // Event endpoints
  async getEvents(cameraId?: number, eventType?: EventType): Promise<Event[]> {
    const response = await this.client.get<Event[]>('/events', {
      params: { camera_id: cameraId, event_type: eventType },
    });
    return response.data;
  }

  async getEvent(id: number): Promise<Event> {
    const response = await this.client.get<Event>(`/events/${id}`);
    return response.data;
  }

  // PTZ endpoints
  async ptzContinuousMove(
    cameraId: number,
    pan: number,
    tilt: number,
    zoom: number,
    timeout: number = 1
  ): Promise<void> {
    await this.client.post(`/ptz/${cameraId}/continuous-move`, {
      pan,
      tilt,
      zoom,
      timeout,
    });
  }

  async ptzAbsoluteMove(
    cameraId: number,
    pan: number,
    tilt: number,
    zoom: number
  ): Promise<void> {
    await this.client.post(`/ptz/${cameraId}/absolute-move`, {
      pan,
      tilt,
      zoom,
    });
  }

  async ptzRelativeMove(
    cameraId: number,
    pan: number,
    tilt: number,
    zoom: number
  ): Promise<void> {
    await this.client.post(`/ptz/${cameraId}/relative-move`, {
      pan,
      tilt,
      zoom,
    });
  }

  async ptzStop(cameraId: number): Promise<void> {
    await this.client.post(`/ptz/${cameraId}/stop`);
  }

  async getPtzPresets(cameraId: number): Promise<any[]> {
    const response = await this.client.get(`/ptz/${cameraId}/presets`);
    return response.data.presets;
  }

  async ptzGotoPreset(cameraId: number, presetToken: string): Promise<void> {
    await this.client.post(`/ptz/${cameraId}/goto-preset`, {
      preset_token: presetToken,
    });
  }

  async ptzSetPreset(cameraId: number, name: string): Promise<{ preset_token: string }> {
    const response = await this.client.post(`/ptz/${cameraId}/set-preset`, { name });
    return response.data;
  }

  async ptzRemovePreset(cameraId: number, presetToken: string): Promise<void> {
    await this.client.delete(`/ptz/${cameraId}/presets/${presetToken}`);
  }

  async ptzGotoHome(cameraId: number): Promise<void> {
    await this.client.post(`/ptz/${cameraId}/home`);
  }

  async ptzSetHome(cameraId: number): Promise<void> {
    await this.client.post(`/ptz/${cameraId}/set-home`);
  }
}

export const apiClient = new ApiClient();
