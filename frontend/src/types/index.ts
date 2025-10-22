export enum UserRole {
  ADMIN = 'admin',
  USER = 'user',
  VIEWER = 'viewer',
}

export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export enum CameraStatus {
  ONLINE = 'online',
  OFFLINE = 'offline',
  ERROR = 'error',
  RECORDING = 'recording',
}

export enum RecordingMode {
  CONTINUOUS = 'continuous',
  MOTION = 'motion',
  SCHEDULED = 'scheduled',
  DISABLED = 'disabled',
}

export interface MotionRegion {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface Camera {
  id: number;
  name: string;
  description?: string;
  stream_url: string;
  protocol: string;
  username?: string;
  password?: string;
  resolution: string;
  fps: number;
  codec: string;
  recording_mode: RecordingMode;
  recording_quality: number;
  max_recording_days: number;
  motion_detection_enabled: boolean;
  motion_sensitivity: number;
  motion_regions?: MotionRegion[];
  status: CameraStatus;
  last_seen?: string;
  is_active: boolean;
  owner_id: number;
  created_at: string;
  updated_at?: string;
}

export interface CameraCreate {
  name: string;
  description?: string;
  stream_url: string;
  protocol?: string;
  username?: string;
  password?: string;
  resolution?: string;
  fps?: number;
  codec?: string;
  recording_mode?: RecordingMode;
  recording_quality?: number;
  max_recording_days?: number;
  motion_detection_enabled?: boolean;
  motion_sensitivity?: number;
  motion_regions?: MotionRegion[];
}

export interface CameraUpdate extends Partial<CameraCreate> {
  is_active?: boolean;
}

export enum RecordingType {
  CONTINUOUS = 'continuous',
  MOTION = 'motion',
  MANUAL = 'manual',
  SCHEDULED = 'scheduled',
}

export interface Recording {
  id: number;
  camera_id: number;
  file_path: string;
  file_size?: number;
  duration?: number;
  recording_type: RecordingType;
  start_time: string;
  end_time?: string;
  codec?: string;
  resolution?: string;
  fps?: number;
  bitrate?: number;
  thumbnail_path?: string;
  created_at: string;
}

export enum EventType {
  MOTION_DETECTED = 'motion_detected',
  OBJECT_DETECTED = 'object_detected',
  CAMERA_ONLINE = 'camera_online',
  CAMERA_OFFLINE = 'camera_offline',
  RECORDING_STARTED = 'recording_started',
  RECORDING_STOPPED = 'recording_stopped',
  STORAGE_WARNING = 'storage_warning',
  ERROR = 'error',
}

export interface Event {
  id: number;
  camera_id?: number;
  recording_id?: number;
  user_id?: number;
  event_type: EventType;
  title: string;
  description?: string;
  event_data?: Record<string, any>;
  created_at: string;
}
