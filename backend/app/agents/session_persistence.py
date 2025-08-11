"""
Session Persistence Module

Provides session backup and recovery for server restarts.
Stores session data in a JSON file for persistence across restarts.
"""

import json
import os
from typing import Dict, Any
from datetime import datetime
import threading

PERSISTENCE_FILE = "session_backup.json"
_persistence_lock = threading.Lock()

def save_sessions_to_disk(active_sessions: Dict[str, Any], session_metrics: Dict[str, Any]):
    """Save current sessions and metrics to disk"""
    try:
        with _persistence_lock:
            backup_data = {
                "timestamp": datetime.now().isoformat(),
                "active_sessions": active_sessions,
                "session_metrics": {
                    key: value for key, value in session_metrics.items()
                    if key != "response_times"  # Don't persist response times array
                },
                "version": "1.0"
            }
            
            # Convert defaultdict to regular dict for JSON serialization
            if "error_counts" in backup_data["session_metrics"]:
                backup_data["session_metrics"]["error_counts"] = dict(backup_data["session_metrics"]["error_counts"])
            
            with open(PERSISTENCE_FILE, 'w') as f:
                json.dump(backup_data, f, indent=2)
                
            print(f"[SessionPersistence] Saved {len(active_sessions)} sessions to disk")
            
    except Exception as e:
        print(f"[SessionPersistence] Error saving sessions: {e}")

def load_sessions_from_disk() -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Load sessions and metrics from disk"""
    try:
        if not os.path.exists(PERSISTENCE_FILE):
            print("[SessionPersistence] No backup file found, starting fresh")
            return {}, {}
            
        with _persistence_lock:
            with open(PERSISTENCE_FILE, 'r') as f:
                backup_data = json.load(f)
            
            active_sessions = backup_data.get("active_sessions", {})
            session_metrics = backup_data.get("session_metrics", {})
            
            # Clean up old sessions (older than 10 minutes)
            current_time = datetime.now().timestamp()
            cleaned_sessions = {}
            
            for session_key, session_data in active_sessions.items():
                if "last_activity" in session_data:
                    # Check if session is still recent
                    if current_time - session_data["last_activity"] < 600:  # 10 minutes
                        cleaned_sessions[session_key] = session_data
                    else:
                        print(f"[SessionPersistence] Discarding stale session: {session_key}")
            
            print(f"[SessionPersistence] Loaded {len(cleaned_sessions)} valid sessions from {len(active_sessions)} total")
            return cleaned_sessions, session_metrics
            
    except Exception as e:
        print(f"[SessionPersistence] Error loading sessions: {e}")
        return {}, {}

def cleanup_persistence_file():
    """Remove the persistence file"""
    try:
        if os.path.exists(PERSISTENCE_FILE):
            os.remove(PERSISTENCE_FILE)
            print("[SessionPersistence] Cleaned up persistence file")
    except Exception as e:
        print(f"[SessionPersistence] Error cleaning up persistence file: {e}")

def get_persistence_status() -> Dict[str, Any]:
    """Get status of session persistence"""
    try:
        if os.path.exists(PERSISTENCE_FILE):
            stat = os.stat(PERSISTENCE_FILE)
            return {
                "persistence_enabled": True,
                "backup_file_exists": True,
                "backup_file_size": stat.st_size,
                "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
        else:
            return {
                "persistence_enabled": True,
                "backup_file_exists": False
            }
    except Exception as e:
        return {
            "persistence_enabled": False,
            "error": str(e)
        }