import typing as t
from datetime import datetime, timedelta

import discord


async def get_latest_audit(
    guild: discord.Guild, actions: t.Iterable[discord.enums.AuditLogAction],
    target: t.Any = None, max_time: int = 5,
) -> t.Optional[discord.AuditLogEntry]:
    logs = []

    for action in actions:
        audit_logs = await guild.audit_logs(limit=1, action=action).flatten()
        logs.extend(audit_logs)

    if not logs or len(logs) == 0:
        return

    last_log = max(logs, key=lambda log_: log_.created_at)

    time_delta = datetime.utcnow() - timedelta(seconds=max_time)
    if last_log.created_at < time_delta:
        return

    if target is not None and last_log.target != target:
        return
