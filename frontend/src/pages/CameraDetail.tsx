import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { apiClient } from '@/services/api';
import { Camera, Recording } from '@/types';
import { VideoPlayer } from '@/components/VideoPlayer';
import { FiArrowLeft, FiPlay, FiSquare, FiSettings, FiTrash2, FiDownload } from 'react-icons/fi';
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
  const [activeTab, setActiveTab] = useState<'live' | 'recordings'>('live');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      loadCamera(parseInt(id));
      loadRecordings(parseInt(id));
    }
  }, [id]);

  const loadCamera = async (cameraId: number) => {
    try {
      const data = await apiClient.getCamera(cameraId);
      setCamera(data);
    } catch (error) {
      toast.error('Failed to load camera');
    } finally {
      setLoading(false);
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

            <div className="flex gap-4">
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
            </div>
          </div>
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
