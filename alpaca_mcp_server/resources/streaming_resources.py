"""Streaming resources implementation."""

from datetime import datetime
from ..config.settings import settings


async def get_stream_status() -> dict:
    """Real-time streaming status and buffer statistics."""
    try:
        # Access global streaming state
        stream_manager = settings.get_stream_manager()

        if not stream_manager or not hasattr(stream_manager, "is_streaming"):
            return {
                "status": "inactive",
                "streams_active": 0,
                "buffer_stats": {},
                "last_updated": datetime.now().isoformat(),
            }

        # Get buffer statistics
        buffer_stats = {}
        total_messages = 0

        for symbol, buffers in stream_manager.buffers.items():
            symbol_stats = {}
            symbol_total = 0

            for data_type, buffer in buffers.items():
                buffer_size = len(buffer)
                symbol_stats[data_type] = {
                    "buffer_size": buffer_size,
                    "last_update": buffer[-1].get("timestamp") if buffer else None,
                }
                symbol_total += buffer_size

            buffer_stats[symbol] = {
                "data_types": symbol_stats,
                "total_messages": symbol_total,
            }
            total_messages += symbol_total

        return {
            "status": "active" if stream_manager.is_streaming else "inactive",
            "streams_active": (
                len(stream_manager.subscribed_symbols)
                if hasattr(stream_manager, "subscribed_symbols")
                else 0
            ),
            "subscribed_symbols": (
                list(stream_manager.subscribed_symbols)
                if hasattr(stream_manager, "subscribed_symbols")
                else []
            ),
            "total_messages_buffered": total_messages,
            "buffer_stats": buffer_stats,
            "stream_duration_seconds": (
                stream_manager.duration_seconds
                if hasattr(stream_manager, "duration_seconds")
                else None
            ),
            "feed_type": (
                stream_manager.feed if hasattr(stream_manager, "feed") else "unknown"
            ),
            "last_updated": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error",
            "streams_active": 0,
            "last_updated": datetime.now().isoformat(),
        }


async def get_stream_performance() -> dict:
    """Streaming performance metrics and health indicators."""
    try:
        stream_manager = settings.get_stream_manager()

        if not stream_manager:
            return {
                "status": "unavailable",
                "performance": "unknown",
                "last_updated": datetime.now().isoformat(),
            }

        # Calculate performance metrics
        total_symbols = (
            len(stream_manager.subscribed_symbols)
            if hasattr(stream_manager, "subscribed_symbols")
            else 0
        )
        total_buffers = (
            sum(len(buffers) for buffers in stream_manager.buffers.values())
            if hasattr(stream_manager, "buffers")
            else 0
        )

        # Estimate memory usage (rough calculation)
        estimated_memory_mb = total_buffers * 0.001  # ~1KB per message estimate

        # Performance assessment
        if total_symbols == 0:
            performance_level = "idle"
        elif total_symbols <= 10 and estimated_memory_mb < 50:
            performance_level = "optimal"
        elif total_symbols <= 50 and estimated_memory_mb < 200:
            performance_level = "good"
        else:
            performance_level = "heavy"

        return {
            "status": (
                "active"
                if hasattr(stream_manager, "is_streaming")
                and stream_manager.is_streaming
                else "inactive"
            ),
            "performance_level": performance_level,
            "total_symbols_streaming": total_symbols,
            "total_data_types": total_buffers,
            "estimated_memory_usage_mb": round(estimated_memory_mb, 2),
            "recommended_action": {
                "idle": "Ready to start streaming",
                "optimal": "Performance is excellent",
                "good": "Performance is good",
                "heavy": "Consider reducing symbols or clearing buffers",
            }.get(performance_level, "Monitor performance"),
            "last_updated": datetime.now().isoformat(),
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error",
            "performance_level": "unknown",
            "last_updated": datetime.now().isoformat(),
        }
