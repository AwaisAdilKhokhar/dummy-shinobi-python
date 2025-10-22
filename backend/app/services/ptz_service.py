from onvif import ONVIFCamera
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class PTZService:
    """Service for controlling PTZ cameras via ONVIF."""

    @staticmethod
    def create_onvif_camera(host: str, port: int, username: str, password: str) -> Optional[ONVIFCamera]:
        """Create ONVIF camera connection."""
        try:
            # Extract host from URL if needed
            if "://" in host:
                host = host.split("://")[1].split(":")[0].split("/")[0]

            camera = ONVIFCamera(host, port, username, password)
            return camera
        except Exception as e:
            logger.error(f"Failed to create ONVIF camera: {e}")
            return None

    @staticmethod
    def get_ptz_service(camera: ONVIFCamera):
        """Get PTZ service from camera."""
        try:
            return camera.create_ptz_service()
        except Exception as e:
            logger.error(f"Failed to get PTZ service: {e}")
            return None

    @staticmethod
    def get_media_service(camera: ONVIFCamera):
        """Get media service from camera."""
        try:
            return camera.create_media_service()
        except Exception as e:
            logger.error(f"Failed to get media service: {e}")
            return None

    @staticmethod
    def get_ptz_configuration(camera: ONVIFCamera) -> Optional[Dict]:
        """Get PTZ configuration."""
        try:
            media_service = PTZService.get_media_service(camera)
            if not media_service:
                return None

            profiles = media_service.GetProfiles()
            if not profiles:
                return None

            # Get first profile with PTZ configuration
            for profile in profiles:
                if profile.PTZConfiguration:
                    return {
                        'profile_token': profile.token,
                        'ptz_configuration': profile.PTZConfiguration,
                        'name': profile.Name
                    }
            return None
        except Exception as e:
            logger.error(f"Failed to get PTZ configuration: {e}")
            return None

    @staticmethod
    def continuous_move(camera: ONVIFCamera, pan: float, tilt: float, zoom: float,
                       timeout: int = 1) -> bool:
        """
        Perform continuous PTZ move.

        Args:
            camera: ONVIF camera instance
            pan: Pan velocity (-1.0 to 1.0)
            tilt: Tilt velocity (-1.0 to 1.0)
            zoom: Zoom velocity (-1.0 to 1.0)
            timeout: Movement duration in seconds

        Returns:
            Success status
        """
        try:
            ptz_service = PTZService.get_ptz_service(camera)
            if not ptz_service:
                return False

            config = PTZService.get_ptz_configuration(camera)
            if not config:
                return False

            request = ptz_service.create_type('ContinuousMove')
            request.ProfileToken = config['profile_token']

            # Set velocity
            request.Velocity = {
                'PanTilt': {'x': pan, 'y': tilt},
                'Zoom': {'x': zoom}
            }

            # Set timeout
            if timeout:
                request.Timeout = f"PT{timeout}S"

            ptz_service.ContinuousMove(request)
            return True
        except Exception as e:
            logger.error(f"Continuous move failed: {e}")
            return False

    @staticmethod
    def absolute_move(camera: ONVIFCamera, pan: float, tilt: float, zoom: float) -> bool:
        """
        Perform absolute PTZ move.

        Args:
            camera: ONVIF camera instance
            pan: Pan position (-1.0 to 1.0)
            tilt: Tilt position (-1.0 to 1.0)
            zoom: Zoom position (0.0 to 1.0)

        Returns:
            Success status
        """
        try:
            ptz_service = PTZService.get_ptz_service(camera)
            if not ptz_service:
                return False

            config = PTZService.get_ptz_configuration(camera)
            if not config:
                return False

            request = ptz_service.create_type('AbsoluteMove')
            request.ProfileToken = config['profile_token']

            # Set position
            request.Position = {
                'PanTilt': {'x': pan, 'y': tilt},
                'Zoom': {'x': zoom}
            }

            ptz_service.AbsoluteMove(request)
            return True
        except Exception as e:
            logger.error(f"Absolute move failed: {e}")
            return False

    @staticmethod
    def relative_move(camera: ONVIFCamera, pan: float, tilt: float, zoom: float) -> bool:
        """
        Perform relative PTZ move.

        Args:
            camera: ONVIF camera instance
            pan: Pan translation (-1.0 to 1.0)
            tilt: Tilt translation (-1.0 to 1.0)
            zoom: Zoom translation (-1.0 to 1.0)

        Returns:
            Success status
        """
        try:
            ptz_service = PTZService.get_ptz_service(camera)
            if not ptz_service:
                return False

            config = PTZService.get_ptz_configuration(camera)
            if not config:
                return False

            request = ptz_service.create_type('RelativeMove')
            request.ProfileToken = config['profile_token']

            # Set translation
            request.Translation = {
                'PanTilt': {'x': pan, 'y': tilt},
                'Zoom': {'x': zoom}
            }

            ptz_service.RelativeMove(request)
            return True
        except Exception as e:
            logger.error(f"Relative move failed: {e}")
            return False

    @staticmethod
    def stop(camera: ONVIFCamera) -> bool:
        """
        Stop PTZ movement.

        Args:
            camera: ONVIF camera instance

        Returns:
            Success status
        """
        try:
            ptz_service = PTZService.get_ptz_service(camera)
            if not ptz_service:
                return False

            config = PTZService.get_ptz_configuration(camera)
            if not config:
                return False

            request = ptz_service.create_type('Stop')
            request.ProfileToken = config['profile_token']
            request.PanTilt = True
            request.Zoom = True

            ptz_service.Stop(request)
            return True
        except Exception as e:
            logger.error(f"Stop failed: {e}")
            return False

    @staticmethod
    def get_presets(camera: ONVIFCamera) -> List[Dict]:
        """
        Get PTZ presets.

        Args:
            camera: ONVIF camera instance

        Returns:
            List of presets
        """
        try:
            ptz_service = PTZService.get_ptz_service(camera)
            if not ptz_service:
                return []

            config = PTZService.get_ptz_configuration(camera)
            if not config:
                return []

            request = ptz_service.create_type('GetPresets')
            request.ProfileToken = config['profile_token']

            presets = ptz_service.GetPresets(request)

            return [
                {
                    'token': preset.token,
                    'name': preset.Name,
                    'pan': preset.PTZPosition.PanTilt.x if preset.PTZPosition else None,
                    'tilt': preset.PTZPosition.PanTilt.y if preset.PTZPosition else None,
                    'zoom': preset.PTZPosition.Zoom.x if preset.PTZPosition else None,
                }
                for preset in presets
            ]
        except Exception as e:
            logger.error(f"Get presets failed: {e}")
            return []

    @staticmethod
    def goto_preset(camera: ONVIFCamera, preset_token: str) -> bool:
        """
        Go to PTZ preset.

        Args:
            camera: ONVIF camera instance
            preset_token: Preset token

        Returns:
            Success status
        """
        try:
            ptz_service = PTZService.get_ptz_service(camera)
            if not ptz_service:
                return False

            config = PTZService.get_ptz_configuration(camera)
            if not config:
                return False

            request = ptz_service.create_type('GotoPreset')
            request.ProfileToken = config['profile_token']
            request.PresetToken = preset_token

            ptz_service.GotoPreset(request)
            return True
        except Exception as e:
            logger.error(f"Goto preset failed: {e}")
            return False

    @staticmethod
    def set_preset(camera: ONVIFCamera, preset_name: str) -> Optional[str]:
        """
        Set PTZ preset at current position.

        Args:
            camera: ONVIF camera instance
            preset_name: Name for the preset

        Returns:
            Preset token if successful, None otherwise
        """
        try:
            ptz_service = PTZService.get_ptz_service(camera)
            if not ptz_service:
                return None

            config = PTZService.get_ptz_configuration(camera)
            if not config:
                return None

            request = ptz_service.create_type('SetPreset')
            request.ProfileToken = config['profile_token']
            request.PresetName = preset_name

            response = ptz_service.SetPreset(request)
            return response.PresetToken if response else None
        except Exception as e:
            logger.error(f"Set preset failed: {e}")
            return None

    @staticmethod
    def remove_preset(camera: ONVIFCamera, preset_token: str) -> bool:
        """
        Remove PTZ preset.

        Args:
            camera: ONVIF camera instance
            preset_token: Preset token to remove

        Returns:
            Success status
        """
        try:
            ptz_service = PTZService.get_ptz_service(camera)
            if not ptz_service:
                return False

            config = PTZService.get_ptz_configuration(camera)
            if not config:
                return False

            request = ptz_service.create_type('RemovePreset')
            request.ProfileToken = config['profile_token']
            request.PresetToken = preset_token

            ptz_service.RemovePreset(request)
            return True
        except Exception as e:
            logger.error(f"Remove preset failed: {e}")
            return False

    @staticmethod
    def goto_home_position(camera: ONVIFCamera) -> bool:
        """
        Go to home position.

        Args:
            camera: ONVIF camera instance

        Returns:
            Success status
        """
        try:
            ptz_service = PTZService.get_ptz_service(camera)
            if not ptz_service:
                return False

            config = PTZService.get_ptz_configuration(camera)
            if not config:
                return False

            request = ptz_service.create_type('GotoHomePosition')
            request.ProfileToken = config['profile_token']

            ptz_service.GotoHomePosition(request)
            return True
        except Exception as e:
            logger.error(f"Goto home position failed: {e}")
            return False

    @staticmethod
    def set_home_position(camera: ONVIFCamera) -> bool:
        """
        Set current position as home position.

        Args:
            camera: ONVIF camera instance

        Returns:
            Success status
        """
        try:
            ptz_service = PTZService.get_ptz_service(camera)
            if not ptz_service:
                return False

            config = PTZService.get_ptz_configuration(camera)
            if not config:
                return False

            request = ptz_service.create_type('SetHomePosition')
            request.ProfileToken = config['profile_token']

            ptz_service.SetHomePosition(request)
            return True
        except Exception as e:
            logger.error(f"Set home position failed: {e}")
            return False
