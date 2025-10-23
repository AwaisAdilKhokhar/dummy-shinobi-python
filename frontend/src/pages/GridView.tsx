import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import GridLayout from 'react-grid-layout';
import { apiClient } from '@/services/api';
import { Camera, CameraStatus } from '@/types';
import { VideoPlayer } from '@/components/VideoPlayer';
import { FiSettings, FiMaximize2 } from 'react-icons/fi';
import toast from 'react-hot-toast';
import 'react-grid-layout/css/styles.css';
import './GridView.css';

interface CameraStream {
  cameraId: number;
  streamUrl: string | null;
  isStreaming: boolean;
}

export const GridView: React.FC = () => {
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [streams, setStreams] = useState<Map<number, CameraStream>>(new Map());
  const [loading, setLoading] = useState(true);
  const [layout, setLayout] = useState<Array<any>>([]);

  useEffect(() => {
    loadCameras();
  }, []);

  const loadCameras = async () => {
    try {
      const data = await apiClient.getCameras();
      setCameras(data);

      // Initialize streams map
      const streamsMap = new Map<number, CameraStream>();
      data.forEach(camera => {
        streamsMap.set(camera.id, {
          cameraId: camera.id,
          streamUrl: null,
          isStreaming: false
        });
      });
      setStreams(streamsMap);

      // Generate layout
      const gridLayout = data.map((camera, index) => ({
        i: camera.id.toString(),
        x: (index % 2) * 6,
        y: Math.floor(index / 2) * 4,
        w: 6,
        h: 4,
        minW: 3,
        minH: 3
      }));
      setLayout(gridLayout);

      // Auto-start all streams
      data.forEach(camera => startStream(camera.id));
    } catch (error) {
      toast.error('Failed to load cameras');
    } finally {
      setLoading(false);
    }
  };

  const startStream = async (cameraId: number) => {
    try {
      const response = await apiClient.startStream(cameraId);
      setStreams(prev => {
        const newStreams = new Map(prev);
        newStreams.set(cameraId, {
          cameraId,
          streamUrl: response.playlist_url,
          isStreaming: true
        });
        return newStreams;
      });
    } catch (error) {
      console.error(`Failed to start stream for camera ${cameraId}`, error);
    }
  };

  const _stopStream = async (cameraId: number) => {
    try {
      await apiClient.stopStream(cameraId);
      setStreams(prev => {
        const newStreams = new Map(prev);
        newStreams.set(cameraId, {
          cameraId,
          streamUrl: null,
          isStreaming: false
        });
        return newStreams;
      });
    } catch (error) {
      console.error(`Failed to stop stream for camera ${cameraId}`, error);
    }
  };

  const onLayoutChange = (newLayout: Array<any>) => {
    setLayout(newLayout);
    // Save layout to localStorage
    localStorage.setItem('cameraGridLayout', JSON.stringify(newLayout));
  };

  const getStatusColor = (status: CameraStatus) => {
    switch (status) {
      case CameraStatus.ONLINE:
        return 'bg-green-500';
      case CameraStatus.RECORDING:
        return 'bg-red-500';
      case CameraStatus.OFFLINE:
        return 'bg-gray-500';
      case CameraStatus.ERROR:
        return 'bg-yellow-500';
      default:
        return 'bg-gray-500';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-white">Loading cameras...</div>
      </div>
    );
  }

  if (cameras.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400 mb-4">No cameras available for grid view</p>
        <Link
          to="/cameras/new"
          className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          Add Camera
        </Link>
      </div>
    );
  }

  return (
    <div className="grid-view-container p-4">
      <div className="mb-4 flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white">Grid View ({cameras.length} cameras)</h2>
        <div className="text-sm text-gray-400">
          Drag to rearrange • Resize by dragging corners
        </div>
      </div>

      <GridLayout
        className="layout"
        layout={layout}
        cols={12}
        rowHeight={80}
        width={1200}
        onLayoutChange={onLayoutChange}
        draggableHandle=".drag-handle"
        compactType={null}
        preventCollision={false}
      >
        {cameras.map((camera) => {
          const stream = streams.get(camera.id);
          return (
            <div key={camera.id.toString()} className="grid-item bg-gray-800 rounded-lg overflow-hidden">
              {/* Header */}
              <div className="drag-handle bg-gray-700 px-3 py-2 flex justify-between items-center cursor-move">
                <div className="flex items-center gap-2">
                  <div className={`w-2 h-2 rounded-full ${getStatusColor(camera.status)}`}></div>
                  <span className="text-white font-medium text-sm truncate">{camera.name}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Link
                    to={`/cameras/${camera.id}`}
                    className="text-gray-400 hover:text-white p-1"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <FiMaximize2 size={14} />
                  </Link>
                  <Link
                    to={`/cameras/${camera.id}/edit`}
                    className="text-gray-400 hover:text-white p-1"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <FiSettings size={14} />
                  </Link>
                </div>
              </div>

              {/* Video */}
              <div className="video-container bg-gray-900">
                {stream?.isStreaming && stream.streamUrl ? (
                  <VideoPlayer src={stream.streamUrl} autoPlay controls={false} />
                ) : (
                  <div className="flex items-center justify-center h-full text-gray-500 text-sm">
                    Starting stream...
                  </div>
                )}
              </div>

              {/* Info */}
              <div className="px-3 py-2 bg-gray-700 text-xs text-gray-400 flex justify-between">
                <span>{camera.resolution}</span>
                <span>{camera.fps} FPS</span>
              </div>
            </div>
          );
        })}
      </GridLayout>
    </div>
  );
};
