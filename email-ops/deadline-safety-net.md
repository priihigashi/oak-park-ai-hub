# Deadline safety net runbook

This is a read-only shadow watcher for OPC Gmail and one verified Outlook/Hotmail connected account.
It does not send, forward, label, archive, delete, reply, or create calendar events.

## Private configuration

The public repository intentionally does not contain private mailbox identities or school/medical sender lists.
Configure these GitHub repository secrets:

- `DEADLINE_OUTLOOK_ALIAS`: the verified active Composio Outlook account alias.
- `DEADLINE_ALLOWED_SENDERS_JSON`: a JSON list of exact addresses or domains.

The workflow reuses existing `SHEETS_TOKEN`, `COMPOSIO_KEY`, and `NTFY_TOPIC` secrets.
Keep repository variable `DEADLINE_NOTIFY_ENABLED=false` throughout shadow observation.

## Rollout

1. Run the test workflow and confirm the Step Up regression fixture passes.
2. Run `deadline_watch.yml` manually with `notify=false`.
3. Inspect the artifact. Both mailboxes must appear in `mailboxes_ok`.
4. Observe scheduled shadow runs before enabling notifications.
5. Only then run manually with `notify=true`; alerts contain mailbox, subject, and due date only.

Any mailbox read failure makes the workflow red. A missing output artifact is a health failure, not “no deadlines.”

## Kill switch

Disable the `deadline_watch.yml` workflow. No source mailbox state needs rollback because the watcher never mutates mail.
