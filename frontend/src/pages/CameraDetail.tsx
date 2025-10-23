import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { apiClient } from '@/services/api';
import { Camera, Recording, Event, EventType } from '@/types';
import { VideoPlayer } from '@/components/VideoPlayer';
import { PTZControls } from '@/components/PTZControls';
import { FiArrowLeft, FiPlay, FiSquare, FiSettings, FiTrash2, FiDownload, FiEye } from 'react-icons/fi';
import toast from 'react-hot-toast';
import { format } from 'date-fns';

export const CameraDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [camera, setCamera] = useState<Camera | null>(null);
  const [recordings, setRecordings] = useState<Recording[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamUrl, setStreamUrl] = useState<string>('');
  const [isRecording, setIsRecording] = useState(false);
  const [activeTab, setActiveTab] = useState<'live' | 'recordings' | 'ptz'>('live');
  const [loading, setLoading] = useState(true);
  const [motionDetectionEnabled, setMotionDetectionEnabled] = useState(false);
  const [motionDetectionActive, setMotionDetectionActive] = useState(false);
  const [motionEvents, setMotionEvents] = useState<Event[]>([]);

  useEffect(() => {
    if (id) {
      loadCamera(parseInt(id));
      loadRecordings(parseInt(id));
      loadMotionDetectionStatus(parseInt(id));
      loadMotionEvents(parseInt(id));
    }
  }, [id]);

  const loadCamera = async (cameraId: number) => {
    try {
      const data = await apiClient.getCamera(cameraId);
      setCamera(data);
      setMotionDetectionEnabled(data.motion_detection_enabled || false);
    } catch (error) {
      toast.error('Failed to load camera');
    } finally {
      setLoading(false);
    }
  };

  const loadMotionDetectionStatus = async (cameraId: number) => {
    try {
      const status = await apiClient.getMotionDetectionStatus(cameraId);
      setMotionDetectionEnabled(status.enabled);
      setMotionDetectionActive(status.active);
    } catch (error) {
      console.error('Failed to load motion detection status', error);
    }
  };

  const loadMotionEvents = async (cameraId: number) => {
    try {
      const events = await apiClient.getEvents(cameraId, EventType.MOTION_DETECTED);
      setMotionEvents(events.slice(0, 5)); // Last 5 events
    } catch (error) {
      console.error('Failed to load motion events', error);
    }
  };

  const loadRecordings = async (cameraId: number) => {
    try {
      const data = await apiClient.getCameraRecordings(cameraId);
      setRecordings(data);
    } catch (error) {
      console.error('Failed to load recordings', error);
    }
  };

  const handleStartStream = async () => {
    if (!camera) return;

    try {
      const response = await apiClient.startStream(camera.id);
      setStreamUrl(response.playlist_url);
      setIsStreaming(true);
      toast.success('Stream started');
    } catch (error) {
      toast.error('Failed to start stream');
    }
  };

  const handleStopStream = async () => {
    if (!camera) return;

    try {
      await apiClient.stopStream(camera.id);
      setIsStreaming(false);
      setStreamUrl('');
      toast.success('Stream stopped');
    } catch (error) {
      toast.error('Failed to stop stream');
    }
  };

  const handleStartRecording = async () => {
    if (!camera) return;

    try {
      await apiClient.startRecording(camera.id);
      setIsRecording(true);
      toast.success('Recording started');
    } catch (error) {
      toast.error('Failed to start recording');
    }
  };

  const handleToggleMotionDetection = async () => {
    if (!camera) return;

    try {
      const newEnabled = !motionDetectionEnabled;
      await apiClient.toggleMotionDetection(camera.id, newEnabled);
      setMotionDetectionEnabled(newEnabled);
      setMotionDetectionActive(newEnabled);
      toast.success(`Motion detection ${newEnabled ? 'enabled' : 'disabled'}`);

      // Reload events if enabled
      if (newEnabled) {
        loadMotionEvents(camera.id);
      }
    } catch (error) {
      toast.error('Failed to toggle motion detection');
    }
  };

  const handleDeleteCamera = async () => {
    if (!camera || !window.confirm('Are you sure you want to delete this camera?')) return;

    try {
      await apiClient.deleteCamera(camera.id);
      toast.success('Camera deleted');
      navigate('/');
    } catch (error) {
      toast.error('Failed to delete camera');
    }
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return 'N/A';
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hrs}h ${mins}m ${secs}s`;
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return 'N/A';
    const mb = bytes / (1024 * 1024);
    if (mb > 1024) {
      return `${(mb / 1024).toFixed(2)} GB`;
    }
    return `${mb.toFixed(2)} MB`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  if (!camera) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400">Camera not found</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <Link to="/" className="inline-flex items-center gap-2 text-blue-500 hover:text-blue-400">
          <FiArrowLeft /> Back to Dashboard
        </Link>
      </div>

      <div className="flex justify-between items-start mb-6">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">{camera.name}</h1>
          {camera.description && <p className="text-gray-400">{camera.description}</p>}
        </div>
        <div className="flex gap-2">
          <Link
            to={`/cameras/${camera.id}/edit`}
            className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 flex items-center gap-2"
          >
            <FiSettings /> Settings
          </Link>
          <button
            onClick={handleDeleteCamera}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2"
          >
            <FiTrash2 /> Delete
          </button>
        </div>
      </div>

      <div className="mb-6">
        <div className="flex gap-4 mb-4">
          <button
            onClick={() => setActiveTab('live')}
            className={`px-4 py-2 rounded-lg ${
              activeTab === 'live'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Live View
          </button>
          <button
            onClick={() => setActiveTab('recordings')}
            className={`px-4 py-2 rounded-lg ${
              activeTab === 'recordings'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            Recordings ({recordings.length})
          </button>
          {camera?.protocol === 'onvif' && (
            <button
              onClick={() => setActiveTab('ptz')}
              className={`px-4 py-2 rounded-lg ${
                activeTab === 'ptz'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              PTZ Controls
            </button>
          )}
        </div>

        {activeTab === 'live' && (
          <div>
            <div className="bg-gray-800 rounded-lg overflow-hidden mb-4">
              <div className="aspect-video bg-gray-900 flex items-center justify-center">
                {isStreaming && streamUrl ? (
                  <VideoPlayer src={streamUrl} />
                ) : (
                  <div className="text-center">
                    <p className="text-gray-400 mb-4">Stream not active</p>
                    <button
                      onClick={handleStartStream}
                      className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 mx-auto"
                    >
                      <FiPlay /> Start Stream
                    </button>
                  </div>
                )}
              </div>
            </div>

            <div className="flex gap-4 mb-6">
              {isStreaming ? (
                <button
                  onClick={handleStopStream}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2"
                >
                  <FiSquare /> Stop Stream
                </button>
              ) : null}

              {!isRecording ? (
                <button
                  onClick={handleStartRecording}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
                >
                  <FiPlay /> Start Recording
                </button>
              ) : (
                <button className="px-4 py-2 bg-red-600 text-white rounded-lg flex items-center gap-2">
                  <span className="animate-pulse">●</span> Recording...
                </button>
              )}

              <button
                onClick={handleToggleMotionDetection}
                className={`px-4 py-2 rounded-lg flex items-center gap-2 ${
                  motionDetectionEnabled
                    ? 'bg-green-600 hover:bg-green-700 text-white'
                    : 'bg-gray-700 hover:bg-gray-600 text-white'
                }`}
              >
                <FiEye />
                {motionDetectionEnabled ? 'Motion Detection ON' : 'Motion Detection OFF'}
                {motionDetectionActive && (
                  <span className="ml-1 w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                )}
              </button>
            </div>

            {/* Motion Events */}
            {motionDetectionEnabled && motionEvents.length > 0 && (
              <div className="bg-gray-800 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                  <FiEye /> Recent Motion Events
                </h3>
                <div className="space-y-2">
                  {motionEvents.map(event => (
                    <div key={event.id} className="p-3 bg-gray-700 rounded-lg">
                      <div className="flex justify-between items-start">
                        <div>
                          <div className="text-sm text-white font-medium">{event.title}</div>
                          <div className="text-xs text-gray-400 mt-1">{event.description}</div>
                        </div>
                        <div className="text-xs text-gray-500">
                          {format(new Date(event.created_at), 'PPpp')}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'ptz' && camera && (
          <PTZControls cameraId={camera.id} isOnvif={camera.protocol === 'onvif'} />
        )}

        {activeTab === 'recordings' && (
          <div className="bg-gray-800 rounded-lg p-6">
            {recordings.length === 0 ? (
              <p className="text-center text-gray-400">No recordings available</p>
            ) : (
              <div className="space-y-4">
                {recordings.map((recording) => (
                  <div
                    key={recording.id}
                    className="flex items-center gap-4 p-4 bg-gray-700 rounded-lg"
                  >
                    {recording.thumbnail_path && (
                      <img
                        src={apiClient.getRecordingThumbnailUrl(recording.id)}
                        alt="Thumbnail"
                        className="w-32 h-20 object-cover rounded"
                      />
                    )}
                    <div className="flex-1">
                      <p className="text-white font-medium">
                        {format(new Date(recording.start_time), 'PPpp')}
                      </p>
                      <div className="flex gap-4 text-sm text-gray-400 mt-1">
                        <span>Duration: {formatDuration(recording.duration)}</span>
                        <span>Size: {formatFileSize(recording.file_size)}</span>
                        <span>Type: {recording.recording_type}</span>
                      </div>
                    </div>
                    <a
                      href={apiClient.getRecordingDownloadUrl(recording.id)}
                      download
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
                    >
                      <FiDownload /> Download
                    </a>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
