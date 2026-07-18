"""Flask GUI for Smart Music Tagger.

A self-contained web layer over the shared :class:`~core.service.TaggerService`.
It does not import or modify the CLI; it reuses the same core modules the CLI
uses, wiring form-provided configuration into the service and streaming
progress to the browser via Server-Sent Events.
"""

from .app import create_app
from .progress import Job, JobStore
from .runner import JobManager

__all__ = ["create_app", "Job", "JobStore", "JobManager"]
