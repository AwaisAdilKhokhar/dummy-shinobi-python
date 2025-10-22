from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from app.database import get_db
from app.services.camera_service import CameraService
from app.services.ptz_service import PTZService
from app.api.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/ptz", tags=["PTZ"])


class PTZMoveRequest(BaseModel):
    pan: float
    tilt: float
    zoom: float


class ContinuousMoveRequest(PTZMoveRequest):
    timeout: int = 1


class PresetRequest(BaseModel):
    name: str


class PresetGotoRequest(BaseModel):
    preset_token: str


@router.post("/{camera_id}/continuous-move")
def continuous_move(
    camera_id: int,
    move_request: ContinuousMoveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Perform continuous PTZ movement."""
    camera = CameraService.get_camera(db, camera_id, current_user)

    if camera.protocol != "onvif":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Camera must be ONVIF protocol for PTZ control"
        )

    # Extract host and port from stream URL
    try:
        # Parse stream URL (e.g., rtsp://192.168.1.100:554/stream)
        url_parts = camera.stream_url.split("://")[1].split("/")[0]
        host_port = url_parts.split(":")
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 80
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid camera stream URL"
        )

    onvif_camera = PTZService.create_onvif_camera(
        host, port, camera.username or "", camera.password or ""
    )

    if not onvif_camera:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect to ONVIF camera"
        )

    success = PTZService.continuous_move(
        onvif_camera,
        move_request.pan,
        move_request.tilt,
        move_request.zoom,
        move_request.timeout
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PTZ movement failed"
        )

    return {"message": "PTZ movement executed successfully"}


@router.post("/{camera_id}/absolute-move")
def absolute_move(
    camera_id: int,
    move_request: PTZMoveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Perform absolute PTZ movement."""
    camera = CameraService.get_camera(db, camera_id, current_user)

    if camera.protocol != "onvif":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Camera must be ONVIF protocol for PTZ control"
        )

    try:
        url_parts = camera.stream_url.split("://")[1].split("/")[0]
        host_port = url_parts.split(":")
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 80
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid camera stream URL"
        )

    onvif_camera = PTZService.create_onvif_camera(
        host, port, camera.username or "", camera.password or ""
    )

    if not onvif_camera:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect to ONVIF camera"
        )

    success = PTZService.absolute_move(
        onvif_camera,
        move_request.pan,
        move_request.tilt,
        move_request.zoom
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PTZ movement failed"
        )

    return {"message": "PTZ movement executed successfully"}


@router.post("/{camera_id}/relative-move")
def relative_move(
    camera_id: int,
    move_request: PTZMoveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Perform relative PTZ movement."""
    camera = CameraService.get_camera(db, camera_id, current_user)

    if camera.protocol != "onvif":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Camera must be ONVIF protocol for PTZ control"
        )

    try:
        url_parts = camera.stream_url.split("://")[1].split("/")[0]
        host_port = url_parts.split(":")
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 80
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid camera stream URL"
        )

    onvif_camera = PTZService.create_onvif_camera(
        host, port, camera.username or "", camera.password or ""
    )

    if not onvif_camera:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect to ONVIF camera"
        )

    success = PTZService.relative_move(
        onvif_camera,
        move_request.pan,
        move_request.tilt,
        move_request.zoom
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PTZ movement failed"
        )

    return {"message": "PTZ movement executed successfully"}


@router.post("/{camera_id}/stop")
def stop_ptz(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Stop PTZ movement."""
    camera = CameraService.get_camera(db, camera_id, current_user)

    if camera.protocol != "onvif":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Camera must be ONVIF protocol for PTZ control"
        )

    try:
        url_parts = camera.stream_url.split("://")[1].split("/")[0]
        host_port = url_parts.split(":")
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 80
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid camera stream URL"
        )

    onvif_camera = PTZService.create_onvif_camera(
        host, port, camera.username or "", camera.password or ""
    )

    if not onvif_camera:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect to ONVIF camera"
        )

    success = PTZService.stop(onvif_camera)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PTZ stop failed"
        )

    return {"message": "PTZ stopped successfully"}


