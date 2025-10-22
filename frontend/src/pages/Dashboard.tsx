import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiClient } from '@/services/api';
import { Camera, CameraStatus } from '@/types';
import { FiPlus, FiVideo, FiVideoOff } from 'react-icons/fi';
import toast from 'react-hot-toast';

export const Dashboard: React.FC = () => {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCameras();
  }, []);

  const loadCameras = async () => {
    try {
      const data = await apiClient.getCameras();
      setCameras(data);
    } catch (error) {
      toast.error('Failed to load cameras');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: CameraStatus) => {
    switch (status) {
      case CameraStatus.ONLINE:
        return 'text-green-500';
      case CameraStatus.RECORDING:
        return 'text-red-500';
      case CameraStatus.OFFLINE:
        return 'text-gray-500';
      case CameraStatus.ERROR:
        return 'text-yellow-500';
      default:
        return 'text-gray-500';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-white">Loading...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-white">Cameras</h1>
        <Link
          to="/cameras/new"
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <FiPlus /> Add Camera
        </Link>
      </div>

      {cameras.length === 0 ? (
        <div className="text-center py-12">
          <FiVideoOff className="mx-auto text-6xl text-gray-500 mb-4" />
          <p className="text-gray-400 mb-4">No cameras configured yet</p>
          <Link
            to="/cameras/new"
            className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            <FiPlus /> Add Your First Camera
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cameras.map((camera) => (
            <Link
              key={camera.id}
              to={`/cameras/${camera.id}`}
              className="bg-gray-800 rounded-lg overflow-hidden hover:ring-2 hover:ring-blue-500 transition"
            >
              <div className="aspect-video bg-gray-900 flex items-center justify-center">
                <FiVideo className="text-6xl text-gray-600" />
              </div>
              <div className="p-4">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-lg font-semibold text-white">{camera.name}</h3>
                  <span className={`text-sm ${getStatusColor(camera.status)}`}>
                    {camera.status}
                  </span>
                </div>
                {camera.description && (
                  <p className="text-gray-400 text-sm mb-2">{camera.description}</p>
                )}
                <div className="flex gap-2 text-xs text-gray-500">
                  <span>{camera.resolution}</span>
                  <span>•</span>
                  <span>{camera.fps} FPS</span>
                  <span>•</span>
                  <span>{camera.codec.toUpperCase()}</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};
