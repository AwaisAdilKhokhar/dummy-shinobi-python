import React, { useState, useEffect } from 'react';
import { apiClient } from '@/services/api';
import toast from 'react-hot-toast';
import {
  FiChevronUp,
  FiChevronDown,
  FiChevronLeft,
  FiChevronRight,
  FiZoomIn,
  FiZoomOut,
  FiHome,
  FiSave,
  FiTrash2,
} from 'react-icons/fi';

interface PTZControlsProps {
  cameraId: number;
  isOnvif: boolean;
}

interface Preset {
  token: string;
  name: string;
  pan: number | null;
  tilt: number | null;
  zoom: number | null;
}

export const PTZControls: React.FC<PTZControlsProps> = ({ cameraId, isOnvif }) => {
  const [presets, setPresets] = useState<Preset[]>([]);
  const [newPresetName, setNewPresetName] = useState('');
  const [showPresetInput, setShowPresetInput] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOnvif) {
      loadPresets();
    }
  }, [cameraId, isOnvif]);

  const loadPresets = async () => {
    try {
      const data = await apiClient.getPtzPresets(cameraId);
      setPresets(data);
    } catch (error) {
      console.error('Failed to load presets', error);
    }
  };

  const handleMove = async (pan: number, tilt: number, zoom: number = 0) => {
    try {
      await apiClient.ptzContinuousMove(cameraId, pan, tilt, zoom, 1);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'PTZ movement failed');
    }
  };

  const handleStop = async () => {
    try {
      await apiClient.ptzStop(cameraId);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'PTZ stop failed');
    }
  };

  const handleZoom = async (direction: number) => {
    try {
      await apiClient.ptzContinuousMove(cameraId, 0, 0, direction, 1);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Zoom failed');
    }
  };

  const handleHome = async () => {
    try {
      await apiClient.ptzGotoHome(cameraId);
      toast.success('Moving to home position');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Go to home failed');
    }
  };

  const handleSetHome = async () => {
    try {
      await apiClient.ptzSetHome(cameraId);
      toast.success('Home position set');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Set home failed');
    }
  };

  const handleGotoPreset = async (presetToken: string) => {
    try {
      await apiClient.ptzGotoPreset(cameraId, presetToken);
      toast.success('Moving to preset');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Go to preset failed');
    }
  };

  const handleSavePreset = async () => {
    if (!newPresetName.trim()) {
      toast.error('Please enter a preset name');
      return;
    }

    setLoading(true);
    try {
      await apiClient.ptzSetPreset(cameraId, newPresetName);
      toast.success('Preset saved');
      setNewPresetName('');
      setShowPresetInput(false);
      loadPresets();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Save preset failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDeletePreset = async (presetToken: string) => {
    if (!window.confirm('Are you sure you want to delete this preset?')) return;

    try {
      await apiClient.ptzRemovePreset(cameraId, presetToken);
      toast.success('Preset deleted');
      loadPresets();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Delete preset failed');
    }
  };

  if (!isOnvif) {
    return (
      <div className="bg-gray-800 rounded-lg p-4">
        <p className="text-gray-400 text-sm text-center">
          PTZ controls are only available for ONVIF cameras
        </p>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-white mb-4">PTZ Controls</h3>

      <div className="grid grid-cols-2 gap-6">
        {/* Pan/Tilt Controls */}
        <div>
          <h4 className="text-sm font-medium text-gray-300 mb-3">Pan/Tilt</h4>
          <div className="flex flex-col items-center gap-2">
            {/* Up */}
            <button
              onMouseDown={() => handleMove(0, 1)}
              onMouseUp={handleStop}
              onMouseLeave={handleStop}
              className="p-3 bg-gray-700 hover:bg-gray-600 rounded-lg text-white"
            >
              <FiChevronUp size={24} />
            </button>

            {/* Left/Center/Right */}
            <div className="flex gap-2">
              <button
                onMouseDown={() => handleMove(-1, 0)}
                onMouseUp={handleStop}
                onMouseLeave={handleStop}
                className="p-3 bg-gray-700 hover:bg-gray-600 rounded-lg text-white"
              >
                <FiChevronLeft size={24} />
              </button>

              <button
                onClick={handleStop}
                className="p-3 bg-red-600 hover:bg-red-700 rounded-lg text-white font-bold"
              >
                STOP
              </button>

              <button
                onMouseDown={() => handleMove(1, 0)}
                onMouseUp={handleStop}
                onMouseLeave={handleStop}
                className="p-3 bg-gray-700 hover:bg-gray-600 rounded-lg text-white"
              >
                <FiChevronRight size={24} />
              </button>
            </div>

            {/* Down */}
            <button
              onMouseDown={() => handleMove(0, -1)}
              onMouseUp={handleStop}
              onMouseLeave={handleStop}
              className="p-3 bg-gray-700 hover:bg-gray-600 rounded-lg text-white"
            >
              <FiChevronDown size={24} />
            </button>
          </div>
        </div>

        {/* Zoom Controls */}
        <div>
          <h4 className="text-sm font-medium text-gray-300 mb-3">Zoom</h4>
          <div className="flex flex-col gap-2">
            <button
              onMouseDown={() => handleZoom(0.5)}
              onMouseUp={handleStop}
              onMouseLeave={handleStop}
              className="flex items-center justify-center gap-2 p-3 bg-gray-700 hover:bg-gray-600 rounded-lg text-white"
            >
              <FiZoomIn size={20} /> Zoom In
            </button>

            <button
              onMouseDown={() => handleZoom(-0.5)}
              onMouseUp={handleStop}
              onMouseLeave={handleStop}
              className="flex items-center justify-center gap-2 p-3 bg-gray-700 hover:bg-gray-600 rounded-lg text-white"
            >
              <FiZoomOut size={20} /> Zoom Out
            </button>

            <button
              onClick={handleHome}
              className="flex items-center justify-center gap-2 p-3 bg-blue-600 hover:bg-blue-700 rounded-lg text-white"
            >
              <FiHome size={20} /> Home
            </button>

            <button
              onClick={handleSetHome}
              className="flex items-center justify-center gap-2 p-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-white text-sm"
            >
              Set Home
            </button>
          </div>
        </div>
      </div>

      {/* Presets */}
      <div className="mt-6">
        <div className="flex justify-between items-center mb-3">
          <h4 className="text-sm font-medium text-gray-300">Presets</h4>
          <button
            onClick={() => setShowPresetInput(!showPresetInput)}
            className="text-sm text-blue-500 hover:text-blue-400"
          >
            {showPresetInput ? 'Cancel' : '+ Add Preset'}
          </button>
        </div>

        {showPresetInput && (
          <div className="flex gap-2 mb-3">
            <input
              type="text"
              value={newPresetName}
              onChange={(e) => setNewPresetName(e.target.value)}
              placeholder="Preset name"
              className="flex-1 px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleSavePreset}
              disabled={loading}
              className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md text-sm disabled:opacity-50 flex items-center gap-2"
            >
              <FiSave size={16} /> Save
            </button>
          </div>
        )}

        <div className="space-y-2">
          {presets.length === 0 ? (
            <p className="text-gray-500 text-sm text-center py-4">No presets saved</p>
          ) : (
            presets.map((preset) => (
              <div
                key={preset.token}
                className="flex items-center justify-between p-2 bg-gray-700 rounded-lg"
              >
                <button
                  onClick={() => handleGotoPreset(preset.token)}
                  className="flex-1 text-left text-white hover:text-blue-400 text-sm"
                >
                  {preset.name}
                </button>
                <button
                  onClick={() => handleDeletePreset(preset.token)}
                  className="p-2 text-red-500 hover:text-red-400"
                >
                  <FiTrash2 size={16} />
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