@router.get("/{camera_id}/presets")
def get_presets(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get PTZ presets."""
    camera = CameraService.get_camera(db, camera_id, current_user)

    if camera.protocol != "onvif":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Camera must be ONVIF protocol for PTZ control"
        )

    try:
        url_parts = camera.stream_url.split("://")[1].split("/")[0]
        host_port = url_parts.split(":")
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 80
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid camera stream URL"
        )

    onvif_camera = PTZService.create_onvif_camera(
        host, port, camera.username or "", camera.password or ""
    )

    if not onvif_camera:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect to ONVIF camera"
        )

    presets = PTZService.get_presets(onvif_camera)
    return {"presets": presets}


@router.post("/{camera_id}/goto-preset")
def goto_preset(
    camera_id: int,
    preset_request: PresetGotoRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Go to PTZ preset."""
    camera = CameraService.get_camera(db, camera_id, current_user)

    if camera.protocol != "onvif":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Camera must be ONVIF protocol for PTZ control"
        )

    try:
        url_parts = camera.stream_url.split("://")[1].split("/")[0]
        host_port = url_parts.split(":")
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 80
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid camera stream URL"
        )

    onvif_camera = PTZService.create_onvif_camera(
        host, port, camera.username or "", camera.password or ""
    )

    if not onvif_camera:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect to ONVIF camera"
        )

    success = PTZService.goto_preset(onvif_camera, preset_request.preset_token)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Go to preset failed"
        )

    return {"message": "Moved to preset successfully"}


@router.post("/{camera_id}/set-preset")
def set_preset(
    camera_id: int,
    preset_request: PresetRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Set PTZ preset at current position."""
    camera = CameraService.get_camera(db, camera_id, current_user)

    if camera.protocol != "onvif":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Camera must be ONVIF protocol for PTZ control"
        )

    try:
        url_parts = camera.stream_url.split("://")[1].split("/")[0]
        host_port = url_parts.split(":")
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 80
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid camera stream URL"
        )

    onvif_camera = PTZService.create_onvif_camera(
        host, port, camera.username or "", camera.password or ""
    )

    if not onvif_camera:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect to ONVIF camera"
        )

    preset_token = PTZService.set_preset(onvif_camera, preset_request.name)

    if not preset_token:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Set preset failed"
        )

    return {"message": "Preset set successfully", "preset_token": preset_token}


@router.delete("/{camera_id}/presets/{preset_token}")
def remove_preset(
    camera_id: int,
    preset_token: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove PTZ preset."""
    camera = CameraService.get_camera(db, camera_id, current_user)

    if camera.protocol != "onvif":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Camera must be ONVIF protocol for PTZ control"
        )

    try:
        url_parts = camera.stream_url.split("://")[1].split("/")[0]
        host_port = url_parts.split(":")
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 80
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid camera stream URL"
        )

    onvif_camera = PTZService.create_onvif_camera(
        host, port, camera.username or "", camera.password or ""
    )

    if not onvif_camera:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect to ONVIF camera"
        )

    success = PTZService.remove_preset(onvif_camera, preset_token)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Remove preset failed"
        )

    return {"message": "Preset removed successfully"}


@router.post("/{camera_id}/home")
def goto_home(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Go to home position."""
    camera = CameraService.get_camera(db, camera_id, current_user)

    if camera.protocol != "onvif":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Camera must be ONVIF protocol for PTZ control"
        )

    try:
        url_parts = camera.stream_url.split("://")[1].split("/")[0]
        host_port = url_parts.split(":")
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 80
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid camera stream URL"
        )

    onvif_camera = PTZService.create_onvif_camera(
        host, port, camera.username or "", camera.password or ""
    )

    if not onvif_camera:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect to ONVIF camera"
        )

    success = PTZService.goto_home_position(onvif_camera)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Go to home position failed"
        )

    return {"message": "Moved to home position successfully"}


@router.post("/{camera_id}/set-home")
def set_home(
    camera_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Set current position as home position."""
    camera = CameraService.get_camera(db, camera_id, current_user)

    if camera.protocol != "onvif":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Camera must be ONVIF protocol for PTZ control"
        )

    try:
        url_parts = camera.stream_url.split("://")[1].split("/")[0]
        host_port = url_parts.split(":")
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 80
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid camera stream URL"
        )

    onvif_camera = PTZService.create_onvif_camera(
        host, port, camera.username or "", camera.password or ""
    )

    if not onvif_camera:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to connect to ONVIF camera"
        )

    success = PTZService.set_home_position(onvif_camera)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Set home position failed"
        )

    return {"message": "Home position set successfully"}
