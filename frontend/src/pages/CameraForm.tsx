import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { apiClient } from '@/services/api';
import { CameraCreate, RecordingMode } from '@/types';
import { FiArrowLeft } from 'react-icons/fi';
import toast from 'react-hot-toast';

export const CameraForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = !!id;

  const [formData, setFormData] = useState<CameraCreate>({
    name: '',
    description: '',
    stream_url: '',
    protocol: 'rtsp',
    username: '',
    password: '',
    resolution: '1920x1080',
    fps: 15,
    codec: 'h264',
    recording_mode: RecordingMode.MOTION,
    recording_quality: 80,
    max_recording_days: 7,
    motion_detection_enabled: true,
    motion_sensitivity: 50,
  });

  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isEdit && id) {
      loadCamera(parseInt(id));
    }
  }, [id, isEdit]);

  const loadCamera = async (cameraId: number) => {
    try {
      const camera = await apiClient.getCamera(cameraId);
      setFormData({
        name: camera.name,
        description: camera.description,
        stream_url: camera.stream_url,
        protocol: camera.protocol,
        username: camera.username,
        password: camera.password,
        resolution: camera.resolution,
        fps: camera.fps,
        codec: camera.codec,
        recording_mode: camera.recording_mode,
        recording_quality: camera.recording_quality,
        max_recording_days: camera.max_recording_days,
        motion_detection_enabled: camera.motion_detection_enabled,
        motion_sensitivity: camera.motion_sensitivity,
      });
    } catch (error) {
      toast.error('Failed to load camera');
    }
  };

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target;

    if (type === 'checkbox') {
      const checked = (e.target as HTMLInputElement).checked;
      setFormData({ ...formData, [name]: checked });
    } else if (type === 'number') {
      setFormData({ ...formData, [name]: parseInt(value) || 0 });
    } else {
      setFormData({ ...formData, [name]: value });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      if (isEdit && id) {
        await apiClient.updateCamera(parseInt(id), formData);
        toast.success('Camera updated successfully');
      } else {
        await apiClient.createCamera(formData);
        toast.success('Camera created successfully');
      }
      navigate('/');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to save camera');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <div className="mb-6">
        <Link to="/" className="inline-flex items-center gap-2 text-blue-500 hover:text-blue-400">
          <FiArrowLeft /> Back to Dashboard
        </Link>
      </div>

      <h1 className="text-3xl font-bold text-white mb-8">
        {isEdit ? 'Edit Camera' : 'Add New Camera'}
      </h1>

      <form onSubmit={handleSubmit} className="space-y-6 bg-gray-800 p-6 rounded-lg">
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Camera Name *</label>
          <input
            type="text"
            name="name"
            required
            value={formData.name}
            onChange={handleChange}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows={3}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">Stream URL *</label>
          <input
            type="text"
            name="stream_url"
            required
            value={formData.stream_url}
            onChange={handleChange}
            placeholder="rtsp://192.168.1.100:554/stream"
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Protocol</label>
            <select
              name="protocol"
              value={formData.protocol}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="rtsp">RTSP</option>
              <option value="http">HTTP</option>
              <option value="onvif">ONVIF</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Recording Mode</label>
            <select
              name="recording_mode"
              value={formData.recording_mode}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value={RecordingMode.CONTINUOUS}>Continuous</option>
              <option value={RecordingMode.MOTION}>Motion Detection</option>
              <option value={RecordingMode.SCHEDULED}>Scheduled</option>
              <option value={RecordingMode.DISABLED}>Disabled</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Username</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Resolution</label>
            <select
              name="resolution"
              value={formData.resolution}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="1920x1080">1080p</option>
              <option value="1280x720">720p</option>
              <option value="640x480">480p</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">FPS</label>
            <input
              type="number"
              name="fps"
              value={formData.fps}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Codec</label>
            <select
              name="codec"
              value={formData.codec}
              onChange={handleChange}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="h264">H.264</option>
              <option value="h265">H.265</option>
              <option value="mjpeg">MJPEG</option>
            </select>
          </div>
        </div>

        <div>
          <label className="flex items-center gap-2 text-gray-300">
            <input
              type="checkbox"
              name="motion_detection_enabled"
              checked={formData.motion_detection_enabled}
              onChange={handleChange}
              className="rounded"
            />
            Enable Motion Detection
          </label>
        </div>

        {formData.motion_detection_enabled && (
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Motion Sensitivity: {formData.motion_sensitivity}
            </label>
            <input
              type="range"
              name="motion_sensitivity"
              min="0"
              max="100"
              value={formData.motion_sensitivity}
              onChange={handleChange}
              className="w-full"
            />
          </div>
        )}

        <div className="flex gap-4">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Saving...' : isEdit ? 'Update Camera' : 'Add Camera'}
          </button>
          <button
            type="button"
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};
