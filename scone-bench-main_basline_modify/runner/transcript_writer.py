# Copyright 2026 Anthropic PBC
# SPDX-License-Identifier: Apache-2.0
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class TranscriptWriter:
    """Handles writing transcripts to files in real-time as SSE events stream."""

    def __init__(self, file_path: str, problem_id: str, container_id: str):
        self.file_path = Path(file_path)
        self.problem_id = problem_id
        self.container_id = container_id
        self.events: list[dict[str, Any]] = []
        self.messages: list[dict[str, Any]] = []
        self.start_time = datetime.now(timezone.utc).isoformat()

        # Create directory if it doesn't exist
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize transcript file with metadata
        self._initialize_file()

    def _initialize_file(self):
        """Initialize the transcript file with metadata."""
        metadata = {
            "problem_id": self.problem_id,
            "container_id": self.container_id,
            "start_time": self.start_time,
            "status": "in_progress",
            "events": [],
            "messages": [],
        }

        with open(self.file_path, "w") as f:
            json.dump(metadata, f, indent=2)

    def write_event(self, event_data: str):
        """
        Write an SSE event to the transcript.

        Args:
            event_data: The SSE event string (e.g., "data: {...}\n\n")
        """
        if not event_data.startswith("data: "):
            return

        try:
            # Extract JSON from SSE format
            json_str = event_data[6:].strip()  # Remove "data: " prefix
            if not json_str:
                return

            event = json.loads(json_str)
            event_type = event.get("type")

            # Skip text streaming chunks and tool param chunks
            if event_type in ["text", "tool_use_param"]:
                return

            # Only save important events
            save_event = event_type in [
                "start",
                "message",
                "grade",
                "error",
                "done",
                "tool_executing",
                "tool_use_start",
            ]

            if save_event:
                self.events.append({"timestamp": datetime.now(timezone.utc).isoformat(), "event": event})

            # Track messages separately for easier access
            if event_type == "message":
                self.messages.append(event["message"])

            # Update file with new event only if we saved it
            if save_event:
                self._update_file(event)

        except json.JSONDecodeError as e:
            print(f"Error parsing SSE event: {e}")

    def _calculate_score(self, grade: dict) -> float:
        """Calculate final score from subscores and weights."""
        if not grade or "subscores" not in grade or "weights" not in grade:
            return 0.0
        subscores = grade["subscores"]
        weights = grade["weights"]
        return sum(subscores[key] * weights[key] for key in subscores.keys())

    def _update_file(self, event: dict[str, Any]):
        """Update the transcript file with a new event."""
        try:
            # Read current file content
            with open(self.file_path) as f:
                data = json.load(f)

            # Sync with our in-memory data
            data["events"] = self.events
            data["messages"] = self.messages

            # Update based on event type
            if event.get("type") == "done":
                data["end_time"] = datetime.now(timezone.utc).isoformat()
                # Don't set status here - wait for grade or error
            elif event.get("type") == "error":
                data["error"] = event.get("content", "Unknown error")
                data["end_time"] = datetime.now(timezone.utc).isoformat()
                # Only set error status if we don't have a grade
                if "grade" not in data:
                    data["status"] = "error"
            elif event.get("type") == "grade":
                grade = event.get("grade")
                data["grade"] = grade
                data["status"] = "done"

            # Write updated content
            with open(self.file_path, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Error updating transcript file: {e}")

    def finalize(self, grade: Optional[Dict[str, Any]] = None):
        """Finalize the transcript with completion status and optional grade."""
        try:
            with open(self.file_path) as f:
                data = json.load(f)

            data["end_time"] = datetime.now(UTC).isoformat()

            if grade:
                data["grade"] = grade
                data["status"] = "done"
            elif "status" not in data or data["status"] == "in_progress":
                # No grade and still in progress means it failed/timed out
                data["status"] = "failed"

            with open(self.file_path, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            print(f"Error finalizing transcript: {e}")
